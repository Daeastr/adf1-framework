{
  "name": "aadf-plan-preview",
  "displayName": "AADF Plan Preview",
  "description": "VS Code extension for AADF framework plan preview and log monitoring",
  "version": "0.0.1",
  "engines": {
    "vscode": "^1.74.0"
  },
  "categories": [
    "Other"
  ],
  "activationEvents": [
    "onCommand:aadf.showPlanPreview",
    "workspaceContains:**/orchestrator_artifacts",
    "workspaceContains:**/orchestrator_state.json"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "viewsContainers": {
      "activitybar": [
        {
          "id": "aadfPreview",
          "title": "AADF Plan Preview",
          "icon": "resources/plan.svg"
        }
      ]
    },
    "views": {
      "aadfPreview": [
        {
          "id": "aadfPlanTree",
          "name": "Current Plan",
          "when": "workspaceFolder"
        }
      ],
      "explorer": [
        {
          "id": "aadfStepLogs",
          "name": "Step Logs",
          "when": "workspaceFolder"
        }
      ]
    },
    "commands": [
      {
        "command": "aadf.showPlanPreview",
        "title": "Show Plan Preview",
        "icon": "$(preview)"
      },
      {
        "command": "aadf.openPlanPreview",
        "title": "Open Plan Preview",
        "icon": "$(eye)"
      },
      {
        "command": "aadfLogs.openLog",
        "title": "Open Log File"
      },
      {
        "command": "aadfLogs.refresh",
        "title": "Refresh Logs",
        "icon": "$(refresh)"
      }
    ],
    "menus": {
      "view/title": [
        {
          "command": "aadfLogs.refresh",
          "when": "view == aadfStepLogs",
          "group": "navigation"
        }
      ],
      "commandPalette": [
        {
          "command": "aadf.showPlanPreview",
          "when": "workspaceFolder"
        },
        {
          "command": "aadf.openPlanPreview",
          "when": "workspaceFolder"
        }
      ]
    }
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./"
  },
  "devDependencies": {
    "@types/vscode": "^1.74.0",
    "@types/node": "16.x",
    "typescript": "^4.9.4"
  }
}
