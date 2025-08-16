import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export function activate(context: vscode.ExtensionContext) {
    const root = vscode.workspace.rootPath || '';
    const provider = new PlanPreviewProvider(root);
    vscode.window.registerTreeDataProvider('planPreviewView', provider);
}

class PlanPreviewProvider implements vscode.TreeDataProvider<InstructionItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<InstructionItem | undefined | void> = new vscode.EventEmitter();
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
            try {
                const fullPath = path.join(instrDir, f);
                const raw = JSON.parse(fs.readFileSync(fullPath, 'utf8'));
                const label = raw.id || f;
                const badges: string[] = [];
                if (raw.priority) { badges.push(`P:${raw.priority}`); }
                if (raw.risk) { badges.push(`R:${raw.risk}`); }
                return new InstructionItem(
                    `${label} ${badges.join(' ')}`.trim(),
                    vscode.TreeItemCollapsibleState.None,
                    fullPath
                );
            } catch {
                return new InstructionItem(`${f} (invalid JSON)`, vscode.TreeItemCollapsibleState.None);
            }
        }));
    }
}

class InstructionItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly filePath?: string
    ) {
        super(label, collapsibleState);
        if (filePath) {
            this.command = {
                command: 'vscode.open',
                title: 'Open Instruction',
                arguments: [vscode.Uri.file(filePath)]
            };
        }
    }
}