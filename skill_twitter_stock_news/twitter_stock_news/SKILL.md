---
name: twitter_stock_news
description: Fetches your X/Twitter home timeline and summarizes stock market sentiment
user-invocable: true
metadata:
  openclaw:
    requires:
      bins: ["python3"]
tools:
  - name: summarize_twitter_feed
    description: Fetches and summarizes stock market sentiment from your X/Twitter home timeline.
    parameters: {}
    code: |
      print(default_api.exec(command="python3 ~/.openclaw/skills/twitter_stock_news/twitter_feed.py"))
---

# Twitter Stock News Skill

## Purpose

Fetches the user's X/Twitter home timeline and analyzes it for stock market news — summarizing overall market sentiment and surfacing the most relevant posts.

> "X feed" and "Twitter feed" are interchangeable — treat any reference to either as a request to run this skill.

## How to invoke

Run the following shell command:

```bash
python3 ~/.openclaw/skills/twitter_stock_news/twitter_feed.py
```

It returns up to 100 posts from the last 2 hours, each formatted as:

```
From @username: post text
```

## What to do with the results

1. **Filter for stock market content only** — ignore posts unrelated to markets, stocks, investing, or economic news
2. **Determine overall sentiment** — based on the filtered posts, classify the mood as one of:
   - 🚀 **Bullish** — optimism, upward moves, strong earnings, positive catalysts
   - 😡 **Bearish** — pessimism, downward pressure, negative macro, risk-off signals
   - ❔ **Neutral** — mixed signals, sideways action, uncertainty
3. **Summarize key drivers** — briefly explain the 2–4 notable news elements contributing to that sentiment (e.g. Fed commentary, earnings beats/misses, sector moves, macro data). Prefix each with an appropriate emoji that reflects the nature of the driver (e.g. 🏦 for Fed/rates, 📈 for positive price action, 📉 for declines, 💵 for earnings, 🌍 for macro/geopolitical, ⚡ for energy, etc.)
4. **List the 3 most notable posts** — ranked by relevance and importance to the overall summary. For each post include:
   - The @username and any relevant context about who they are
   - The time the post was made, converted to US Eastern Time
   - The post content
   - Why it's notable

## Output format

```
🚀 Bullish / 😡 Bearish / ❔ Neutral

**Sentiment:** [one sentence]

**Key drivers:**
- [emoji] [driver 1]
- [emoji] [driver 2]
- [emoji] [driver 3]

**Top posts:**
1. @username · [time ET] — [post text]
   *(why it matters)*

2. @username · [time ET] — [post text]
   *(why it matters)*

3. @username · [time ET] — [post text]
   *(why it matters)*
```

## Example prompts

> What's the stock market sentiment on my Twitter feed?
> Summarize my Twitter feed
> What's the market looking like today?
> Any big news in the market?
> What's moving on my X feed?
> Summarize my X feed
> What are people saying about stocks on X?

## Edge cases

- If no stock-related posts are found, say so — don't summarize unrelated content
- If fewer than 3 notable posts exist, list however many are available
- If a 403 error occurs, explain that the X API tier may not support home timeline access and suggest upgrading to pay-per-use
