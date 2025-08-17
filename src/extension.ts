import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import * as cp from 'child_process';

export function activate(context: vscode.ExtensionContext) {
    const root = vscode.workspace.rootPath || '';
    const cwd = vscode.workspace.workspaceFolders?.[0].uri.fsPath ?? "";
    
    // Initialize providers
    const artifactsPath = path.join(root, 'orchestrator_artifacts');
    const statePath = path.join(root, 'orchestrator_state.json');
    const logsProvider = new LogsProvider(artifactsPath, statePath);
    const planProvider = new PlanProvider(cwd);
    
    // Register tree data providers
    vscode.window.registerTreeDataProvider('aadfStepLogs', logsProvider);
    vscode.window.registerTreeDataProvider('aadfPlanTree', planProvider);
    
    // Register log commands
    context.subscriptions.push(
        vscode.commands.registerCommand('aadfLogs.openLog', (filepath: string) => {
            vscode.workspace.openTextDocument(filepath).then(doc => {
                vscode.window.showTextDocument(doc, { preview: false });
            });
        }),
        vscode.commands.registerCommand('aadfLogs.refresh', () => {
            logsProvider.refresh();
        })
    );

    // Register plan preview commands
    context.subscriptions.push(
        vscode.commands.registerCommand('aadf.openPlanPreview', async () => {
            // Reveal the view in Explorer
            await vscode.commands.executeCommand('workbench.view.explorer');
            try {
                await vscode.commands.executeCommand('workbench.views.focus', 'aadfStepLogs');
            } catch {
                // Some VS Code versions may not support workbench.views.focus; ignore failures
            }
            vscode.window.showInformationMessage('AADF: Plan Preview opened in Explorer (look for Plan Preview).');
        }),
        vscode.commands.registerCommand('aadf.showPlanPreview', () => {
            planProvider.refresh();
            showPlanPreview(context);
        })
    );

    // Register doc automation command
    context.subscriptions.push(
        vscode.commands.registerCommand('aadf.runDocAutomation', async () => {
            const fileUri = await vscode.window.showOpenDialog({
                canSelectMany: false,
                openLabel: 'Select Instruction File',
                filters: { 'JSON/YAML': ['json', 'yml', 'yaml'] }
            });
            if (!fileUri || fileUri.length === 0) { return; }

            const filePath = fileUri[0].fsPath;
            const workspaceCwd = vscode.workspace.workspaceFolders?.[0].uri.fsPath ?? path.dirname(filePath);

            const term = vscode.window.createTerminal({ name: 'AADF Orchestrator', cwd: workspaceCwd });
            term.show();
            term.sendText(`.\\venv\\Scripts\\activate && python -m core.orchestrator "${filePath}"`);
        })
    );

    // Register step log viewing command
    context.subscriptions.push(
        vscode.commands.registerCommand('aadf.viewStepLog', async (step: any) => {
            if (!step.log_file) {
                return vscode.window.showWarningMessage(`No log found for step ${step.id}`);
            }
            const logUri = vscode.Uri.file(step.log_file);
            const doc = await vscode.workspace.openTextDocument(logUri);
            await vscode.window.showTextDocument(doc, { preview: false });
        }),
        
        // Keep the run step command for when logs don't exist
        vscode.commands.registerCommand('aadf.runStep', async (step: any) => {
            const stepId = step.id;
            const term = vscode.window.createTerminal({ 
                name: `Run ${stepId}`, 
                cwd: cwd 
            });
            term.show();
            // Run orchestrator with a --step-id flag to target only this step
            term.sendText(`.\\venv\\Scripts\\activate && python -m core.orchestrator --step-id ${stepId}`);
        })
    );

    // Create status bar item for plan preview
    const previewButton = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Left,
        100
    );
    previewButton.command = 'aadf.showPlanPreview';
    previewButton.text = '$(preview) Plan Preview';
    previewButton.tooltip = 'Open AADF Plan Preview Panel';
    previewButton.show();

    context.subscriptions.push(previewButton);

    // Auto-restore if user had the panel open last time
    const wasOpen = context.globalState.get('aadfPreviewOpen');
    if (wasOpen) {
        showPlanPreview(context);
    }
}

