# Streamlit Dashboard — AI Job Lead Intelligence System
import streamlit as st
import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv

# =========================================
# LOAD ENV
# =========================================
load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="AI Job Lead Intelligence System",
    layout="wide"
)

# =========================================
# TITLE
# =========================================
st.title("AI Job Lead Intelligence Dashboard")
st.markdown("Find HRs, Hiring Managers, and Alumni Leads using Google Search")

# =========================================
# SIDEBAR
# =========================================
st.sidebar.header("Search Settings")

num_results = st.sidebar.slider(
    "Results Per Search",
    min_value=3,
    max_value=10,
    value=5
)

sleep_time = st.sidebar.slider(
    "Delay Between Requests (seconds)",
    min_value=1,
    max_value=5,
    value=2
)

# =========================================
# INPUT
# =========================================
companies_text = st.text_area(
    "Enter Company Names (One Per Line)",
    height=250,
    placeholder="Amazon\nGoogle\nMicrosoft"
)

# =========================================
# SEARCH TEMPLATES
# =========================================
search_templates = {
    "HR": 'site:linkedin.com/in ("HR" OR "Recruiter" OR "Talent Acquisition") "{company}"',

    "Hiring Manager": 'site:linkedin.com/in ("AI Manager" OR "Engineering Manager" OR "Data Science Lead" OR "Bioinformatics Lead") "{company}"',

    "Alumni": 'site:linkedin.com/in ("IIT B" OR "IIT Bombay" OR "BTech" OR "MTech") "{company}"'
}

# =========================================
# GOOGLE SEARCH FUNCTION
# =========================================
def google_search(query, num_results=5):

    url = "https://google.serper.dev/search"

    payload = {
        "q": query,
        "num": num_results
    }

    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        st.error(f"API Error: {response.text}")
        return []

    data = response.json()

    return data.get("organic", [])

# =========================================
# LEAD SCORING
# =========================================
def calculate_score(category, role, alumni_flag):

    score = 0

    if category == "Hiring Manager":
        score += 5

    if category == "HR":
        score += 3

    if alumni_flag == "Yes":
        score += 5

    leadership_keywords = [
        'Head',
        'Director',
        'Lead',
        'Manager',
        'Principal'
    ]

    for word in leadership_keywords:
        if word.lower() in role.lower():
            score += 3
            break

    return score

# =========================================
# SEARCH BUTTON
# =========================================
if st.button("Start Lead Search"):

    if not companies_text.strip():
        st.warning("Please enter company names")
        st.stop()

    companies = [c.strip() for c in companies_text.split('\n') if c.strip()]

    all_results = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    total_searches = len(companies) * len(search_templates)
    current_search = 0

    for company in companies:

        status_text.text(f"Searching: {company}")

        for category, template in search_templates.items():

            query = template.format(company=company)

            results = google_search(query, num_results)

            for item in results:

                title = item.get('title', '')
                link = item.get('link', '')
                snippet = item.get('snippet', '')

                # Extract probable name
                probable_name = title.split('-')[0].strip()

                # Extract role
                probable_role = ""

                if '-' in title:
                    probable_role = title.split('-')[1].strip()

                # Alumni detection
                alumni_keywords = ['IIT Bombay', 'IIT B', 'MSU Baroda', 'Sayaji']

                alumni_flag = "No"

                for word in alumni_keywords:
                    if word.lower() in title.lower() or word.lower() in snippet.lower():
                        alumni_flag = "Yes"
                        break

                # Score
                score = calculate_score(
                    category,
                    probable_role,
                    alumni_flag
                )

                all_results.append({
                    'Company': company,
                    'Category': category,
                    'Name': probable_name,
                    'Role': probable_role,
                    'Alumni Match': alumni_flag,
                    'Lead Score': score,
                    'LinkedIn URL': link,
                    'Snippet': snippet
                })

            current_search += 1

            progress_bar.progress(current_search / total_searches)

            time.sleep(sleep_time)

    # =========================================
    # DATAFRAME
    # =========================================
    results_df = pd.DataFrame(all_results)

    # Remove duplicates
    results_df.drop_duplicates(
        subset=['LinkedIn URL'],
        inplace=True
    )

    # Sort by score safely
    if not results_df.empty and 'Lead Score' in results_df.columns:

        results_df.sort_values(
            by='Lead Score',
            ascending=False,
            inplace=True
        )

    else:
        st.warning("No leads found. Check API key or queries.")
        st.stop()

    # =========================================
    # FILTERS
    # =========================================
    st.success(f"Found {len(results_df)} leads")

    col1, col2 = st.columns(2)

    with col1:
        selected_category = st.multiselect(
            "Filter Category",
            options=results_df['Category'].unique(),
            default=results_df['Category'].unique()
        )

    with col2:
        alumni_filter = st.selectbox(
            "Alumni Filter",
            options=['All', 'Yes Only']
        )

    filtered_df = results_df[
        results_df['Category'].isin(selected_category)
    ]

    if alumni_filter == 'Yes Only':
        filtered_df = filtered_df[
            filtered_df['Alumni Match'] == 'Yes'
        ]

    # =========================================
    # DISPLAY
    # =========================================
    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    # =========================================
    # DOWNLOAD BUTTON
    # =========================================
    excel_file = "lead_results.xlsx"

    filtered_df.to_excel(excel_file, index=False)

    with open(excel_file, 'rb') as f:
        st.download_button(
            label="Download Excel",
            data=f,
            file_name="lead_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # =========================================
    # METRICS
    # =========================================
    st.subheader("Lead Metrics")

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Total Leads",
        len(filtered_df)
    )

    m2.metric(
        "Alumni Matches",
        len(filtered_df[
            filtered_df['Alumni Match'] == 'Yes'
        ])
    )

    m3.metric(
        "Hiring Managers",
        len(filtered_df[
            filtered_df['Category'] == 'Hiring Manager'
        ])
    )