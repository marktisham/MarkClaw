# Twitter Stock News — Skill Setup

> Connects your OpenClaw instance to your X/Twitter home timeline so the agent can fetch and summarize posts from accounts you follow.

**Prerequisites:** A running OpenClaw instance on GCP. If you haven't set that up yet, start with [Deploy OpenClaw on a Private GCP Compute Engine Instance](vm_setup.md).

> **Cost note:** Reading your timeline uses the X API pay-per-use model at ~$0.005 per post read. For occasional personal summarization (e.g. fetching 50–100 posts a few times a day) this will cost pennies.

---

## Step 1: Create an X Developer Account

1. Go to [console.x.com](https://console.x.com) and sign in with your X account
2. Accept the **Developer Agreement and Policy**
3. When prompted to describe your use case, write at least 250 characters explaining your intent — something like:

   > *"I am building a personal AI assistant for private use. I want to read my own home timeline to generate summaries of posts from accounts I follow. This is for personal productivity only — no data will be stored, shared, or used for commercial purposes."*

4. Submit and wait for approval (usually instant for personal use)

---

## Step 2: Enable pay-per-use and add credits

1. In the Developer Console, navigate to **Billing & Usage**
2. Switch to **Pay-per-use**
3. Purchase a small credit amount to start (e.g. $5–10 — enough for months of personal summarization)
4. Confirm your billing details

---

## Step 3: Create an App and generate credentials

1. From the Developer Console, click **+ Create App**
2. Give it a name (e.g. `openclaw-personal`)
3. Under **App permissions**, select **Read** (we only need to read your timeline — no need for write access)
4. On creation the console shows your **Consumer Key** and **Secret Key** — save them immediately in a password manager (shown once only)
5. Navigate to the **User Authentication Settings** section and click **Set up**. Configure it as follows:
   - **App permissions:** Select **Read**
   - **Type of App:** Select **Web App, Android, or iOS** (the most flexible option)
   - **Callback URI / Redirect URL:** Enter `http://localhost:8080` — X requires this even for local scripts
   - **Website URL:** Enter any URL (your GitHub profile or `http://example.com` works fine)
   - Click **Save** at the bottom of the page
6. Under **OAuth 1.0 Keys**, click **Generate** next to **Access Token**. This generates two more credentials — save both immediately:
   - **Access Token**
   - **Access Token Secret**

   > The Access Token authenticates as *you* (@your-handle), which is required to read your private home timeline. The Consumer Key alone is not sufficient.

---

## Step 4: Install dependencies (on the VM)

If you're not already SSH'd into your VM, connect now from your Mac:

```bash
gcloud compute ssh [YOUR_INSTANCE] --zone=[YOUR_ZONE]
```

The Twitter Stock News skill requires Python and the `tweepy` library:

```bash
sudo apt install -y python3-pip && pip3 install tweepy python-dotenv --break-system-packages
```

Notice: `--break-system-packages` is safe here — this is a dedicated single-purpose VM and there's no risk of conflicting Python apps.

Now create the skills directory and register it with OpenClaw:

```bash
mkdir -p ~/.openclaw/skills
```

Then register it with OpenClaw by adding `~/.openclaw/skills` to the `skills.load.extraDirs` array in `~/.openclaw/openclaw.json`:

```bash
jq '.skills.load.extraDirs += ["~/.openclaw/skills"]' ~/.openclaw/openclaw.json > /tmp/openclaw.json && mv /tmp/openclaw.json ~/.openclaw/openclaw.json
```

---

## Step 5: Configure credentials and upload the skill (on your Mac)

Switch back to a terminal on your Mac for this step.

### 5.1 Edit `.env` with your credentials

Open `twitter_stock_news/.env` and replace the placeholder values with the credentials you saved from Step 3:

```env
TWITTER_API_KEY=your-consumer-key
TWITTER_API_SECRET=your-consumer-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret
```

### 5.2 Upload the skill to the VM

Upload the entire skill folder to your openclaw VM:

```bash
gcloud compute scp --recurse twitter_stock_news/ [YOUR_INSTANCE]:~/.openclaw/skills/ --zone=[YOUR_ZONE]
```

Replace `[YOUR_INSTANCE]` with your VM's name (e.g. `openclaw`) and `[YOUR_ZONE]` with the zone you chose during setup (e.g. `us-central1-a`).

### 5.3 Verify the script runs (on the VM)

```bash
python3 ~/.openclaw/skills/twitter_stock_news/twitter_feed.py
```

You should see recent posts from your timeline printed to the console, or a message that there are no new posts in the last 2 hours. If you get a 403 error, double-check that you completed Step 2 (pay-per-use billing).

---

## Step 6: Register the skill with OpenClaw

### 6.1 Restart the gateway

OpenClaw automatically discovers any skill directory containing a `SKILL.md` file with valid frontmatter on restart:

```bash
openclaw gateway restart
```

### 6.2 Verify the skill is registered

```bash
openclaw skills list
```

Confirm `Twitter Stock News` appears with a status of **ready**.

---

## Step 7: Test the integration

In the OpenClaw dashboard chat, ask:

```
Summarize my Twitter feed
```

The agent should run `twitter_feed.py`, fetch your home timeline, and return a grouped summary. If it works, you can refine the prompt — ask it to filter by topic, highlight key links, focus on specific accounts, etc.

> **Tip:** The skill description in `SKILL.md` controls how the agent formats results. You can edit this file on the VM and restart the gateway to adjust the summarization style.
