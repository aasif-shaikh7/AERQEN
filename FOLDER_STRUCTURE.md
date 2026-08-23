# AI Computer Employee — Repository Structure

This is the target structure. It may evolve only through documented architecture decisions.

```text
AI_COMPUTER_EMPLOYEE/
│
├── README.md
├── PRD.md
├── ARCHITECTURE.md
├── FOLDER_STRUCTURE.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── ROADMAP.md
├── DEVELOPMENT_AND_TESTING.md
├── AI_DEVELOPMENT_GUIDE.md
├── CHANGELOG.md
├── LICENSE
├── .gitignore
│
├── app/
│   ├── entrypoint/
│   ├── ui/
│   └── configuration/
│
├── core/
│   ├── brain/
│   ├── planner/
│   ├── executor/
│   ├── verifier/
│   ├── recovery/
│   └── task_manager/
│
├── agents/
│   ├── computer/
│   ├── browser/
│   ├── office/
│   ├── coding/
│   ├── research/
│   └── specialist/
│
├── tools/
│   ├── filesystem/
│   ├── browser/
│   ├── computer/
│   ├── documents/
│   ├── spreadsheets/
│   ├── presentations/
│   ├── pdf/
│   └── developer/
│
├── security/
│   ├── policy/
│   ├── permissions/
│   ├── approvals/
│   └── audit/
│
├── memory/
│   ├── user/
│   ├── projects/
│   └── tasks/
│
├── integrations/
│   ├── ai/
│   ├── windows/
│   └── external_services/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── system/
│   ├── security/
│   └── regression/
│
├── docs/
│   ├── decisions/
│   ├── user_guides/
│   └── troubleshooting/
│
└── data/
    ├── logs/
    ├── runtime/
    └── test/
```

## Structure Rule
Do not create modules merely because they look useful. Add a module when a real requirement or architectural boundary justifies it.
