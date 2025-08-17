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

    // Create status bar i
