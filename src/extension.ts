// src/extension.ts
import * as vscode from "vscode";
import * as path from "path";
import { spawn } from "child_process";

// Adjust to point to your orchestrator entry point
const ORCHESTRATOR_MODULE = path.join(
    vscode.workspace.rootPath || "",
    "core",
    "orchestrator.py"
);

// Helper to spawn orchestrator in a VS Code terminal
function runOrchestrator(args: string[]) {
    const term = vscode.window.createTerminal({
        name: "AADF Orchestrator",
        hideFromUser: false,
    });
    const quotedArgs = args.map(a => a.includes(" ") ? `"${a}"` : a);
    term.sendText(`python "${ORCHESTRATOR_MODULE}" ${quotedArgs.join(" ")}`);
    term.show();
}

// Dummy example: resolve log path(s) from a view item
function getLogPathsForStep(item: any): string[] {
    // Your own logic: item could have a `logPath` or `logPaths` property
    if (Array.isArray(item?.logPaths)) {
        return item.logPaths;
    }
    if (item?.logPath) {
        return [item.logPath];
    }
    if (item?.log_file) {
        return [item.log_file];
    }
    vscode.window.showWarningMessage("No log paths found for step");
    return [];
}

export function activate(context: vscode.ExtensionContext) {
    // Register the log alert command to receive alerts from Python
    context.subscriptions.push(
        vscode.commands.registerCommand('aadf.showLogAlert', (alertData: string) => {
            try {
                // Parse the alert data from the command line format: level?step?message
                const parts = alertData.split('?');
                if (parts.length >= 3) {
                    const [level, step, ...messageParts] = parts;
                    const message = messageParts.join('?'); // Rejoin in case message contains '?'
                    
                    if (level === 'error') {
                        vscode.window.showErrorMessage(`❌ [${step}] ${message}`);
                    } else if (level === 'warn') {
                        vscode.window.showWarningMessage(`⚠️ [${step}] ${message}`);
                    }
                } else {
                    console.error('Invalid alert data format:', alertData);
                }
            } catch (error) {
                console.error('Failed to process log alert:', error);
            }
        })
    );

    // Open AADF Step Log
    context.subscriptions.push(
        vscode.commands.registerCommand("aadfLogs.openLog", (item) => {
            if (!item?.resourceUri) {
                vscode.window.showWarningMessage("No log resource provided");
                return;
            }
            vscode.window.showTextDocument(item.resourceUri);
        })
    );

    // Open Plan Preview
    context.subscriptions.push(
        vscode.commands.registerCommand("aadf.openPlanPreview", () => {
            // Your UI logic to show the plan preview webview/panel
            vscode.commands.executeCommand("workbench.view.explorer");
        })
    );

    // Selective Rerun Mapped Tests
    context.subscriptions.push(
        vscode.commands.registerCommand("aadf1.selectiveRerun", (item) => {
            // Adapt this to pass your mapped test args
            runOrchestrator(["--rerun-tests", item?.stepId || ""]);
        })
    );

    // Show AADF Plan Preview
    context.subscriptions.push(
        vscode.commands.registerCommand("aadf1.showPlanPreview", () => {
            vscode.window.showInformationMessage("Showing AADF Plan Preview");
            // Implementation for showing preview panel here
        })
    );

    // Tail Colored Logs
    context.subscriptions.push(
        vscode.commands.registerCommand("aadf.tailColoredLogs", (item) => {
            const paths = getLogPathsForStep(item);
            if (paths.length) {
                runOrchestrator(["--follow-log-colored", ...paths]);
            }
        })
    );

    // Tail Colored Logs with Alerts
    context.subscriptions.push(
        vscode.commands.registerCommand("aadf.tailColoredLogsWithAlert", (item) => {
            const paths = getLogPathsForStep(item);
            if (paths.length) {
                runOrchestrator(["--follow-log-colored-alert", ...paths]);
            }
        })
    );

    // Tail Step Logs with Alert (single‑step helper)
    context.subscriptions.push(
        vscode.commands.registerCommand("aadf.tailStepLogsWithAlert", (item) => {
            const paths = getLogPathsForStep(item);
            if (paths.length === 1) {
                runOrchestrator(["--follow-log-colored-alert", paths[0]]);
            } else if (paths.length > 1) {
                runOrchestrator(["--follow-log-colored-alert", ...paths]);
            }
        })
    );
}

export function deactivate() {
    // Clean‑up if necessary
}```

