awesome — here’s a complete, hand-off-ready spec your devs can implement. it includes (1) a prompt pack for each AI node and (2) a technical spec with data schemas, env vars, flow logic, QA controls, and posting/playbooks.

---

# brightface.ai — automated content engine

**goal:** automatically turn curated AI/branding/photography news + evergreen topics into on-brand posts for linkedin & x, and long-form drafts for the brightface blog.
**guardrails:** high relevance to brightface, human-sounding tone, no hallucinated facts, links always to brightface.ai with utm tags.

---

## 1) prompt pack (drop-in for your nodes)

### A) scoring AI (relevance + virality)

**purpose:** rate each incoming item for *relevance to brightface* and *engagement potential*.

**system prompt**

> you are an editorial analyst for brightface.ai (ai headshots & personal branding). score incoming content for how well it can be turned into an engaging post that promotes brightface without sounding salesy.

**user prompt (inputs: `{title}`, `{summary}`, `{full_text}`, `{source}`, `{url}`)**
return strict json:

```
Article:
- Title: {title}
- Summary: {summary}
- Source: {source}
- URL: {url}

Task:
1) Relevance: does this help our audience with AI headshots, personal branding, linkedin optimization, ai content tools, or startup/creator growth?
2) Freshness: is this still timely (<= 14 days) or evergreen?
3) Angle: suggest 1–2 “brightface angles” that connect this topic to: (a) first impressions, (b) profile photos, (c) ai-assisted self-presentation.
4) Risk: any compliance/claims risk?

Return JSON exactly:
{
  "relevance_score": 0-10,
  "virality_score": 0-10,
  "freshness_days": integer,
  "angles": ["...", "..."],
  "risk_flags": ["none" | "medical claim" | "copyright" | "privacy" | "unverified benchmark"],
  "one_line_take": "12–18 word hook",
  "keywords": ["3–6 seo/hashtag terms"]
}
```

### B) quality filter (boolean gate)

**rule:** pass only if:

* `relevance_score >= 7`
* `virality_score >= 6`
* `freshness_days <= 21` (unless evergreen keyword present: “guide”, “how to”, “checklist” → allow)

**optional extra:** down-weight items with `risk_flags != "none"` unless angle explicitly avoids risk.

### C) content AI — social post generator

**purpose:** turn a passed item into linkedin & x posts (different lengths), optionally a blog draft.

**system prompt**

> you are the voice of brightface.ai. tone: confident, modern, helpful, lightly playful. avoid hype. connect ideas to personal branding and first impressions. never fabricate facts; cite only what’s provided.

**user prompt (inputs: `{title}`, `{summary}`, `{angles}`, `{one_line_take}`, `{url}`, `{source}`, `{keywords}`)**
output strict json with 3 variants:

```
Context:
Title: {title}
Source: {source}
Summary: {summary}
Angle(s): {angles}
Hook: {one_line_take}
URL: {url}

Brand rules:
- Mention how great first impressions + profile photos drive outcomes.
- Include CTA: "Try Brightface to upgrade your profile photo" with link https://brightface.ai/?utm_source={platform}&utm_campaign=autopost&utm_medium=social
- Use 2–4 tasteful hashtags from {keywords} + #AIHeadshots #PersonalBranding
- No emojis at start of sentences; 0–2 total is fine.

Produce JSON exactly:
{
  "linkedin": {
    "text": "120–220 words, 2–3 short paragraphs, 1 bullet list if natural. End with CTA + link.",
    "hashtags": ["#...", "#..."]
  },
  "x": {
    "text": "230–260 chars, 1 sentence hook + 1 insight + CTA + link",
    "hashtags": ["#...", "#..."]
  },
  "blog": {
    "title": "SEO title <= 60 chars including 'AI headshots' or 'personal branding' when relevant",
    "slug": "kebab-case",
    "meta_description": "140–160 chars",
    "outline": ["H2 ...", "H2 ...", "H2 ..."],
    "body_md": "600–900 words markdown. Include a short intro, 3–5 H2s, one checklist, and a soft CTA section linking to brightface.ai. Insert the source URL once in 'Further reading'. No invented stats."
  }
}
```

