# Streamlit Dashboard — AI Job Lead Intelligence System (Multi-Provider)
import streamlit as st
import pandas as pd
import requests
import json
import time

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="AI Job Lead Intelligence System",
    layout="wide",
    page_icon="🎯"
)

st.title("🎯 AI Job Lead Intelligence Dashboard")
st.markdown("Enter your dream role and companies — AI will suggest the right search keywords and scoring weights automatically.")

# =========================================
# SIDEBAR — API KEYS + SETTINGS
# =========================================
st.sidebar.header("🔑 Serper API Key")
serper_api_key = st.sidebar.text_input(
    "Serper API Key",
    type="password",
    placeholder="From serper.dev",
    help="Used for Google search. 2,500 free searches/month."
)
st.sidebar.markdown("👉 [Get free Serper key](https://serper.dev)")

st.sidebar.divider()

st.sidebar.header("🤖 AI Provider (for keyword suggestions)")

ai_provider = st.sidebar.selectbox(
    "Choose AI Provider",
    options=["Gemini (Free)", "OpenAI", "Anthropic (Claude)", "DeepSeek", "Groq (Free)"],
    help="All are supported. Gemini and Groq have a completely free tier."
)

# Show the right API key input + help link per provider
provider_links = {
    "Gemini (Free)":       ("Gemini API Key",   "From aistudio.google.com — free, no credit card",   "https://aistudio.google.com/app/apikey"),
    "OpenAI":              ("OpenAI API Key",    "From platform.openai.com — $5 free trial credits",  "https://platform.openai.com/api-keys"),
    "Anthropic (Claude)":  ("Anthropic API Key", "From console.anthropic.com — $5 free trial credits","https://console.anthropic.com"),
    "DeepSeek":            ("DeepSeek API Key",  "From platform.deepseek.com — very cheap/free tier", "https://platform.deepseek.com"),
    "Groq (Free)":         ("Groq API Key",      "From console.groq.com — free, no credit card",      "https://console.groq.com"),
}

label, help_text, link = provider_links[ai_provider]
ai_api_key = st.sidebar.text_input(label, type="password", placeholder=help_text)
st.sidebar.markdown(f"👉 [Get key here]({link})")

st.sidebar.divider()
st.sidebar.header("⚙️ Search Settings")
num_results = st.sidebar.slider("Results Per Search", min_value=3, max_value=10, value=5)
sleep_time  = st.sidebar.slider("Delay Between Requests (sec)", min_value=1, max_value=5, value=2)

# =========================================
# AI CALL — UNIVERSAL WRAPPER
# =========================================
def call_ai(prompt, provider, api_key):
    """
    Unified AI caller. Returns raw text response or raises Exception.
    """
    try:
        # ---- Gemini ----
        if provider == "Gemini (Free)":
            models_to_try = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
            last_error = None
            for model in models_to_try:
                url  = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                body = {"contents": [{"parts": [{"text": prompt}]}]}
                r    = requests.post(url, params={"key": api_key}, json=body, timeout=30)
                if r.status_code == 400:
                    raise Exception("Invalid Gemini API key. Please check and re-enter it.")
                if r.status_code == 404:
                    last_error = f"{model} not found, trying next..."
                    continue
                if r.status_code == 429:
                    last_error = f"Rate limited on {model}"
                    time.sleep(3)
                    continue
                r.raise_for_status()
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            raise Exception(f"Gemini error: {last_error}. Try Groq instead — it's also free.")

        # ---- OpenAI ----
        elif provider == "OpenAI":
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            body = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000}
            r = requests.post(url, headers=headers, json=body, timeout=30)
            if r.status_code == 401:
                raise Exception("Invalid OpenAI API key.")
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]

        # ---- Anthropic ----
        elif provider == "Anthropic (Claude)":
            url = "https://api.anthropic.com/v1/messages"
            headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
            body = {"model": "claude-haiku-20240307", "max_tokens": 1000, "messages": [{"role": "user", "content": prompt}]}
            r = requests.post(url, headers=headers, json=body, timeout=30)
            if r.status_code == 401:
                raise Exception("Invalid Anthropic API key.")
            r.raise_for_status()
            return r.json()["content"][0]["text"]

        # ---- DeepSeek ----
        elif provider == "DeepSeek":
            url = "https://api.deepseek.com/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            body = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000}
            r = requests.post(url, headers=headers, json=body, timeout=30)
            if r.status_code == 401:
                raise Exception("Invalid DeepSeek API key.")
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]

        # ---- Groq ----
        elif provider == "Groq (Free)":
            url     = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            models_to_try = ["llama-3.1-8b-instant", "llama3-70b-8192", "mixtral-8x7b-32768"]
            for model in models_to_try:
                body = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000}
                r    = requests.post(url, headers=headers, json=body, timeout=30)
                if r.status_code == 401:
                    raise Exception("Invalid Groq API key.")
                if r.status_code == 400:
                    continue
                if r.status_code == 429:
                    time.sleep(3)
                    continue
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"]
            raise Exception("No Groq models available right now. Try again in a moment.")

    except Exception as e:
        raise Exception(str(e))

