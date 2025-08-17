import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export function activate(context: vscode.ExtensionContext) {
    const root = vscode.workspace.rootPath || '';
    const artifactsPath = path.join(root, 'orchestrator_artifacts');
    const statePath = path.join(root, 'orchestrator_state.json');
    const provider = new LogsProvider(artifactsPath, statePath);
    vscode.window.registerTreeDataProvider('aadfStepLogs', provider);
    context.subscriptions.push(
        vscode.commands.registerCommand('aadfLogs.openLog', (filepath: string) => {
            vscode.workspace.openTextDocument(filepath).then(doc => {
                vscode.window.showTextDocument(doc, { preview: false });
            });
        })
    );
    context.subscriptions.push(
        vscode.commands.registerCommand('aadf.openPlanPreview', async () => {
            // Reveal the view in Explorer
            await vscode.commands.executeCommand('workbench.view.explorer');
            // Try to reveal the view container by its id
            try {
                await vscode.commands.executeCommand('workbench.views.focus', 'aadfStepLogs');
            } catch {
                // Some VS Code versions may not support workbench.views.focus; ignore failures
            }
            vscode.window.showInformationMessage('AADF: Plan Preview opened in Explorer (look for Plan Preview).');
        })
    );
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
export function activate(context: vscode.ExtensionContext) {
    const disposable = vscode.commands.registerCommand('aadf.openPlanPreview', () => {
        showPlanPreview(context);
    });
    context.subscriptions.push(disposable);

    // Auto‑restore if user had the panel open last time
    const wasOpen = context.globalState.get('aadfPreviewOpen');
    if (wasOpen) {
        showPlanPreview(context);
    }
}

function showPlanPreview(context: vscode.ExtensionContext) {
    const panel = vscode.window.createWebviewPanel(
        'aadfPlanPreview',
        'AADF Plan Preview',
        vscode.ViewColumn.Two,
        { enableScripts: true, retainContextWhenHidden: true }
    );
    panel.webview.html = renderPlanHtml(); // your function to run parse_only and build HTML

    panel.onDidDispose(() => {
        context.globalState.update('aadfPreviewOpen', false);
    });
    context.globalState.update('aadfPreviewOpen', true);
}
