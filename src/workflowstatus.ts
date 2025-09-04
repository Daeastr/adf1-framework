import * as vscode from 'vscode';
import { execSync } from 'child_process';
import * as path from 'path';

export class WorkflowStatusProvider implements vscode.TreeDataProvider<vscode.TreeItem> {
  private _onDidChangeTreeData: vscode.EventEmitter<void> = new vscode.EventEmitter<void>();
  readonly onDidChangeTreeData: vscode.Event<void> = this._onDidChangeTreeData.event;

  refresh(): void { this._onDidChangeTreeData.fire(); }

  getTreeItem(element: vscode.TreeItem): vscode.TreeItem {
    return element;
  }

  getChildren(): Thenable<vscode.TreeItem[]> {
    return Promise.resolve(this.buildStatusItems());
  }

  private buildStatusItems(): vscode.TreeItem[] {
    const items: vscode.TreeItem[] = [];
    try {
      // Venv Python version
      const pyVer = execSync('.\\.venv\\Scripts\\python --version').toString().trim();
      items.push(new vscode.TreeItem(`🐍 Python: ${pyVer}`));

      // Diff requirements.txt vs .lock
      const diff = execSync('git diff --name-only requirements.txt requirements.lock').toString().trim();
      items.push(new vscode.TreeItem(diff ? '⚠️ Requirements differ' : '✅ Requirements in sync'));

      // Last venv rebuild tag
      const lastTag = execSync('git describe --tags --match "venv-rebuild-*" --abbrev=0').toString().trim();
      items.push(new vscode.TreeItem(`🏷 Last rebuild: ${lastTag}`));
    } catch (err) {
      items.push(new vscode.TreeItem(`⚠️ Error fetching status: ${err}`));
    }
    return items;
  }
}
