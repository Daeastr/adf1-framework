import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export function activate(context: vscode.ExtensionContext) {
    const root = vscode.workspace.rootPath || '';
    const artifactsPath = path.join(root, 'orchestrator_artifacts');
    const statePath = path.join(root, 'orchestrator_state.json');
    const provider = new LogsProvider(artifactsPath, statePath);
    vscode.window.registerTreeDataProvider('aadfStepLogs', provider);
    
    // Register log opening command
    context.subscriptions.push(
        vscode.commands.registerCommand('aadfLogs.openLog', (filepath: string) => {
            vscode.workspace.openTextDocument(filepath).then(doc => {
                vscode.window.showTextDocument(doc, { preview: false });
            });
        })
    );

    // Register plan preview command
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

    // Create status bar item for plan preview
    const previewCommand = 'aadf1.showPlanPreview';
    const previewButton = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Left,
        100
    );
    previewButton.command = previewCommand;
    previewButton.text = '$(preview) Plan Preview';
    previewButton.tooltip = 'Open AADF Plan Preview Panel';
    previewButton.show();

    context.subscriptions.push(previewButton);

    // Register the webview panel command
    context.subscriptions.push(
        vscode.commands.registerCommand(previewCommand, () => {
            showPlanPreview(context);
        })
    );

    // Auto-restore if user had the panel open last time
    const wasOpen = context.globalState.get('aadfPreviewOpen');
    if (wasOpen) {
        showPlanPreview(context);
    }
}

function showPlanPreview(context: vscode.ExtensionContext) {
        const panel = vscode.window.createWebviewPanel(
                'aadfPlanPreview',
                'AADF Plan Preview',
                { viewColumn: vscode.ViewColumn.One, preserveFocus: false },
                { enableScripts: true }
        );

        panel.webview.html = getWebviewContent();

        // Persist open state so we can auto-restore
        context.globalState.update('aadfPreviewOpen', true);

        panel.onDidDispose(() => {
                context.globalState.update('aadfPreviewOpen', false);
        }, null, context.subscriptions);

    // Helper to load plan/state and post cards to the webview
    const root = vscode.workspace.rootPath || '';
    const stateFile = path.join(root, 'orchestrator_state.json');

    function buildCardsFromState(): any[] {
        try {
            const raw = fs.readFileSync(stateFile, 'utf8');
            const state = JSON.parse(raw);
            const steps = state.steps || [];
            return steps.map((s: any, idx: number) => {
                const id = s.id ?? s.name ?? `step${idx}`;
                const title = s.title ?? s.name ?? s.id ?? `Step ${idx}`;
                const description = s.description ?? s.desc ?? '';
                const priority = s.priority ?? s.priorityLevel ?? (s.critical ? 'P1' : 'P2');
                const risk = s.risk ?? (s.status === 'failed' ? 'High' : s.status === 'passed' ? 'Low' : 'Medium');
                const logPath = s.logPath ?? path.join(root, 'orchestrator_artifacts', `${id}.log`);
                return { id, title, description, priority, risk, logPath };
            });
        } catch (err) {
            // If file missing or invalid, return empty array
            return [];
        }
    }

    // post initial data
    const initialCards = buildCardsFromState();
    panel.webview.postMessage({ type: 'setCards', cards: initialCards });

    // Handle messages from the webview
    panel.webview.onDidReceiveMessage(async (msg) => {
        if (!msg || !msg.type) {
            return;
        }
        if (msg.type === 'refresh') {
            const cards = buildCardsFromState();
            panel.webview.postMessage({ type: 'setCards', cards });
            vscode.window.showInformationMessage('Plan Preview refreshed');
        } else if (msg.type === 'openLogs') {
            // Reveal Explorer for logs; user can open files from the tree view
            await vscode.commands.executeCommand('workbench.view.explorer');
            vscode.window.showInformationMessage('Explorer opened — check AADF Step Logs view');
        } else if (msg.type === 'cardClick') {
            const name = msg.name || msg.id || 'item';
            // Focus Explorer and open the related log via the existing command
            await vscode.commands.executeCommand('workbench.view.explorer');
            if (msg.logPath) {
                // Use the tree command to open log so behavior is centralized
                try {
                    await vscode.commands.executeCommand('aadfLogs.openLog', msg.logPath);
                } catch (e) {
                    // Fallback: open document directly
                    if (fs.existsSync(msg.logPath)) {
                        const doc = await vscode.workspace.openTextDocument(msg.logPath);
                        vscode.window.showTextDocument(doc, { preview: false });
                    } else {
                        vscode.window.showInformationMessage(`Log not found: ${msg.logPath}`);
                    }
                }
            } else {
                vscode.window.showInformationMessage(`Card clicked: ${name}`);
            }
        }
    }, undefined, context.subscriptions);
}