# =========================================
# MAIN INPUTS
# =========================================
col_a, col_b = st.columns(2)

with col_a:
    companies_text = st.text_area(
        "🏢 Dream Companies (one per line)",
        height=160,
        placeholder="Google\nAmazon\nFlipkart"
    )

with col_b:
    dream_role = st.text_input(
        "💼 Dream Role",
        placeholder="e.g. Data Scientist, Marketing Manager, SWE"
    )
    target_location = st.text_input(
        "📍 Target Location",
        value="Bengaluru",
        help="City to filter leads by"
    )
    alumni_input = st.text_area(
        "🎓 Alumni Keywords (one per line)",
        value="IIT Bombay\nIIT B\nMSU Baroda",
        height=80,
        help="Matched against LinkedIn titles/snippets"
    )

alumni_keywords = [k.strip() for k in alumni_input.split('\n') if k.strip()]

# =========================================
# STEP 1 — AI SUGGEST
# =========================================
st.divider()
st.subheader("Step 1 — Auto-suggest keywords for your role")

if "role_config" not in st.session_state:
    st.session_state.role_config = None

if st.button("✨ Auto-suggest Skills & Search Keywords", type="secondary"):

    if not ai_api_key.strip():
        st.error(f"Please enter your {label} in the sidebar.")
        st.stop()

    if not dream_role.strip():
        st.warning("Please enter your dream role first.")
        st.stop()

    prompt = f"""You are a job search expert. A user wants to find LinkedIn contacts to help them get a job as: "{dream_role}"

Return ONLY a valid JSON object (no markdown, no explanation, no backticks) with these exact keys:

{{
  "skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
  "manager_titles": ["title1", "title2", "title3"],
  "recruiter_keywords": ["keyword1", "keyword2", "keyword3"],
  "skill_score": 3,
  "manager_score": 5,
  "hr_score": 3,
  "alumni_score": 5,
  "location_score": 4,
  "search_summary": "One sentence describing the search strategy for this role."
}}

Rules:
- skills: 5 most important technical/domain skills for this role
- manager_titles: exact LinkedIn titles of people who would hire for this role
- recruiter_keywords: domain words a recruiter for this role would have in their profile
- skill_score: how much a skill keyword match should add to lead score (1-5)
- manager_score: score weight for hiring manager leads (1-10)
- hr_score: score weight for HR/recruiter leads (1-10)
- alumni_score: score weight for alumni leads (1-10)
- location_score: score weight for location match (1-10)
Return ONLY the JSON. No extra text."""

    with st.spinner(f"Asking {ai_provider} about '{dream_role}' roles..."):
        try:
            raw = call_ai(prompt, ai_provider, ai_api_key)

            # Strip markdown fences if model added them anyway
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            st.session_state.role_config = json.loads(raw)
            st.success(f"✅ Suggestions loaded from {ai_provider}! Review and edit below.")

        except json.JSONDecodeError:
            st.error("AI returned invalid JSON. Try again — it sometimes happens on the first attempt.")
            st.stop()
        except Exception as e:
            st.error(f"❌ API error: {e}")
            st.stop()

