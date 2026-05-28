# 🎯 AI Job Lead Intelligence Dashboard

A Streamlit app that finds **HRs, Hiring Managers, Alumni, and Skill-matched leads** on LinkedIn for your dream companies — powered by Google Search and AI-generated role-aware keywords.

---

## 🚀 Live Demo

> Deploy your own free instance on [Streamlit Community Cloud](https://share.streamlit.io) — see setup below.

---

## ✨ What It Does

You enter your **dream role** (e.g. `Data Scientist`) and **dream companies** (e.g. `Google, Flipkart`) — the app does the rest:

1. **AI suggests keywords** — calls your chosen AI provider to generate role-specific skills, hiring manager titles, and recruiter keywords automatically
2. **Runs 5 targeted LinkedIn searches** per company via Google (Serper API):
   - Hiring Managers with role-specific titles
   - HR / Recruiters with domain keywords
   - Alumni from your college
   - Skills-matched profiles
   - Location-filtered leads
3. **Scores every lead** based on role relevance, skill matches, seniority, alumni, and location
4. **Filters out past employees** — detects if someone has left the company using snippet signals and year ranges
5. **Flexible location matching** — `Bengaluru` also matches `Bangalore`, `Karnataka`; `Hyderabad` matches `Telangana`, etc.

---

## 🔑 API Keys Required

All keys are entered by the user in the sidebar — nothing is hardcoded or stored.

| API | Purpose | Free Tier |
|-----|---------|-----------|
| [Serper](https://serper.dev) | Google Search | 2,500 searches/month free |
| [Groq](https://console.groq.com) | AI keyword suggestions | Free, no credit card |
| [Gemini](https://aistudio.google.com/app/apikey) | AI keyword suggestions | Free, no credit card |
| [OpenAI](https://platform.openai.com/api-keys) | AI keyword suggestions | $5 trial credits |
| [Anthropic](https://console.anthropic.com) | AI keyword suggestions | $5 trial credits |
| [DeepSeek](https://platform.deepseek.com) | AI keyword suggestions | Free/cheap tier |

> **Recommendation for first-time users:** Use **Groq** (completely free, no credit card, works instantly).

---

## 🖥️ How to Use

### Step 1 — Enter API Keys
Paste your **Serper key** and choose an **AI provider + key** in the sidebar.

### Step 2 — Fill in Your Details
- **Dream Companies** — one per line (e.g. `Google`, `Amazon`, `Flipkart`)
- **Dream Role** — e.g. `Data Scientist`, `Marketing Manager`, `Backend Engineer`
- **Target Location** — e.g. `Bengaluru`, `Hyderabad`, `Mumbai`
- **Alumni Keywords** — your college names (e.g. `IIT Bombay`, `BITS Pilani`)

### Step 3 — Auto-suggest Keywords
Click **✨ Auto-suggest Skills & Search Keywords** — the AI fills in:
- Relevant skills for your role
- Hiring manager titles to target
- Recruiter domain keywords
- Scoring weights for each factor

Review and edit these before searching.

### Step 4 — Run the Search
Click **🚀 Start Lead Search** — results appear with filters for:
- **Current Status** — `Likely Current`, `Check Profile`, `Possibly Past`
- **Category** — Hiring Manager, HR/Recruiter, Alumni, Skills Match, Location
- **Alumni** and **Location** filters

### Step 5 — Download
Export filtered results as a **CSV** file.

---

## 📊 Lead Scoring

Each lead gets a score based on:

| Factor | Points |
|--------|--------|
| Hiring Manager title match | up to 10 (AI-suggested) |
| HR / Recruiter match | up to 10 (AI-suggested) |
| Skill keyword in profile | per skill × weight (AI-suggested) |
| Alumni keyword match | up to 10 (AI-suggested) |
| Location match | up to 10 (AI-suggested) |
| Seniority (Head/Director/VP etc.) | +3 bonus |
| Possibly Past employee | −8 penalty |
| Check Profile (unclear) | −3 penalty |

---

## 🗺️ Flexible Location Matching

Typing a city automatically expands to its aliases, state, and country:

| You type | Also matches |
|----------|-------------|
| Bengaluru | Bangalore, Karnataka, India |
| Hyderabad | Telangana, Andhra, India |
| Mumbai | Bombay, Maharashtra, India |
| Gurugram | Gurgaon, Haryana, NCR, India |
| Delhi | New Delhi, NCR, India |

---

## 🛠️ Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
pip install -r requirements.txt
streamlit run app.py
```

**requirements.txt**
```
streamlit
pandas
requests
```

---

## ☁️ Deploy on Streamlit Community Cloud (Free)

1. Push this repo to GitHub (must be **public**)
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **New app** → select your repo → set main file to `app.py`
4. Click **Deploy**

Your app gets a public URL instantly. Users bring their own API keys — no shared quota.

---

## ⚠️ Disclaimer

This tool uses Google Search to find publicly available LinkedIn profile URLs. It does not scrape LinkedIn directly. Always use leads responsibly and in accordance with LinkedIn's terms of service.

---

## 🤝 Contributing

PRs welcome! Some ideas for contributions:
- Add more city → alias mappings in `LOCATION_MAP`
- Add support for more AI providers
- Add email finding / outreach message generation

---

*Built with [Streamlit](https://streamlit.io) · Powered by [Serper](https://serper.dev)*