### D) quality filter 2 (safety + polish)

**reject if any true:**

* contains “study shows”/specific statistics not in the input.
* more than 4 hashtags (linkedin) or >2 hashtags (x).
* missing CTA link with utm params.
* sensitive/medical/identity claims.

### E) archive / review prompts (optional)

* **“new for review”**: if borderline (relevance 6–6.9 or risk flag set), write a 1-sentence reason: *“Held for review: {reason}”* plus the proposed copy.

---

## 2) implementation spec for dev team

### stack & integrations

* **automation runner:** Make.com (or n8n/zapier flows—naming below is generic)
* **llm:** openai gpt-5 (chat/completions)
* **datasources:** rss feeds (see below)
* **storage/ops:** google sheets (content ledger) + optional notion cms
* **publishers:** linkedin company page (brightface) + x (twitter)

### env variables (vaulted)

```
OPENAI_API_KEY=
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
LINKEDIN_PAGE_ID=            # Brightface company page
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=
GOOGLE_SHEETS_ID=            # "Brightface Content Ledger"
NOTION_API_KEY=              # if using Notion for blog drafts
NOTION_DB_ID=                # blog posts database
DEFAULT_UTM_CAMPAIGN=autopost
```

### rss sources (initial set)

* OpenAI Blog RSS
* Google AI Blog RSS
* Product Hunt “AI” RSS
* VentureBeat AI RSS
* TechCrunch AI RSS
* Adobe blog (Firefly / creative) RSS
* LinkedIn Engineering / Creator blog RSS
* *Add your own: “personal branding”, “photography business”, “linkedin profile tips” curated lists*

### data schema

**google sheet: `content_ledger`**

| date_iso | platform | status | title | source | url | relevance | virality | risk | post_text | hashtags | blog_slug | reviewer | posted_at | post_url | clicks | likes | reposts | comments |
| -------- | -------- | ------ | ----- | ------ | --- | --------- | -------- | ---- | --------- | -------- | --------- | -------- | --------- | -------- | ------ | ----- | ------- | -------- |

**notion database (optional)**

* `Title` (title)
* `Slug` (text)
* `Status` (select: Draft/Ready/Published/Held)
* `SEO Description` (text)
* `Body` (rich text/markdown)
* `Source URL` (url)
* `Author` (people) default “Brightface AI”
* `Tags` (multi-select: AI Headshots, Personal Branding, LinkedIn, Photography, Tools)

### flow logic (mapped to your screenshot)

1. **RSS Trigger** (every 60–120 mins)
   → fetch new items, de-dupe by URL hash (store `seen_urls` in sheet or KV).

2. **Scoring AI**
   → send `{title, summary/full_text, source, url}` to prompt A
   → parse json; log to `content_ledger`.

3. **Code: gating & formatting**

   * reject if `freshness_days > 21` (unless evergreen terms)
   * attach `angles`, `keywords`, `one_line_take`.

4. **Quality Filter**

   * pass if `relevance >= 7 && virality >= 6`

5. **Content AI**
   → prompt C; receive `{linkedin, x, blog}` json.

6. **Quality Filter 2**

   * run regex checks for banned phrases, link+utm presence, hashtag counts.

7. **Branching**

   * **true (green path):**

     * **Store Content** in sheet (+ planned publish time)
     * **Code:** add UTM `?utm_source=linkedin|x&utm_campaign=${DEFAULT_UTM_CAMPAIGN}&utm_medium=social`
     * **Post to X** immediately or queue (tweet endpoint)
     * **Post to LinkedIn** immediately or queue (UGC post endpoint)
     * **Optional:** Create Notion draft using `blog` object
   * **false (red path):**

     * Append to **New for Review** sheet or Notion with “reason”
     * If hard fail (safety), append to **Archive** with reason

### scheduling & cadence

* **social:** 1–2 posts/day/platform, randomize between 08:30–10:00 and 15:30–17:00 UK time.
* **blog:** 2 long-form drafts/week (Mon/Thu 11:00). Manual review before publish.

### review mode toggle

* env: `AUTO_POST=true|false`

  * `false`: write to “New for Review” only (with one-click approve webhook to post)
  * `true`: post immediately + log.

