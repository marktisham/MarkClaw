# Deploy OpenClaw on a Private GCP Compute Engine Instance

[![YouTube](https://img.shields.io/badge/Watch-FF0000?style=flat&logo=youtube&logoColor=white)](https://youtu.be/0sq7zmLj46g)

> A step-by-step guide to self-hosting the OpenClaw AI gateway on a private GCP VM, using Google Gemini as the model backend.

## Prerequisites

- Google Cloud CLI (`gcloud`) installed and authenticated on your Mac
- A GCP project with billing enabled
- Your GCP project ID: `[YOUR_PROJECT_ID]`

---

## Step 1: Create the GCP VM

We're creating a minimal Ubuntu VM to host the OpenClaw gateway — inference is handled by the Gemini API, so no GPU or large machine is needed.

### 1.1 Open the GCP Console

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Select your project (`[YOUR_PROJECT_ID]`) from the project dropdown at the top

### 1.2 Enable Compute Engine API (if not already)

1. Navigate to **APIs & Services > Enabled APIs & services**
2. Click **+ ENABLE APIS AND SERVICES**
3. Search for **Compute Engine API** and enable it (skip if already enabled)

### 1.3 Create the VM

1. Navigate to **Compute Engine > VM instances**
2. Click **CREATE INSTANCE**
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `openclaw` |
| **Region / Zone** | Any region works — `us-central1` / `us-central1-a` is a good default, but pick whatever is geographically closest to you for lower latency |
| **Machine type** | `e2-small` (2 vCPU, 2 GB memory) |
| **Boot disk** | In the **OS and storage** section, click **Change** → Select **Ubuntu 24.04 LTS** (x86/64), set size to **30 GB**, Standard persistent disk |
| **Firewall** | Leave both **Allow HTTP** and **Allow HTTPS** **unchecked** |

4. Leave everything else as default and click **CREATE**

**Why these choices:**
- **e2-small**: 2 vCPUs, 2 GB RAM — sufficient for the OpenClaw gateway since inference is offloaded to the Gemini API (~$13/mo, or pennies if stopped when idle)
- **Ubuntu 24.04 LTS**: current LTS with Node 24 support
- **30 GB standard disk**: plenty of headroom for the OS, OpenClaw, Node.js, and logs — the gateway alone needs well under 10 GB
- **No firewall rules** — we'll access the dashboard via SSH tunnel only (more secure)

### 1.4 Verify the VM is running

In the **VM instances** list, confirm `openclaw` shows a green checkmark with status **RUNNING**.

### 1.5 SSH into the VM (from your Mac terminal)

```bash
gcloud compute ssh [YOUR_INSTANCE] --zone=[YOUR_ZONE]
```

Replace `[YOUR_ZONE]` with the zone you selected in step 1.3 (e.g. `us-central1-a`).

If prompted to create an SSH key, accept the defaults.

---

## Step 2: Get your Gemini API Key

Do this on your **Mac** before running the OpenClaw installer on the VM — you'll paste the key into the onboarding wizard.

### 2.1 Create an API key

1. Go to [aistudio.google.com](https://aistudio.google.com) in your Mac's browser
2. Sign in with your Google account
3. Click **Get API key** → **Create API key**
4. Select your GCP project (`[YOUR_PROJECT_ID]`) when prompted
5. Copy and save the key somewhere safe

### 2.2 Upgrade to pay-as-you-go to avoid rate limits

The free tier limits you to 15 requests per minute and 1,500 requests per day — easy to hit during normal use. Linking a billing account switches you to pay-as-you-go pricing, which is very affordable for personal use (Gemini Flash costs a fraction of a cent per request).

1. In AI Studio, click your profile icon → **Settings**
2. Under **Billing**, click **Manage billing** — this takes you to the GCP billing console
3. Link your project (`[YOUR_PROJECT_ID]`) to a billing account (create one if needed — a credit card is required but personal use costs are typically under $1/month)
4. Return to AI Studio and confirm the key now shows a paid quota

> If you still hit limits under heavy use, you can request a quota increase: **Cloud Console → APIs & Services → Gemini API → Quotas**, then request an increase for the specific limit (e.g. requests per minute).

---

## Step 3: Install and Configure OpenClaw

Run all commands below **on the VM** (via your SSH session).

### 3.1 Update system packages

Refresh the package index and upgrade all installed packages to their latest versions. This ensures you have current security patches and dependencies before installing new software:

```bash
sudo apt update && sudo apt upgrade -y
```

### 3.2 Install OpenClaw and run the onboarding wizard

The official installer handles Node.js and launches the onboarding wizard automatically:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

The wizard walks you through several steps. Here's what to select:

#### Step 1 — Mode

Select **QuickStart** (sensible defaults for port, auth, etc.)

#### Step 2 — Model provider

Select **Google (Gemini API key)**

When prompted, paste the API key you created in step 2.1.

#### Step 3 — Default model

Select **`google/gemini-2.5-flash`** (fast, cost-effective, and handles OpenClaw's tool-calling reliably)

#### Step 4 — Channel

This is how you'll interact with OpenClaw remotely (e.g. Telegram, Slack, WhatsApp). Select the tool that works best for you and follow the on-screen directions to connect it.

#### Remaining steps

Accept defaults or skip all remaining steps — the wizard will finish setup and install a systemd service so the gateway starts on boot.

### 3.3 Reload your shell after install

The installer updates your PATH but requires a shell reload before `openclaw` is available:

```bash
source ~/.bashrc
```

### 3.4 Confirm everything is running

```bash
openclaw gateway status
```

Expected output confirms:
- `Service: systemd (enabled)` — auto-starts on reboot
- `Runtime: running` — gateway is active
- `RPC probe: ok` — gateway is reachable
- `Dashboard: http://127.0.0.1:18789/` — ready for SSH tunnel access

## Step 4: Access the Dashboard from Your Mac

The gateway binds to loopback (`127.0.0.1`) on the VM — it's not exposed to the internet. We forward it to your Mac via an SSH tunnel.

### 4.1 Get the dashboard URL and tunnel command (on the VM)

In your SSH session, run:

```bash
openclaw dashboard
```

This prints everything you need, e.g.:
```
Dashboard URL: http://127.0.0.1:18789/#token=<your-token>
No GUI detected. Open from your computer:
ssh -N -L 18789:127.0.0.1:18789 <user>@<internal-ip>
Then open:
http://localhost:18789/#token=<your-token>
```

Note the two lines under "Then open:" — you'll use the `localhost` version in your browser.

### 4.2 Open the tunnel (on your Mac, in a new terminal tab)

```bash
gcloud compute ssh openclaw --zone=[YOUR_ZONE] -- -L 18789:127.0.0.1:18789 -N
```

Keep this tab open while using the dashboard. (`-N` means tunnel-only, no shell.)

### 4.3 Open the dashboard

Paste the `http://localhost:18789/#token=...` URL printed in step 4.1 into your Mac's browser. You'll land directly in the dashboard without being prompted for a token.

## Step 5: Verify and Personalize the Assistant

Before adding integrations, confirm the assistant is working and personalize its identity.

### 5.1 Send a test message

In the dashboard chat interface, send a simple message like:

```
Hello! What model are you running on?
```

You should get a response confirming it's using `gemini-2.5-flash`. This verifies the full stack is working end-to-end — OpenClaw is routing requests to the Gemini API successfully.

### 5.2 Personalize through conversation

OpenClaw recommends configuring its identity and personality by prompting the agent directly — it will guide you through the process and update its own configuration files. Start with something like:

```
I'd like to personalize you. Let's set up your identity, personality, and some context about me.
```

Follow the agent's prompts from there.

> **Reference:** Under the hood, the agent writes to markdown files in `~/.openclaw/workspace/` — `IDENTITY.md`, `SOUL.md`, `USER.md`, `AGENTS.md`, and `TOOLS.md` — which are injected into every conversation. You can inspect or manually edit these on the VM if needed, but the recommended path is through conversation.

## Next Steps: Add Skills

Once your instance is running, you can extend it with skills that give the agent real-world capabilities.

- [Twitter Stock News Skill Setup](skill_twitter_stock_news/skill_setup.md) — connect your X/Twitter home timeline so the agent can summarize posts from accounts you follow

---

## Appendix: FAQ

### How do I switch to a different Gemini model?

To change the default model on an existing OpenClaw install:

1. **Update OpenClaw's default model** (on the VM):

   ```bash
   openclaw config patch '{"agents": {"defaults": {"model": {"primary": "google/gemini-2.5-flash"}}}}'
   ```

   Replace `google/gemini-2.5-flash` with whichever Gemini model you want to use.

2. **Restart the gateway:**

   ```bash
   openclaw gateway restart
   ```

3. **Verify** by sending a test message in the dashboard and confirming the model in the response.

> To see available Gemini models, check [Google AI Studio](https://aistudio.google.com) or the [Gemini API model list](https://ai.google.dev/gemini-api/docs/models).
