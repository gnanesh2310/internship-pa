# 🤖 Internship PA — Gnanesh's Personal AI Internship Assistant

An autonomous system that scrapes internship listings, writes personalised emails using AI, and sends them daily on autopilot — while keeping you in the loop via Telegram.

---

## 📁 Project Structure

```
internship-pa/
├── dashboard/          ← Next.js frontend (deploy on Vercel)
├── backend/            ← Python backend (deploy on Railway)
└── supabase/           ← SQL schema
```

---

## 🚀 Setup Guide (Full)

### Step 1 — Supabase Database

1. Go to [supabase.com](https://supabase.com) → New Project
2. Open **SQL Editor** → paste the entire contents of `supabase/schema.sql` → Click **Run**
3. Go to **Settings → API**, copy:
   - `Project URL` → `NEXT_PUBLIC_SUPABASE_URL`
   - `anon public` key → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `service_role` key → `SUPABASE_SERVICE_KEY` (backend only)

---

### Step 2 — Gmail OAuth (One-time)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project → Enable **Gmail API** + **Google Sheets API**
3. Go to **Credentials → Create → OAuth 2.0 Client ID → Desktop App**
4. Download the client ID and secret
5. Run the OAuth setup script locally:
   ```bash
   cd backend
   pip install google-auth-oauthlib
   python sender/oauth_setup.py
   ```
6. Log in with both Gmail accounts when prompted
7. Copy the printed refresh tokens into your `.env`

---

### Step 3 — Telegram Bot

1. Open Telegram → search `@BotFather`
2. Send `/newbot` → follow prompts → copy your **Bot Token**
3. Start a chat with your new bot
4. Get your Chat ID: visit `https://api.telegram.org/bot<TOKEN>/getUpdates` after sending `/start`
5. Your Chat ID is already set to `8394802242` in the code

---

### Step 4 — AI API Keys (all free tiers)

| Provider | Get Key | Free Limit |
|---|---|---|
| Gemini 1.5 Flash | [aistudio.google.com](https://aistudio.google.com) | 1M tokens/day |
| Groq | [console.groq.com](https://console.groq.com) | 14.4k tokens/min |
| OpenRouter | [openrouter.ai](https://openrouter.ai) | Free models available |
| Together AI | [api.together.xyz](https://api.together.xyz) | $1 free credit |

---

### Step 5 — Google Sheets (optional)

1. Create a new Google Sheet
2. Copy the Sheet ID from the URL: `docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit`
3. Create a service account in Google Cloud Console → download JSON
4. Share your sheet with the service account email

---

### Step 6 — Deploy Dashboard (Vercel)

```bash
cd dashboard
cp .env.local.example .env.local
# Fill in your Supabase URL and anon key
```

1. Push `dashboard/` to GitHub
2. Go to [vercel.com](https://vercel.com) → New Project → Import repo
3. Add environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. Click **Deploy**

Your dashboard will be live at `yourapp.vercel.app`

---

### Step 7 — Deploy Backend (Railway)

```bash
cd backend
cp .env.example .env
# Fill in ALL environment variables
```

1. Push `backend/` to GitHub (separate repo or subfolder)
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add ALL environment variables from `backend/.env.example`
4. Railway will detect the `Procfile` and start the worker

**To test immediately:**
```bash
cd backend
pip install -r requirements.txt
python main.py --now
```

---

## ⚙️ How It Works

```
9:00 AM IST daily:
  1. Telegram morning report
  2. Scrape Internshala + LinkedIn + Naukri + Wellfound
  3. Classify each job (GREEN/YELLOW/RED)
  4. GREEN → AI writes email → Gmail sends it
  5. RED → Added to manual queue → Telegram alert
  6. Scrape IIT/NIT professors
  7. Email relevant professors
  8. Send 7-day follow-ups
  9. Sync Google Sheets
  10. Telegram end-of-day summary

6:00 PM IST daily:
  - Second follow-up check
```

---

## 🎛️ Dashboard Pages

| Page | URL | Purpose |
|---|---|---|
| Home | `/` | Stats, activity feed, PA status |
| Applications | `/applications` | Full table, filters, CSV export |
| Manual Queue | `/manual-queue` | Cards for govt portals needing manual apply |
| Profile | `/profile` | Edit your info, skills, resume text |
| Settings | `/settings` | Daily limits, toggles, Telegram test |
| Status | `/status` | Public quick-check page (no login) |

---

## 📱 Telegram Alerts

You'll get:
- 🌅 Morning report every day
- ✅ Notification for every email sent
- 🔴 Instant alert for manual applications needed
- 📬 Alert when someone replies
- 🔄 Follow-up notifications
- ⚠️ Error alerts if something breaks
- 🌙 End-of-day summary

---

## 🔧 Environment Variables

### Dashboard (`dashboard/.env.local`)
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=8394802242
```

### Backend (`backend/.env`)
```
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
GEMINI_API_KEY=
GROQ_API_KEY=
OPENROUTER_API_KEY=
TOGETHER_API_KEY=
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
GMAIL_COMPANY_REFRESH_TOKEN=
GMAIL_RESEARCH_REFRESH_TOKEN=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=8394802242
GOOGLE_SHEETS_ID=
GOOGLE_SHEETS_CREDENTIALS_JSON=service_account.json
```

---

## 🆓 Running Costs

Everything uses free tiers:
- **Supabase**: Free (500MB, 50k rows)
- **Vercel**: Free (hobby plan)
- **Railway**: ~$5/month for the worker (or use free $5 credit)
- **Gemini**: Free (1M tokens/day)
- **Groq/OpenRouter**: Free fallbacks
- **Gmail**: Free
- **Google Sheets**: Free

**Total: ~$0–5/month**

---

## ⚠️ Important Notes

1. **Email limits**: Start at 5/day and ramp up to avoid Gmail spam detection
2. **Random delays**: 4–6 minutes between emails to look human
3. **Manual queue**: Check Telegram daily for RED alerts — these are time-sensitive
4. **CGPA 6.69**: The AI is instructed to not foreground CGPA — it leads with skills and projects
5. **Follow-ups**: Sent exactly 7 days after original email, only if no reply

---

## 🐛 Troubleshooting

**Gmail OAuth error**: Re-run `sender/oauth_setup.py` to get fresh tokens

**Gemini quota exceeded**: PA auto-switches to Groq → OpenRouter → Together

**Scraper blocked**: Add delays, rotate User-Agent, or use a proxy

**Railway not running**: Check logs in Railway dashboard — most issues are missing env vars
