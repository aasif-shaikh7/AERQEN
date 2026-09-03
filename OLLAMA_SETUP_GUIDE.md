# AERQEN — Local LLM Setup Guide (Ollama)

**Document:** `OLLAMA_SETUP_GUIDE.md`
**Status:** Active — working guide for Decision/ADR-005 (AI provider: local Ollama)
**Audience:** The non-programmer developer / project owner
**Cost:** Free (Ollama is open-source; the model is free to download)

Following the accepted decision (ADR-005), AERQEN's Brain/Planner AI runs through a **local**
large language model served by **Ollama**. This guide explains, in simple language, how to
install Ollama on Windows, download a model, and verify it works — all offline and free.

> **Term:** A "model" here is the AI brain. The model runs entirely on your computer, so your
> data never leaves your machine. See `GLOSSARY.md` → "Model".

---

## 1. What you need

- A Windows 10 or Windows 11 computer
- Internet **only during download** (later use is offline)
- Enough free disk space (a small model is a few GB)

---

## 2. Install Ollama

1. Open your internet browser and go to the official site:
   `https://ollama.com`
2. Click **Download** and choose **Windows**.
3. Open the downloaded `.exe` file and follow the install steps (click Next/Install).
4. After install, Ollama runs in the background. You can check it by opening a **Command Prompt** (type `cmd` in the Start menu) and typing:

   ```bat
   ollama --version
   ```

   You should see something like `ollama version 0.x.x`. If you see this, Ollama is installed.

---

## 3. Download a small free model

As a **free** default for AERQEN, download a small, fast model. In the **same Command Prompt** window, type:

```bat
ollama pull qwen2.5:3b
```

Wait for it to finish (it shows a progress bar). This is a one-time download.

> What if my computer is slow / low memory?
> Use an even smaller model: `ollama pull qwen2.5:1.5b` (faster, less smart).
> What if I have a good computer?
> Use a bigger one: `ollama pull qwen2.5:7b` (smarter, slower).

---

## 4. Test the model (measure, don't assume)

In the same Command Prompt, type:

```bat
ollama run qwen2.5:3b
```

Now type a simple question, for example:

```
What is 5 + 7?
```

The model should reply (for example `12`). Then type `/bye` to exit.

**This is your "Measured" evidence** that the local model works. Write it down. Never claim
"the AI works" without this actual test (see `GLOSSARY.md` → Measured).

---

## 5. How AERQEN will talk to Ollama

AERQEN's `integrations/ai/` layer talks to Ollama using its local API. Ollama's API lives at:

```
http://localhost:11434
```

That address is **only on your computer** — no internet traffic (per ADR-006, all-local).
AERQEN code does not know which provider it is using; it talks through a provider **adapter**
(ADR-005), so you can swap models or add a cloud provider later without changing the Brain.

A quick manual API test (optional but useful). In Command Prompt:

```bat
curl http://localhost:11434/api/tags
```

If it prints something like `{"models":[...]}`, the Ollama API is running.

---

## 6. Common problems and fixes

| Problem | Likely cause | Fix |
|---|---|---|
| `ollama` is not recognized | Ollama not installed / not in PATH | Reinstall Ollama, then reopen Command Prompt |
| Even after install, command fails | Terminal opened before install | Close and reopen Command Prompt |
| `pull` is slow and never finishes | Slow internet | Wait longer; or pick a smaller model |
| Computer is very slow / out of memory | Model too big for RAM | Use a smaller model (`1.5b`) |
| Firewall blocks `localhost:11434` | Security software | Allow Ollama on your local network (localhost is safe) |

---

## 7. Never do this

- **Never** hard-code any model key or credential in code. Local Ollama needs no key, but if
  you ever add a cloud provider, use environment variables, not the source code (`SECURITY.md`).
- **Never** claim the AI "works" unless you actually ran the test in step 4.
- **Never** run this on data you must not lose until you have test backups.

---

## 8. Status

| Item | Evidence (2026-09-03( |
|---|---|---|
| Ollama installed | **Measured** — `ollama --version` -> `version is 0.33.2` |
| Model downloaded | **Measured** — `ollama pull qwen2.5:7b` completed;; `ollama list` -> `qwen2.5:7b  4.7 GB` |
| Model answers | **Pending** — run `ollama run qwen2.5:7b`, ask "What is  ️5+7?", then `/bye`;; record the reply here |

Update this table honestly as you complete each step.

---

## Related

- Decision: `ARCHITECTURE_DECISION_LOG.md` → `ADR-005`
- Feasibility record: `TECHNOLOGY_SELECTION.md` → section 3
- Deployment model: `ARCHITECTURE_DECISION_LOG.md` → `ADR-006`
- Terms: `GLOSSARY.md`