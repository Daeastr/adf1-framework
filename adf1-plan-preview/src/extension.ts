import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

// This method is called when your extension is activated
export function activate(context: vscode.ExtensionContext) {
    // Use the console to output diagnostic information (console.log) and errors (console.error)
    console.log('Congratulations, your extension "adf1-plan-preview" is now active!');

    // Register the Plan Preview provider
    const provider = new PlanPreviewProvider(vscode.workspace.rootPath || '');
    vscode.window.registerTreeDataProvider('planPreviewView', provider);

    // The existing command registration
    const disposable = vscode.commands.registerCommand('adf1-plan-preview.helloWorld', () => {
        // The code you place here will be executed every time your command is executed
        // Display a message box to the user
        vscode.window.showInformationMessage('Hello World from adf1-plan-preview!');
    });

    context.subscriptions.push(disposable);
}

class PlanPreviewProvider implements vscode.TreeDataProvider<InstructionItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<InstructionItem | undefined | void> = new vscode.EventEmitter<InstructionItem | undefined | void>();
    readonly onDidChangeTreeData: vscode.Event<InstructionItem | undefined | void> = this._onDidChangeTreeData.event;
    
    constructor(private workspaceRoot: string) {}

    getTreeItem(element: InstructionItem): vscode.TreeItem {
        return element;
    }

    getChildren(): Thenable<InstructionItem[]> {
        if (!this.workspaceRoot) {
            vscode.window.showInformationMessage('No folder open');
            return Promise.resolve([]);
        }

        const instrDir = path.join(this.workspaceRoot, 'instructions');
        if (!fs.existsSync(instrDir)) {
            return Promise.resolve([]);
        }

        const files = fs.readdirSync(instrDir)
            .filter(f => f.endsWith('.json') && f !== 'schema.json');

        return Promise.resolve(files.map(f => {
            const fullPath = path.join(instrDir, f);
            const raw = JSON.parse(fs.readFileSync(fullPath, 'utf8'));
            const label = raw.id || f;
            const badges: string[] = [];
            if (raw.priority) { badges.push(`P:${raw.priority}`); }
            if (raw.risk) { badges.push(`R:${raw.risk}`); }
            return new InstructionItem(
                `${label} ${badges.join(' ')}`,
                vscode.TreeItemCollapsibleState.None
            );
        }));
    }
}

class InstructionItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(label, collapsibleState);
    }
}

// This method is called when your extension is deactivated
export function deactivate() {}