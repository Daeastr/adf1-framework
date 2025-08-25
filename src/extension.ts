// src/extension.ts
import * as vscode from 'vscode';
// ... other imports
import { PlanTreeProvider } from './planTreeProvider'; // Import the new provider

export function activate(context: vscode.ExtensionContext) {
  const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

  // --- Register the Tree View Provider ---
  const planTreeProvider = new PlanTreeProvider(workspaceRoot);
  vscode.window.createTreeView('aadfPlanView', { treeDataProvider: planTreeProvider });
  // Add a command to refresh the tree view
  context.subscriptions.push(
    vscode.commands.registerCommand('aadf.refreshPlanView', () => planTreeProvider.refresh())
  );
  
  // --- All other existing command registrations ---
  // (aadf.openArtifact, aadf.runAppBuild, etc.)
  context.subscriptions.push(
    vscode.commands.registerCommand('aadf.openArtifact', (artifactPath) => {
      // ... implementation
    })
  );
  // ... rest of your activate function
}

// ... deactivate function