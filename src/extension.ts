import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface PlanStep {
    id: string;
    action: string;
    status?: string;
    agent?: string;
    capabilities?: string[];
    duration_sec?: number;
    log_file?: string;
    error?: string;
}

interface ExecutionSummary {
    summary: {
        total_steps: number;
        successful: number;
        failed: number;
        total_duration_sec: number;
    };
    steps: PlanStep[];
}

class PlanPreviewProvider implements vscode.TreeDataProvider<PlanStep> {
    private _onDidChangeTreeData: vscode.EventEmitter<PlanStep | undefined | null | void> = new vscode.EventEmitter<PlanStep | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<PlanStep | undefined | null | void> = this._onDidChangeTreeData.event;

    private planData: PlanStep[] = [];

    constructor() {
        this.loadPlanData();
    }

    refresh(): void {
        this.loadPlanData();
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: PlanStep): vscode.TreeItem {
        const item = new vscode.TreeItem(
            `${element.id} - ${element.action}`,
            vscode.TreeItemCollapsibleState.None
        );
        
        // Status-based icons and colors
        if (element.status === 'completed') {
            item.iconPath = new vscode.ThemeIcon('check', new vscode.ThemeColor('charts.green'));
            item.description = `✅ ${element.duration_sec?.toFixed(2)}s`;
        } else if (element.status === 'failed') {
            item.iconPath = new vscode.ThemeIcon('error', new vscode.ThemeColor('charts.red'));
            item.description = `❌ ${element.error || 'Failed'}`;
        } else {
            item.iconPath = new vscode.ThemeIcon('clock', new vscode.ThemeColor('charts.yellow'));
            item.description = `⏳ ${element.agent || 'Pending'}`;
        }

        // Set context value for menu contributions
        item.contextValue = 'planStep';

        // Add tooltip with more details
        item.tooltip = new vscode.MarkdownString();
        item.tooltip.appendMarkdown(`**${element.id}**\n\n`);
        item.tooltip.appendMarkdown(`Action: ${element.action}\n\n`);
        item.tooltip.appendMarkdown(`Agent: ${element.agent || 'Not assigned'}\n\n`);
        if (element.capabilities && element.capabilities.length > 0) {
            item.tooltip.appendMarkdown(`Capabilities: ${element.capabilities.join(', ')}\n\n`);
        }
        if (element.status) {
            item.tooltip.appendMarkdown(`Status: ${element.status}\n\n`);
        }
        if (element.duration_sec) {
            item.tooltip.appendMarkdown(`Duration: ${element.duration_sec.toFixed(2)}s\n\n`);
        }
        if (element.log_file) {
            item.tooltip.appendMarkdown(`Log: ${element.log_file}\n\n`);
        }

        return item;
    }

    getChildren(element?: PlanStep): Thenable<PlanStep[]> {
        if (!element) {
            return Promise.resolve(this.planData);
        }
        return Promise.resolve([]);
    }

    private async loadPlanData(): Promise<void> {
        try {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                this.planData = [];
                return;
            }

            const { stdout } = await execAsync('python -m core.orchestrator --parse-only', {
                cwd: workspaceFolder.uri.fsPath
            });

            const parsed = JSON.parse(stdout.trim());
            this.planData = Array.isArray(parsed) ? parsed : [];
            
        } catch (error) {
            console.error('Failed to load plan data:', error);
            this.planData = [];
            vscode.window.showErrorMessage('Failed to load AADF plan data');
        }
    }

    public async updateWithExecutionData(executionSummary: ExecutionSummary): Promise<void> {
        this.planData = executionSummary.steps;
        this._onDidChangeTreeData.fire();
    }
}

