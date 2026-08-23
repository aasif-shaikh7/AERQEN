# AERQEN — Phase 1 Manual Testing Guide (for the human operator)

**Document:** `PHASE1_TESTING_GUIDE.md`
**Status:** Active — human acceptance steps for the Phase 1 skeleton pipeline
**Audience:** The non-programmer project owner

This guide tells you exactly what to run, what you should see, and what counts as success
or failure. Framework rule: **never claim a feature works from a screenshot or from "it
looks fine" — run the steps and record what actually happens** (`GLOSSARY.md` -> Measured).

---

## What you are testing

The `echo` demo pipeline. It proves the agent's full loop:

```
Task -> Understand -> Plan -> Policy Check -> Execute -> Observe -> Verify -> Report
```

It is completely safe:
- No mouse/keyboard control
- No real filesystem, no deletion, no network
- The demo tool only returns the message you give it

---

## Before you start

1. Open **Command Prompt** (`cmd`) on the same computer where this project is.
2. Go to the project root. Type:
   ```
   cd "c:\Users\pervi\OneDrive\Attachments\Desktop\ZAID\AASIF\AERQEN"
   ```
3. Make sure the first one-time install happened:
   ```
   python -m pip install pytest
   ```

---

## TEST 1 — Run the pipeline (happy path)

Type and press Enter:

```
python -m app.entrypoint.cli "echo hello aerqen"
```

**You should see:** a report ending with:
- `state     : done`
- an outcome line that includes `Measured: tool returned the exact message.`

**Success if** that `state : done` appears and you saw no red error text.

**Failure if** you get a traceback (a long error starting with `Traceback`) or Python says
`ModuleNotFoundError`. Copy that whole red text and send it to me.

---

## Step 2 — Run the test suite

Type:

```
python -m pytest tests -q
```

**You should see:** `4 passed` and something like `[100%]`.

**Success if** it says `4 passed`.

**Failure if** it says `1 failed` or `Error`. Send the whole output to me.

---

## Test 3 — Try a command the agent does NOT know (expected failure)

Type:

```
python -m app.entrypoint.cli "open office"
```

**You should see:** a short report ending with `state : failed` and an `error` line that
explains it does not know this command.

This is **correct behavior**: the agent must honestly say "I can't do that yet" instead of
pretending it worked.

---

## What counts as done

When all three steps behave as described above, `CRIT-8` (skeleton pipeline) can be marked
`done` in `todo-list.md` + `done-list.md`. Tell me "CRIT-8 accepted" and I will record it.

---

## If something is wrong

Copy the ENTIRE error text (or screenshot) and send it to me exactly. Do not summarize it.
I will investigate, propose the smallest fix, and give you a new command to re-test.

---

## Remember (no fake testing)

From `DEVELOPMENT_AND_TESTING.md`:
> Neither human nor AI may claim "tested", "verified", or "works" unless the test was
> actually performed.

So only say you saw something if you actually ran it and saw it with your own eyes.