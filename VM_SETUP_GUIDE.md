# AERQEN — Virtual Machine (VM) Setup Guide for Windows 11

**Document:** `VM_SETUP_GUIDE.md`
**Status:** Active — working guide for Decision/ADR-007 (Windows 11 VM target)
**Audience:** The non-programmer developer / project owner
**Cost:** Free (VirtualBox is free and open-source)

Per the accepted decision (ADR-007 / `TECHNOLOGY_SELECTION.md` §1), AERQEN's development and
testing runs inside a **Windows 11 Virtual Machine (VM)** so that a failure can never harm
your real computer's data. This guide explains, in simple language, how to set that up even
if you have never used a VM before.

> **What is a VM?** A VM is a "computer inside your computer". You create a virtual Windows 11
> that runs as a normal program on your real machine. Anything that breaks inside it stays
> inside it. See `GLOSSARY.md` → "Virtual Machine" (added below).

---

## 1. What you need (checklist)

- A Windows 10 **or** Windows 11 **host** computer (your real machine) — Windows is easiest for this guide.
- At least **8 GB of RAM** total (16 GB is more comfortable).
- At least **40 GB of free disk space**.
- Internet access for this one-time setup.
- Approx. 1–2 hours for the whole setup.

> A VM makes one copy of your real computer, so never run the VM at the same time as another
> heavy program if your RAM is low.

---

## 2. Install VirtualBox (the free tool that runs VMs)

1. Open your browser and go to the official site:
   `https://www.virtualbox.org`
2. Click **Downloads**, then choose the **Windows** download (the `x86/amd64` or "Windows" .exe).
3. Open the downloaded `.exe` and follow the install steps (Next / Install / Finish).
4. After install, look for the **VirtualBox** icon and open it. This is the "host" screen.

---

## 3. Get a free Windows 11 ISO (disk image)

A "ISO" is a single file that contains the full Windows install.

1. Go to Microsoft's official free Windows page:
   `https://www.microsoft.com/software-download/windows11`
2. Choose **Download Windows 11 Disk Image (ISO)**.
3. Pick the version that matches your real computer (usually "Windows 11" and one architecture).
4. Microsoft will ask for an email to send a link — use any personal email (no student email needed).
5. Save the downloaded `.iso` file somewhere you can find (e.g. `Downloads`).

> **Note:** Microsoft may ask you to pick a release; choose "Release" (Windows 11 23H2+) for a normal install.

---

---

## 5. Attach the Windows 11 ISO and start the install

1. Select your VM (`AERQEN-Win11`) in the list, click **Settings** (gear) → **Storage**.
2. Under the empty CD/DVD slot, click the disk icon → **Choose a disk file** → pick the downloaded Windows 11 `.iso`.
3. Close Settings. Select the VM and click **Start** (green arrow).
4. The VM will boot from the ISO. Follow the normal **Windows setup**:
   - Choose language/layout.
   - When it asks for a Microsoft account, prefer **"Set up without internet" / "Sign in later"** if shown — it avoids account hassle.
   - Create a local user + password.
   - Finish until you reach the Windows 11 desktop **inside the VM**.

> **Tip:** Click inside the VM to use it. Press `Right Ctrl` to release your mouse back to your real computer.

---

## 6. Install the "Guest Additions" (important)

Guest Additions make the VM faster and allow copy/paste between real and virtual machine.

1. Inside the running VM desktop, open the **CD/DVD icon** (or Devices menu) and choose **Insert Guest Additions CD image**.
2. Open `This PC` in the VM, open the "VirtualBox Guest Additions" CD, and run `VBoxWindowsAdditions.exe`.
3. Follow the install, then **restart the VM**.

Now you can resize the window and share clipboard between real machine and VM.

---

## 7. Install Python + the tools inside the VM

Now you have a clean, safe Windows 11 where you will do AERQEN development/testing. Inside the VM:

1. Download Python: `https://www.python.org/downloads/` → Windows → install (check both **"Add Python to PATH"** boxes).
2. Open **Command Prompt** in the VM and verify:
   ```bat
   python --version
   ```
   You should see `Python 3.12...` (or "Python 3.x").
3. Install the chosen AERQEN libraries (from §5/§6 decisions):
   ```bat
   pip install pyautogui pywinauto mss pillow
   ```
4. Install Ollama inside the VM too (see `OLLAMA_SETUP_GUIDE.md`).

---

## 8. Save + protect your VM (snapshot)

A **snapshot** saves the VM's exact state, so if something breaks you can hop back to a known-good state.

1. While the VM is **off** (shut down): in VirtualBox, select it → **Snapshots** → **Take Snapshot**.
2. Name it `Clean base install`. Now you have a restart point.

> Take a snapshot now, before you install anything else, so you always have a clean start.

---

## 9. How to protect the real machine from the VM

- Keep the VM inside VirtualBox; never give the VM access to your real files by default.
- Only **share** a folder if you mean to (Settings → Shared Folders).
- Run system/security tests (ADR-008) inside the VM, and unit/integration tests on the real machine.

---

## 10. First-run checklist (measure honestly)

| Step | Status label |
|---|---|
| VirtualBox installed | **Unverified** until you launch the VirtualBox icon |
| Windows 11 ISO downloaded | **Unverified** until the `.iso` file exists |
| VM created + install finished | **Unverified** until you see the Win desktop inside the VM |
| Guest Additions installed | **Unverified** until you resize the VM window easily |
| Python + libs installed | **Measured** only after `python --version` and `pip install` each finish |
| Snapshot taken | **Unverified** until you see the snapshot saved |

Do not claim "VM ready" until the measured checklist is true.

---

## Common problems and fixes

| Problem | Likely cause | Fix |
|---|---|---|
| "VT-x / hardware acceleration not available" | Virtualization disabled in the real machine's BIOS | Enable "VT-x/AMD-V" in your real computer's BIOS settings |
| VM is very slow | Not enough RAM to the VM | Increase VM memory; close other apps on the real machine |
| Mouse stuck inside the VM | Guest Additions not installed | Press `Esc`, then install Guest Additions |
| Can't find the ISO | File not downloaded / link not clicked | Check `Downloads`; re-run the Windows download page |

---

## Related

- Target decision: `ARCHITECTURE_DECISION_LOG.md` → ADR-007 / `TECHNOLOGY_SELECTION.md` §1
- Testing decision: ADR-008 / `TECHNOLOGY_SELECTION.md` §8
- Local AI setup: `OLLAMA_SETUP_GUIDE.md`

---

## New glossary term

**Virtual Machine (VM):** a software-emulated separate computer running inside your real
computer. Files and programs inside the VM cannot affect your real system unless you let them.
## 4. Create the Virtual Machine in VirtualBox

Open VirtualBox and do:

1. Click the **New** / **New Machine** button.
2. **Name:** type `AERQEN-Win11` (any name is fine).
3. **Type:** choose **Microsoft Windows**; **Version:** choose **Windows 11 (64-bit)**.
4. **Memory size:** give it **at least 2048 MB (2 GB)** — more if your machine has 8 GB+ free (use ~half of real RAM; e.g. give 4 GB if you have 8–16 GB).
5. **Hard disk:** accept **Create a virtual hard disk now** (recommended size 32–64 GB).
6. Click **Create / Finish**.