export function activate(context: vscode.ExtensionContext) {
    console.log('AADF Plan Preview extension is now active!');

    // Create the tree data provider
    const provider = new PlanPreviewProvider();
    
    // Register the tree view
    const treeView = vscode.window.createTreeView('aadfPlanTree', {
        treeDataProvider: provider,
        showCollapseAll: true
    });

    // Register commands
    const refreshCommand = vscode.commands.registerCommand('aadf.openPlanPreview', () => {
        provider.refresh();
        vscode.window.showInformationMessage('AADF Plan Preview refreshed!');
    });

    const showPreviewCommand = vscode.commands.registerCommand('aadf1.showPlanPreview', () => {
        vscode.commands.executeCommand('aadfPlanTree.focus');
    });

    const selectiveRerunCommand = vscode.commands.registerCommand('aadf1.selectiveRerun', async () => {
        try {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('No workspace folder found');
                return;
            }

            vscode.window.showInformationMessage('Running selective tests...');
            
            const { stdout } = await execAsync('python -m core.orchestrator --output-execution-json', {
                cwd: workspaceFolder.uri.fsPath
            });

            // Parse execution results and update tree view
            const lines = stdout.split('\n');
            const jsonLine = lines.find(line => line.includes('"summary"'));
            
            if (jsonLine) {
                const executionSummary: ExecutionSummary = JSON.parse(jsonLine);
                await provider.updateWithExecutionData(executionSummary);
                
                const { summary } = executionSummary;
                vscode.window.showInformationMessage(
                    `Execution complete: ${summary.successful}/${summary.total_steps} successful, ${summary.total_duration_sec.toFixed(2)}s total`
                );
            }
            
        } catch (error) {
            console.error('Selective rerun failed:', error);
            vscode.window.showErrorMessage(`Selective rerun failed: ${error}`);
        }
    });

    // Register the log alert command - NEW
    const logAlertCommand = vscode.commands.registerCommand('aadf.showLogAlert', (alertData: string) => {
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
    });

    // Register the tail colored logs command for context menu
    const tailLogsCommand = vscode.commands.registerCommand('aadf.tailColoredLogs', async (step: PlanStep) => {
        try {
            if (!step.log_file) {
                vscode.window.showWarningMessage(`No log file available for step ${step.id}`);
                return;
            }

            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('No workspace folder found');
                return;
            }

            // Create a new terminal for basic log tailing
            const terminal = vscode.window.createTerminal({
                name: `AADF Logs: ${step.id}`,
                cwd: workspaceFolder.uri.fsPath
            });

            // Run the basic colored log tailer
            terminal.sendText(`python -m core.orchestrator --follow-log "${step.log_file}" --levels ERROR WARN INFO`);
            terminal.show();

        } catch (error) {
            console.error('Failed to tail logs:', error);
            vscode.window.showErrorMessage(`Failed to tail logs: ${error}`);
        }
    });

    // Register the tail colored logs with alerts command for context menu
    const tailLogsWithAlertCommand = vscode.commands.registerCommand('aadf.tailColoredLogsWithAlert', async (step: PlanStep) => {
        try {
            if (!step.log_file) {
                vscode.window.showWarningMessage(`No log file available for step ${step.id}`);
                return;
            }

            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('No workspace folder found');
                return;
            }

            // Create a new terminal for log tailing with alerts
            const terminal = vscode.window.createTerminal({
                name: `AADF Logs + Alerts: ${step.id}`,
                cwd: workspaceFolder.uri.fsPath
            });

            // Run the enhanced log tailer with the new consolidated flag
            terminal.sendText(`python -m core.orchestrator --follow-log-colored-alert "${step.log_file}" --levels ERROR WARN INFO`);
            terminal.show();

            // Show confirmation that alerts are enabled
            vscode.window.showInformationMessage(`🚨 Alert monitoring enabled for ${step.id} logs`);

        } catch (error) {
            console.error('Failed to tail logs with alerts:', error);
            vscode.window.showErrorMessage(`Failed to tail logs with alerts: ${error}`);
        }
    });

    // Add all commands to subscriptions
    context.subscriptions.push(
        refreshCommand,
        showPreviewCommand,
        selectiveRerunCommand,
        logAlertCommand,
        tailLogsCommand,
        tailLogsWithAlertCommand,  // NEW
        treeView
    );

    // Auto-refresh on workspace changes
    const watcher = vscode.workspace.createFileSystemWatcher('**/instructions/*.json');
    watcher.onDidChange(() => provider.refresh());
    watcher.onDidCreate(() => provider.refresh());
    watcher.onDidDelete(() => provider.refresh());
    context.subscriptions.push(watcher);
}

export function deactivate() {
    console.log('AADF Plan Preview extension deactivated');
}