function getWebviewContent(): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AADF Plan Preview</title>
    <style>
        :root{
            --bg:#0f1720; --card:#0b1220; --muted:#9aa4b2; --accent:#60a5fa; --good:#10b981; --warn:#f59e0b; --bad:#ef4444;
            --radius:10px;
            --gap:12px;
        }
        html,body{height:100%;margin:0;font-family:Inter,Segoe UI,Roboto,Arial,sans-serif;background:linear-gradient(180deg,#071025 0%, #071827 100%);color:#e6eef6}
        .wrap{padding:18px;display:flex;flex-direction:column;gap:18px;height:100%;box-sizing:border-box}
        header{display:flex;align-items:center;justify-content:space-between;gap:12px}
        .title{display:flex;align-items:center;gap:12px}
        .logo{width:44px;height:44px;border-radius:8px;background:linear-gradient(135deg,var(--accent),#7c3aed);display:flex;align-items:center;justify-content:center;font-weight:700}
        h1{font-size:1.05rem;margin:0}
        .subtitle{color:var(--muted);font-size:0.85rem}

        .toolbar{display:flex;gap:8px;align-items:center}
        .search{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.03);padding:8px 10px;border-radius:8px;color:var(--muted);min-width:220px}
        .btn{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.03);padding:8px 10px;border-radius:8px;color:var(--muted);cursor:pointer}

        .grid{display:grid;grid-template-columns:repeat(auto-fill, minmax(220px,1fr));gap:var(--gap);align-items:start}
        .card{background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));padding:12px;border-radius:var(--radius);box-shadow:0 2px 18px rgba(2,6,23,0.6);min-height:110px;display:flex;flex-direction:column;gap:10px}
        .row{display:flex;justify-content:space-between;align-items:center}
        .name{font-weight:600}
        .desc{color:var(--muted);font-size:0.85rem}

        .badges{display:flex;gap:8px;align-items:center}
        .badge{padding:6px 8px;border-radius:999px;font-size:0.78rem;color:#051025;font-weight:600}
        .priority{background:linear-gradient(90deg,var(--accent),#7c3aed)}
        .risk-low{background:var(--good)}
        .risk-med{background:var(--warn)}
        .risk-high{background:var(--bad)}
    /* queued/placeholder badge style while we animate in real badges */
    .badge.placeholder{background:rgba(255,255,255,0.03);color:var(--muted);opacity:0.6}
    /* explicit priority colors to match urgency cues (P1=high/red, P2=warn/amber, P3=low/green) */
    .priority-p1{background:var(--bad);color:#fff}
    .priority-p2{background:var(--warn);color:#051025}
    .priority-p3{background:var(--good);color:#051025}

        footer{margin-top:auto;color:var(--muted);font-size:0.82rem}

        @media (max-width:520px){.grid{grid-template-columns:repeat(1,1fr)} .search{min-width:120px}}
    </style>
</head>
<body>
    <div class="wrap">
        <header>
            <div class="title">
                <div class="logo">A</div>
                <div>
                    <h1>ADF Plan Preview</h1>
                    <div class="subtitle">Quick, at-a-glance preview of plan steps with priority & risk</div>
                </div>
            </div>
                <div class="toolbar">
                        <input id="q" class="search" placeholder="Search steps or IDs..." />
                        <select id="filterPriority" class="search">
                            <option value="all">All priorities</option>
                            <option value="P1">P1</option>
                            <option value="P2">P2</option>
                            <option value="P3">P3</option>
                        </select>
                        <select id="filterRisk" class="search">
                            <option value="all">All risks</option>
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                        </select>
                        <select id="sortBy" class="search">
                            <option value="priority">Sort: Priority</option>
                            <option value="risk">Sort: Risk</option>
                            <option value="title">Sort: Title</option>
                        </select>
                        <button id="refresh" class="btn">Refresh</button>
                        <button id="openLogs" class="btn">Open Logs</button>
                    </div>
        </header>

            <section class="grid" id="cards">
                <!-- dynamic cards rendered here -->
            </section>

        <footer>Tip: click a card to copy its name. This preview is a starting point — wire it to real data in the extension.</footer>
    </div>

            <script>
            const vscode = acquireVsCodeApi?.();
            const q = document.getElementById('q');
            const cardsEl = document.getElementById('cards');
            const filterPriority = document.getElementById('filterPriority');
            const filterRisk = document.getElementById('filterRisk');
            const sortBy = document.getElementById('sortBy');

            let cardsState = [];

            // queue of badge render jobs to create a staggered/cascading badge reveal
            const badgeRenderQueue = [];
            let badgeProcessing = false;
            function processBadgeQueue() {
                if (badgeProcessing) return;
                badgeProcessing = true;
                const delay = 120; // ms per badge
                function next() {
                    const job = badgeRenderQueue.shift();
                    if (!job) {
                        badgeProcessing = false;
                        return;
                    }
                    try { job(); } catch (e) { /* ignore individual job errors */ }
                    setTimeout(next, delay);
                }
                // kick off
                setTimeout(next, delay);
            }

            // Apply filters and sorting then render
            function applyAndRender() {
                let list = cardsState.slice();
                const term = q.value.trim().toLowerCase();
                const fp = filterPriority.value;
                const fr = filterRisk.value;
                const sort = sortBy.value;

                // filter
                list = list.filter(c => {
                    if (fp !== 'all' && (String(c.priority || '').toLowerCase() !== String(fp).toLowerCase())) return false;
                    if (fr !== 'all' && (String(c.risk || '').toLowerCase() !== String(fr).toLowerCase())) return false;
                    if (term) {
                        const hay = ((c.title || '') + ' ' + (c.id || '') + ' ' + (c.description || '')).toLowerCase();
                        if (!hay.includes(term)) return false;
                    }
                    return true;
                });

                // sort
                const priorityRank = p => {
                    if (!p) return 99;
                    const s = String(p).toLowerCase();
                    if (s.includes('p1') || s.includes('1')) return 1;
                    if (s.includes('p2') || s.includes('2')) return 2;
                    if (s.includes('p3') || s.includes('3')) return 3;
                    return 99;
                };
                const riskRank = r => {
                    if (!r) return 2;
                    const s = String(r).toLowerCase();
                    if (s.includes('low')) return 0;
                    if (s.includes('medium') || s.includes('med')) return 1;
                    if (s.includes('high')) return 2;
                    return 1;
                };

                if (sort === 'priority') {
                    list.sort((a,b) => priorityRank(a.priority) - priorityRank(b.priority));
                } else if (sort === 'risk') {
                    list.sort((a,b) => riskRank(a.risk) - riskRank(b.risk));
                } else if (sort === 'title') {
                    list.sort((a,b) => ('' + (a.title||a.id||'')).localeCompare('' + (b.title||b.id||'')));
                }

                renderCards(list);
            }

            // Render dynamic cards supplied by the extension
            function renderCards(cards) {
                cardsEl.innerHTML = '';
                if (!cards || !cards.length) {
                    const empty = document.createElement('div');
                    empty.style.color = 'var(--muted)';
                    empty.textContent = 'No plan steps found.';
                    cardsEl.appendChild(empty);
                    return;
                }

                cards.forEach(c => {
                    const card = document.createElement('div');
                    card.className = 'card';
                    card.setAttribute('data-title', c.title || c.id || '');
                    card.style.position = 'relative';

                    const row = document.createElement('div'); row.className = 'row';
                    const name = document.createElement('div'); name.className = 'name'; name.textContent = c.title || c.id || '';
                    const badges = document.createElement('div'); badges.className = 'badges';
                        // create placeholder badges then queue actual render to provide a staged/animated feel
                        const pri = document.createElement('div'); pri.className = 'badge placeholder priority'; pri.textContent = '...';
                        const risk = document.createElement('div'); risk.className = 'badge placeholder risk-placeholder'; risk.textContent = '...';
                        badges.appendChild(pri); badges.appendChild(risk);

                        // queue the final badge rendering (staggered) to give an urgency cue
                        badgeRenderQueue.push(() => {
                            // priority mapping
                            const p = (c.priority || '').toString().toLowerCase();
                            pri.textContent = c.priority || 'P2';
                            pri.classList.remove('placeholder');
                            pri.classList.remove('priority-p1','priority-p2','priority-p3');
                            if (p.includes('p1') || p === '1') {
                                pri.classList.add('priority-p1');
                            } else if (p.includes('p2') || p === '2') {
                                pri.classList.add('priority-p2');
                            } else {
                                pri.classList.add('priority-p3');
                            }

                            // risk mapping
                            const r = (c.risk || '').toString().toLowerCase();
                            risk.textContent = c.risk || 'Medium';
                            risk.classList.remove('placeholder');
                            risk.classList.remove('risk-low','risk-med','risk-high');
                            if (r === 'low') risk.classList.add('risk-low');
                            else if (r === 'high') risk.classList.add('risk-high');
                            else risk.classList.add('risk-med');
                        });

                    row.appendChild(name); row.appendChild(badges);
                    const desc = document.createElement('div'); desc.className = 'desc'; desc.textContent = c.description || '';
                    card.appendChild(row); card.appendChild(desc);

                    card.addEventListener('click', () => {
                        const title = c.title || c.id || '';
                        navigator.clipboard.writeText(title || '');
                        if (vscode) vscode.postMessage({ type: 'cardClick', name: title, id: c.id, logPath: c.logPath });
                        const tip = document.createElement('div');
                        tip.textContent = 'Copied';
                        tip.style.position = 'absolute'; tip.style.padding = '6px 8px'; tip.style.borderRadius = '6px'; tip.style.background = 'rgba(0,0,0,0.6)'; tip.style.color = '#fff'; tip.style.top = '8px'; tip.style.right = '8px';
                        card.appendChild(tip);
                        setTimeout(() => tip.remove(), 900);
                    });

                    cardsEl.appendChild(card);
                });
                        // start processing queue (staggered) — small delay per card for a cascading badge reveal
                        processBadgeQueue();
            }

            // wire events
            q.addEventListener('input', applyAndRender);
            filterPriority.addEventListener('change', applyAndRender);
            filterRisk.addEventListener('change', applyAndRender);
            sortBy.addEventListener('change', applyAndRender);
            document.getElementById('refresh').addEventListener('click', () => {
                if (vscode) vscode.postMessage({ type: 'refresh' });
            });

            document.getElementById('openLogs').addEventListener('click', () => {
                if (vscode) vscode.postMessage({ type: 'openLogs' });
            });

            // Handle messages from extension
            window.addEventListener('message', event => {
                const msg = event.data;
                if (msg && msg.type === 'setCards' && Array.isArray(msg.cards)) {
                    cardsState = msg.cards || [];
                    applyAndRender();
                }
            });
        </script>
</body>
</html>`;
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