// LogItem class for log files
class LogItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly filepath: string,
        public readonly passed?: boolean
    ) {
        super(label);
        this.command = {
            command: 'aadfLogs.openLog',
            title: 'Open Log',
            arguments: [this.filepath]
        };
        
        // Set icon based on pass/fail state
        if (passed === true) {
            this.iconPath = new vscode.ThemeIcon('check', new vscode.ThemeColor('testing.iconPassed'));
        } else if (passed === false) {
            this.iconPath = new vscode.ThemeIcon('error', new vscode.ThemeColor('testing.iconFailed'));
        } else {
            this.iconPath = new vscode.ThemeIcon('question');
        }
        
        this.tooltip = `Log file: ${path.basename(filepath)}`;
        this.description = this.getLogDescription(filepath);
    }
    
    private getLogDescription(filepath: string): string {
        try {
            const stats = fs.statSync(filepath);
            const date = stats.mtime.toLocaleString();
            const size = (stats.size / 1024).toFixed(1) + 'KB';
            return `${size} • ${date}`;
        } catch {
            return '';
        }
    }
}

// LogsProvider class
class LogsProvider implements vscode.TreeDataProvider<LogItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<LogItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;
    private stepResults: Record<string, boolean> = {};

    constructor(private artifactsDir: string, private stateFile: string) {
        this.loadState();
    }

    private loadState() {
        try {
            const raw = fs.readFileSync(this.stateFile, 'utf8');
            const state = JSON.parse(raw);
            // Assuming state.steps[] with { id, status }
            for (const step of state.steps || []) {
                this.stepResults[`${step.id}_step${step.index}`] = (step.status === 'passed');
            }
        } catch (err) {
            console.warn('No state file or invalid format', err);
        }
    }

    refresh(): void {
        this.loadState(); // Reload state when refreshing
        this._onDidChangeTreeData.fire(undefined);
    }

    getChildren(): Thenable<LogItem[]> {
        if (!fs.existsSync(this.artifactsDir)) {
            return Promise.resolve([]);
        }
        const files = fs.readdirSync(this.artifactsDir).filter(f => f.endsWith('.log'));
        return Promise.resolve(
            files.map(f => {
                const key = f.replace('.log', '');
                return new LogItem(f, path.join(this.artifactsDir, f), this.stepResults[key]);
            })
        );
    }

    getTreeItem(element: LogItem): vscode.TreeItem {
        return element;
    }
}

// PlanProvider class for activity bar tree view
class PlanProvider implements vscode.TreeDataProvider<vscode.TreeItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;
    
    constructor(private cwd: string) {}

    refresh(): void { 
        this._onDidChangeTreeData.fire(); 
    }

    getTreeItem(element: vscode.TreeItem): vscode.TreeItem { 
        return element; 
    }

    getChildren(): vscode.ProviderResult<vscode.TreeItem[]> {
        const parseScript = `.\\venv\\Scripts\\activate && python -m core.orchestrator --parse-only`;
        try {
            const output = cp.execSync(parseScript, { 
                cwd: this.cwd, 
                shell: "powershell.exe",
                timeout: 10000 // 10 second timeout
            }).toString();
            
            const plan = JSON.parse(output);
            return plan.map((step: any) => {
                const item = new vscode.TreeItem(
                    `${step.id} — ${step.action}`,
                    vscode.TreeItemCollapsibleState.None
                );
                item.description = `P:${step.priority || 'N/A'} R:${step.risk || 'N/A'}`;
                item.tooltip = `Action: ${step.action}\nPriority: ${step.priority || 'N/A'}\nRisk: ${step.risk || 'N/A'}\n\nClick to view step log`;
                
                // Add command to view the step log when clicked
                item.command = {
                    command: 'aadf.viewStepLog',
                    title: 'View Step Log',
                    arguments: [step]
                };
                
                // Add context value for right-click menus
                item.contextValue = 'aadfStep';
                
                return item;
            });
        } catch (err) {
            console.error('Failed to parse plan:', err);
            vscode.window.showErrorMessage(`Failed to load plan preview: ${err}`);
            return [new vscode.TreeItem('Error loading plan', vscode.TreeItemCollapsibleState.None)];
        }
    }
}

