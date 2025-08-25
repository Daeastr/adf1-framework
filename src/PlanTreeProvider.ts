// src/planTreeProvider.ts
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

// Define a type for the elements in our tree
type PlanStep = {
  id: string;
  action: string;
  artifactPath?: string; // The path to the log file from the orchestrator's output
};

export class PlanTreeProvider implements vscode.TreeDataProvider<PlanStep> {
  private _onDidChangeTreeData: vscode.EventEmitter<PlanStep | undefined | null | void> = new vscode.EventEmitter<PlanStep | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<PlanStep | undefined | null | void> = this._onDidChangeTreeData.event;

  constructor(private workspaceRoot: string | undefined) {}

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  // This method is called for each item in the tree to get its visual representation (TreeItem).
  getTreeItem(element: PlanStep): vscode.TreeItem {
    const treeItem = new vscode.TreeItem(element.id, vscode.TreeItemCollapsibleState.None);
    
    // --- PATCH APPLIED HERE ---
    // If the step has an artifactPath, we make it clickable by attaching the
    // 'aadf.openArtifact' command to it.
    if (element.artifactPath) {
      treeItem.command = {
        command: 'aadf.openArtifact',
        title: 'Open Artifact Log',
        arguments: [element.artifactPath] // Pass the path as an argument to the command
      };
      // Add a tooltip to let the user know it's clickable
      treeItem.tooltip = `Click to open log: ${element.artifactPath}`;
      treeItem.iconPath = new vscode.ThemeIcon('file-text'); // Use a file icon
    } else {
      treeItem.tooltip = `No artifact found for this step.`;
      treeItem.iconPath = new vscode.ThemeIcon('circle-outline');
    }
    // --- END PATCH ---

    treeItem.description = element.action; // Show the action name next to the ID
    return treeItem;
  }

  // This method is called to get the children of a node, or the root nodes if no element is provided.
  getChildren(element?: PlanStep): Thenable<PlanStep[]> {
    if (!this.workspaceRoot) {
      vscode.window.showInformationMessage('No plan in empty workspace');
      return Promise.resolve([]);
    }

    // If we are at the root, we load and parse our instruction plan.
    if (!element) {
      // This is a placeholder path. You would make this dynamic in a real extension.
      const planPath = path.join(this.workspaceRoot, 'instructions', 'translation-run-demo.json');
      
      if (fs.existsSync(planPath)) {
        const planJson = JSON.parse(fs.readFileSync(planPath, 'utf-8'));
        // In a real run, you would merge the artifact paths from the orchestrator's output here.
        // For this demo, we'll manually add them.
        return Promise.resolve(planJson.steps.map((step: any, index: number) => ({
          ...step,
          // Manually adding the artifact path to make the items clickable in the demo
          artifactPath: `orchestrator_artifacts/${step.id}_step${index}.log`
        })));
      } else {
        vscode.window.showInformationMessage('Could not find instruction plan file.');
        return Promise.resolve([]);
      }
    }

    // Our steps have no children, so we return an empty array.
    return Promise.resolve([]);
  }
}