# =========================================
# STEP 2 — SHOW + EDIT SUGGESTIONS
# =========================================
if st.session_state.role_config:
    cfg = st.session_state.role_config

    st.info(f"**Search strategy:** {cfg.get('search_summary', '')}")

    col1, col2, col3 = st.columns(3)

    with col1:
        skills_text = st.text_area(
            "🛠 Skills to match (one per line)",
            value="\n".join(cfg.get("skills", [])),
            height=140
        )
    with col2:
        manager_titles_text = st.text_area(
            "👔 Hiring Manager Titles (one per line)",
            value="\n".join(cfg.get("manager_titles", [])),
            height=140
        )
    with col3:
        recruiter_kw_text = st.text_area(
            "📋 Recruiter Keywords (one per line)",
            value="\n".join(cfg.get("recruiter_keywords", [])),
            height=140
        )

    st.markdown("**Score Weights** (edit if needed)")
    wc1, wc2, wc3, wc4, wc5 = st.columns(5)
    w_skill    = wc1.number_input("Skill Match",    min_value=0, max_value=10, value=int(cfg.get("skill_score",    3)))
    w_manager  = wc2.number_input("Hiring Manager", min_value=0, max_value=10, value=int(cfg.get("manager_score",  5)))
    w_hr       = wc3.number_input("HR/Recruiter",   min_value=0, max_value=10, value=int(cfg.get("hr_score",       3)))
    w_alumni   = wc4.number_input("Alumni",         min_value=0, max_value=10, value=int(cfg.get("alumni_score",   5)))
    w_location = wc5.number_input("Location",       min_value=0, max_value=10, value=int(cfg.get("location_score", 4)))

    skills_list        = [s.strip() for s in skills_text.split('\n')         if s.strip()]
    manager_titles     = [s.strip() for s in manager_titles_text.split('\n') if s.strip()]
    recruiter_keywords = [s.strip() for s in recruiter_kw_text.split('\n')   if s.strip()]

    # =========================================
    # SEARCH TEMPLATES
    # =========================================
    # =========================================
    # LOCATION KEYWORD EXPANDER
    # =========================================
    # Maps city → [aliases, state, country] for flexible matching
    LOCATION_MAP = {
        "bengaluru":  ["bengaluru", "bangalore", "karnataka", "india"],
        "bangalore":  ["bengaluru", "bangalore", "karnataka", "india"],
        "mumbai":     ["mumbai", "bombay", "maharashtra", "india"],
        "delhi":      ["delhi", "new delhi", "ncr", "india"],
        "hyderabad":  ["hyderabad", "telangana", "andhra", "india"],
        "chennai":    ["chennai", "madras", "tamil nadu", "india"],
        "pune":       ["pune", "maharashtra", "india"],
        "kolkata":    ["kolkata", "calcutta", "west bengal", "india"],
        "ahmedabad":  ["ahmedabad", "gujarat", "india"],
        "noida":      ["noida", "ncr", "uttar pradesh", "india"],
        "gurugram":   ["gurugram", "gurgaon", "haryana", "ncr", "india"],
        "gurgaon":    ["gurugram", "gurgaon", "haryana", "ncr", "india"],
        "india":      ["india"],
    }

    def get_location_keywords(location):
        key = location.strip().lower()
        if key in LOCATION_MAP:
            return LOCATION_MAP[key]
        # fallback: just use the city itself + india
        return [key, "india"]

    location_keywords = get_location_keywords(target_location)

    def location_matches(text):
        t = text.lower()
        return any(kw in t for kw in location_keywords)

    def build_search_templates():
        mgr_or   = " OR ".join([f'"{t}"' for t in manager_titles])
        rec_or   = " OR ".join([f'"{k}"' for k in recruiter_keywords])
        alum_or  = " OR ".join([f'"{k}"' for k in alumni_keywords])
        skill_or = " OR ".join([f'"{s}"' for s in skills_list[:3]])
        return {
            "Hiring Manager": 'site:linkedin.com/in (' + mgr_or  + ') "{company}"',
            "HR / Recruiter": 'site:linkedin.com/in ("Recruiter" OR "Talent Acquisition" OR "HR") (' + rec_or + ') "{company}"',
            "Alumni":         'site:linkedin.com/in (' + alum_or + ') "{company}"',
            "Skills Match":   'site:linkedin.com/in (' + skill_or + ') "{company}"',
            "Location":       'site:linkedin.com/in ("' + target_location + '") "{company}"',
        }

    # =========================================
    # LEAD SCORING
    # =========================================
    def calculate_score(category, title, snippet):
        score = 0
        text  = (title + " " + snippet).lower()
        if category == "Hiring Manager":
            score += w_manager
        elif category == "HR / Recruiter":
            score += w_hr
        skill_hits = sum(1 for s in skills_list if s.lower() in text)
        score += skill_hits * w_skill
        if any(k.lower() in text for k in alumni_keywords):
            score += w_alumni
        if location_matches(text):
            score += w_location
        for word in ['Head', 'Director', 'Lead', 'Manager', 'Principal', 'VP', 'Chief']:
            if word.lower() in text:
                score += 3
                break
        return score


    # =========================================
    # CURRENT STATUS DETECTION
    # =========================================
    def detect_current_status(company, title, snippet):
        import re
        text = (title + " " + snippet).lower()
        comp = company.lower()
        past_signals = ["formerly", "previously", "ex-", "past experience",
                        "used to work", "worked at", "left ", "moved on"]
        year_range   = re.search(r"20\d\d\s*[-–]\s*20\d\d", text)
        current_signals = [f"at {comp}", f"@ {comp}", f"| {comp}", "present", "current"]
        past_hit    = any(p in text for p in past_signals) or bool(year_range)
        current_hit = any(c in text for c in current_signals)
        if current_hit and not past_hit:
            return "Likely Current"
        elif past_hit and not current_hit:
            return "Possibly Past"
        else:
            return "Check Profile"
    # =========================================
    # GOOGLE SEARCH
    # =========================================
    def google_search(query, num_results=5):
        try:
            r = requests.post(
                "https://google.serper.dev/search",
                json={"q": query, "num": num_results},
                headers={"X-API-KEY": serper_api_key, "Content-Type": "application/json"},
                timeout=10
            )
            if r.status_code == 401:
                st.error("❌ Invalid Serper API key.")
                st.stop()
            if r.status_code != 200:
                st.warning(f"Serper error {r.status_code}: {r.text}")
                return []
            return r.json().get("organic", [])
        except requests.exceptions.RequestException as e:
            st.warning(f"Network error: {e}")
            return []

    # =========================================
    # STEP 3 — RUN SEARCH
    # =========================================
    st.divider()
    st.subheader("Step 2 — Run the lead search")

    # initialise results store
    if "results_df" not in st.session_state:
        st.session_state.results_df = None

    if st.button("🚀 Start Lead Search", type="primary"):

        if not serper_api_key.strip():
            st.error("Please enter your Serper API key in the sidebar.")
            st.stop()

        if not companies_text.strip():
            st.warning("Please enter at least one company name.")
            st.stop()

        companies        = [c.strip() for c in companies_text.split('\n') if c.strip()]
        search_templates = build_search_templates()
        all_results      = []
        progress_bar     = st.progress(0)
        status_text      = st.empty()
        total_searches   = len(companies) * len(search_templates)
        current_search   = 0

        for company in companies:
            status_text.text(f"🔍 Searching: {company}...")
            for category, template in search_templates.items():
                query   = template.format(company=company)
                results = google_search(query, num_results)

                for item in results:
                    title   = item.get('title',   '')
                    link    = item.get('link',    '')
                    snippet = item.get('snippet', '')

                    parts         = title.split(' - ')
                    probable_name = parts[0].strip() if parts else title
                    probable_role = parts[1].strip() if len(parts) > 1 else ""

                    alumni_flag    = "Yes" if any(k.lower() in (title + snippet).lower() for k in alumni_keywords) else "No"
                    location_flag  = "Yes" if location_matches(title + " " + snippet) else "No"
                    matched_skills = [s for s in skills_list if s.lower() in (title + " " + snippet).lower()]
                    current_status = detect_current_status(company, title, snippet)
                    score          = calculate_score(category, title, snippet)

                    if current_status == "Possibly Past":
                        score -= 8
                    elif current_status == "Check Profile":
                        score -= 3

                    all_results.append({
                        'Company':        company,
                        'Category':       category,
                        'Name':           probable_name,
                        'Role':           probable_role,
                        'Current Status': current_status,
                        'Matched Skills': ", ".join(matched_skills),
                        'Alumni Match':   alumni_flag,
                        'Location Match': location_flag,
                        'Lead Score':     score,
                        'LinkedIn URL':   link,
                        'Snippet':        snippet
                    })

                current_search += 1
                progress_bar.progress(current_search / total_searches)
                time.sleep(sleep_time)

        status_text.text("✅ Search complete!")

        if not all_results:
            st.warning("No leads found. Try different companies or check your API key.")
            st.stop()

        results_df = pd.DataFrame(all_results)
        results_df.drop_duplicates(subset=['LinkedIn URL'], inplace=True)
        results_df.sort_values(by='Lead Score', ascending=False, inplace=True)

        # Save to session state so filters don't re-trigger the search
        st.session_state.results_df = results_df

    # ---- Show results if we have them (persists across filter changes) ----
    if st.session_state.results_df is not None:
        results_df = st.session_state.results_df

        st.success(f"✅ Found **{len(results_df)}** unique leads — use filters below")

        # Filters
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            selected_category = st.multiselect(
                "Filter by Category",
                options=results_df['Category'].unique().tolist(),
                default=results_df['Category'].unique().tolist()
            )
        with fc2:
            status_filter = st.selectbox(
                "Current Status Filter",
                options=['Current + Check Profile', 'Likely Current Only', 'All', 'Possibly Past Only'],
                index=0,
                help="Default shows Likely Current + Check Profile, hiding only confirmed past employees"
            )
        with fc3:
            alumni_filter = st.selectbox("Alumni Filter", ['All', 'Alumni Only'])
        with fc4:
            location_filter = st.selectbox("Location Filter", ['All', f'{target_location} Only'])

        filtered_df = results_df[results_df['Category'].isin(selected_category)].copy()

        if status_filter == 'Current + Check Profile':
            filtered_df = filtered_df[filtered_df['Current Status'].isin(['Likely Current', 'Check Profile'])]
        elif status_filter == 'Likely Current Only':
            filtered_df = filtered_df[filtered_df['Current Status'] == 'Likely Current']
        elif status_filter == 'Possibly Past Only':
            filtered_df = filtered_df[filtered_df['Current Status'] == 'Possibly Past']

        if alumni_filter == 'Alumni Only':
            filtered_df = filtered_df[filtered_df['Alumni Match'] == 'Yes']
        if location_filter != 'All':
            filtered_df = filtered_df[filtered_df['Location Match'] == 'Yes']

        # Metrics
        st.subheader("📊 Lead Metrics")
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Total Leads",      len(filtered_df))
        m2.metric("✅ Likely Current", len(results_df[results_df['Current Status'] == 'Likely Current']))
        m3.metric("⚠️ Check Profile", len(results_df[results_df['Current Status'] == 'Check Profile']))
        m4.metric("❌ Possibly Past",  len(results_df[results_df['Current Status'] == 'Possibly Past']))
        m5.metric("Alumni Matches",   len(filtered_df[filtered_df['Alumni Match']  == 'Yes']))
        m6.metric(f"{target_location} Leads", len(filtered_df[filtered_df['Location Match'] == 'Yes']))

        st.dataframe(filtered_df, use_container_width=True)

        st.download_button(
            label="⬇️ Download CSV",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name="lead_results.csv",
            mime="text/csv"
        )

else:
    st.info("👆 Enter your dream role above and click **Auto-suggest** to get started.")