### api notes

**linkedin** (v2):

* endpoint: `POST /ugcPosts` with organization `LINKEDIN_PAGE_ID`
* include `lifecycleState: "PUBLISHED"`, `specificContent.ugcShareContent.shareCommentary.text`
* include link in text (linkedin auto-previews)

**x (twitter)**:

* endpoint: v2 create tweet
* include full `text` (shortened link + hashtags)

**notion**: `POST /v1/pages` with `parent.database_id = NOTION_DB_ID` and properties per schema.

**openai**: chat completions (`gpt-5`) with `response_format=json`.

### error handling & retries

* catch non-200s → retry (exponential backoff: 1s, 5s, 20s).
* if linkedin/x rate limit → queue in sheet `status=queued` with `next_attempt_at`.
* if json parse fails → send original LLM string to “Held for Review” with label `LLM_FORMAT_ERROR`.

### analytics

* append published `post_url` back into sheet.
* nightly job pulls engagement metrics (likes, comments, reposts) via APIs → update sheet.
* optional bitly or gA4 → capture clicks for each UTM.

### governance & brand rules

* voice: helpful, specific, never smug. 0–2 emojis total max.
* avoid: medical/psych claims, face-recognition/security claims, celebrity use, “perfect”/“flawless” language.
* always: link to **[https://brightface.ai/](https://brightface.ai/)** with UTM, invite to “Try Brightface to upgrade your profile photo”.

---

## 3) developer tasks checklist

1. **repos & config**

   * create `brightface-content-engine` project (Make.com or n8n).
   * add env vars listed above; set `AUTO_POST=false` for first week.

2. **datasource setup**

   * add RSS modules; implement de-dupe by url hash.
   * maintain allowlist of domains in a small KV (json).

3. **llm nodes**

   * implement **Scoring AI** (prompt A).
   * implement **Content AI** (prompt C).
   * enforce `response_format=json` + strict parsing with schema validation.

4. **filters & code nodes**

   * implement Quality Filter rules + regex guards.
   * add UTM params and shortlink if using bitly.

5. **storage**

   * create Google Sheet with `content_ledger` columns above.
   * optional: Notion DB for blog.

6. **publishers**

   * wire **LinkedIn** and **X** posting with queue/retry.
   * implement “review mode” toggle & approve-via-webhook (button → webhook → posts & updates sheet).

7. **observability**

   * log each step to sheet (status, reason).
   * daily metrics pull cron; calculate CTR/ERP in a “metrics” tab.

8. **QA**

   * run in `AUTO_POST=false` for 5 days.
   * sample 20 items → expect ≥70% pass to “review”, ≤5% safety rejections.
   * check that all posts contain link+utm and hashtag limits.

---

## 4) example outputs (sanity)

**linkedin (sample length + structure)**

> first impressions aren’t just visual — they’re *contextual*. new {source} piece shows how ai tools are reshaping online credibility.
>
> key takeaways:
> • consistent profile photo boosts recognition across channels
> • authentic lighting and framing build trust faster than heavy filters
> • small content rituals (weekly posts, updated headline) compound
>
> brightface uses ai to craft natural, professional headshots that fit your brand. try it: [https://brightface.ai/?utm_source=linkedin&utm_campaign=autopost&utm_medium=social](https://brightface.ai/?utm_source=linkedin&utm_campaign=autopost&utm_medium=social)
> #AIHeadshots #PersonalBranding #CreatorTools

**x**

> your profile photo is the “handshake” of the internet. keep it clear, current, consistent — and you’ll convert more views into opportunities. try brightface: [https://brightface.ai/?utm_source=twitter&utm_campaign=autopost&utm_medium=social](https://brightface.ai/?utm_source=twitter&utm_campaign=autopost&utm_medium=social) #AIHeadshots #PersonalBranding

---

## 5) backlog & nice-to-haves

* caption A/B tests per platform (two variants in queue).
* image generator: auto-create 1200×630 OG image for blog using brand template (title overlay).
* “evergreen booster”: recycle top 10% posts after 60–90 days with refreshed hook.
* multilingual expansion (en → de/es fr on request).

