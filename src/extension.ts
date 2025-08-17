import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';

export function activate(context: vscode.ExtensionContext) {
    const runCmd = vscode.commands.registerCommand('aadf.runDocAutomation', async () => {
        const fileUri = await vscode.window.showOpenDialog({
            canSelectMany: false,
            openLabel: 'Select Instruction File',
            filters: { 'JSON/YAML': ['json', 'yml', 'yaml'] }
        });
        if (!fileUri || fileUri.length === 0) { return; }

        const filePath = fileUri[0].fsPath;
        const cwd = vscode.workspace.workspaceFolders?.[0].uri.fsPath ?? path.dirname(filePath);

        const term = vscode.window.createTerminal({ name: 'AADF Orchestrator', cwd });
        term.show();
        term.sendText(`.\\venv\\Scripts\\activate && python -m core.orchestrator "${filePath}"`);
    });

    context.subscriptions.push(runCmd);
}