// WebView panel for plan preview
function showPlanPreview(context: vscode.ExtensionContext) {
    const panel = vscode.window.createWebviewPanel(
        'aadfPlanPreview',
        'AADF Plan Preview',
        vscode.ViewColumn.Two,
        { enableScripts: true, retainContextWhenHidden: true }
    );
    
    panel.webview.html = renderPlanHtml();

    panel.onDidDispose(() => {
        context.globalState.update('aadfPreviewOpen', false);
    });
    context.globalState.update('aadfPreviewOpen', true);
}

function renderPlanHtml(): string {
    const cwd = vscode.workspace.workspaceFolders?.[0].uri.fsPath ?? "";
    const parseScript = `.\\venv\\Scripts\\activate && python -m core.orchestrator --parse-only`;
    
    try {
        const output = cp.execSync(parseScript, { 
            cwd: cwd, 
            shell: "powershell.exe",
            timeout: 10000
        }).toString();
        
        const plan = JSON.parse(output);
        
        const planItems = plan.map((step: any) => `
            <div class="plan-item">
                <h3>${step.id} — ${step.action}</h3>
                <div class="plan-meta">
                    <span class="priority">Priority: ${step.priority || 'N/A'}</span>
                    <span class="risk">Risk: ${step.risk || 'N/A'}</span>
                </div>
                <div class="plan-description">
                    ${step.description || 'No description provided'}
                </div>
            </div>
        `).join('');
        
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <title>AADF Plan Preview</title>
                <style>
                    body { 
                        font-family: var(--vscode-font-family);
                        color: var(--vscode-foreground);
                        background: var(--vscode-editor-background);
                        padding: 20px; 
                        line-height: 1.6;
                    }
                    h1 { 
                        color: var(--vscode-titleBar-activeForeground);
                        border-bottom: 2px solid var(--vscode-panel-border);
                        padding-bottom: 10px;
                    }
                    .plan-item { 
                        margin: 15px 0; 
                        padding: 15px; 
                        border-left: 4px solid var(--vscode-activityBarBadge-background);
                        background: var(--vscode-editor-inactiveSelectionBackground);
                        border-radius: 4px;
                    }
                    .plan-item h3 {
                        margin: 0 0 10px 0;
                        color: var(--vscode-textLink-foreground);
                    }
                    .plan-meta {
                        margin: 8px 0;
                        font-size: 0.9em;
                    }
                    .plan-meta span {
                        margin-right: 15px;
                        padding: 2px 8px;
                        background: var(--vscode-badge-background);
                        color: var(--vscode-badge-foreground);
                        border-radius: 3px;
                    }
                    .plan-description {
                        margin-top: 10px;
                        font-style: italic;
                        color: var(--vscode-descriptionForeground);
                    }
                </style>
            </head>
            <body>
                <h1>🎯 AADF Plan Preview</h1>
                <p>Total steps: ${plan.length}</p>
                ${planItems}
            </body>
            </html>
        `;
    } catch (err) {
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <title>AADF Plan Preview - Error</title>
                <style>
                    body { 
                        font-family: var(--vscode-font-family);
                        color: var(--vscode-errorForeground);
                        background: var(--vscode-editor-background);
                        padding: 20px; 
                    }
                    .error { 
                        padding: 15px; 
                        background: var(--vscode-inputValidation-errorBackground);
                        border: 1px solid var(--vscode-inputValidation-errorBorder);
                        border-radius: 4px;
                    }
                </style>
            </head>
            <body>
                <h1>❌ Plan Preview Error</h1>
                <div class="error">
                    <p>Failed to load plan preview:</p>
                    <pre>${err}</pre>
                </div>
            </body>
            </html>
        `;
    }
}