# AI Computer Employee — Security Policy

## 1. Security Goal
The agent must be useful without becoming an unrestricted process that can accidentally or maliciously damage the computer, data, accounts, or external systems.

## 2. Permission Levels

### LOW RISK
Can normally run automatically:
- Read non-sensitive files
- Take screenshots
- Calculate
- Create temporary files
- Search allowed sources
- Generate drafts

### MEDIUM RISK
Normally requires clear policy evaluation and may require approval:
- Modify existing files
- Install packages
- Run scripts that modify data
- Send data to external services
- Change application settings

### HIGH RISK
Requires explicit user confirmation:
- Delete files
- Overwrite important files
- Send external messages
- Purchase or financial transactions
- Change passwords or account security
- Install unknown software
- Upload sensitive/private data
- Execute destructive system commands

## 3. Secrets
- Never hard-code API keys.
- Never commit secrets to Git.
- Use environment variables or a secure secret store.
- Do not log passwords, tokens, cookies, or private keys.

## 4. Computer Control
The agent must have:
- A global Stop/Cancel mechanism
- Bounded retries
- Action logging
- Permission checks
- Verification after important actions

## 5. Browser Safety
Do not bypass:
- CAPTCHA
- Authentication
- Access controls
- Security restrictions

The agent must not attempt to defeat website security mechanisms.

## 6. Code Execution
Generated code must be treated as untrusted until reviewed/tested. Prefer isolated environments for arbitrary code execution.

## 7. Data Minimization
Only collect and retain data required for the task. Avoid unnecessary screenshots and sensitive information in logs.

## 8. Security Testing
Every major capability must include negative tests:
- Unauthorized action
- Missing permission
- Invalid input
- Tool failure
- Timeout
- Partial completion
- Recovery failure

## 9. Incident Response
If a security issue is discovered:
1. Stop affected automation.
2. Preserve relevant logs without exposing secrets.
3. Reproduce safely.
4. Fix.
5. Add a regression test.
6. Document the change.
