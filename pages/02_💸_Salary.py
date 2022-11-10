import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import datetime

st.set_page_config(page_title='💸 Salary', page_icon = 'images/luke_Favicon.png')

# import and cleanup dataframe
@st.experimental_memo
def fetch_and_clean_data():
    data_url = 'https://storage.googleapis.com/gsearch_share/gsearch_jobs.csv'
    jobs_data = pd.read_csv(data_url).replace("'","", regex=True)
    jobs_data.date_time = pd.to_datetime(jobs_data.date_time) # convert to date time
    jobs_data = jobs_data.drop(labels=['Unnamed: 0', 'index'], axis=1, errors='ignore')
    jobs_data.description_tokens = jobs_data.description_tokens.str.strip("[]").str.split(",")

    # drop rows without salary data
    jobs_data = jobs_data[jobs_data.salary_avg.notna()] 
    return jobs_data

jobs_all = fetch_and_clean_data()

# Skill sort, count, and filter list data
select_all = "Select All"
skill_count = pd.DataFrame(jobs_all.description_tokens.sum()).value_counts().rename_axis('keywords').reset_index(name='counts')
skill_count = skill_count[skill_count.keywords != '']
skills = list(skill_count.keywords)
skills.insert(0, select_all)

# Platform sort, count, and filter list data
platform_count = jobs_all.via.value_counts().rename_axis('platforms').reset_index(name='counts')
platform = list(platform_count.platforms)
platform.insert(0, select_all)

# Other Filter data for slicers
job_type = pd.DataFrame(jobs_all.schedule_type.drop_duplicates())
job_type = job_type[job_type.schedule_type.notna()]
job_type = list(job_type.schedule_type)
job_type.insert(0, select_all)

with st.sidebar:
    st.markdown("# 💰 Filters")
    skills_choice = st.selectbox("Data Skill:", skills)
    platform_choice = st.selectbox("Social Platform:", platform)
    job_type_choice = st.radio("Job Type:", job_type)

# Top page build
st.markdown("## 💸 Salary Histogram for Data Analysts")
salary_dict = {"Standardized": "salary_standardized", "Annual": "salary_yearly", "Hourly": "salary_hourly"}
salary_choice = st.radio('Salary aggregation:', list(salary_dict.keys()), horizontal=True)

# Side column filter data transform
if skills_choice != select_all:
    jobs_all = jobs_all[jobs_all.description_tokens.apply(lambda x: skills_choice in x)]
if platform_choice != select_all:
    jobs_all = jobs_all[jobs_all.via.apply(lambda x: platform_choice in x)]
if job_type_choice != select_all:
    jobs_all = jobs_all[jobs_all.schedule_type.apply(lambda x: job_type_choice in str(x))]

# Man page filter data transform
salary_column = salary_dict[salary_choice]
column = jobs_all[salary_column]
bins = 'auto'

# Make final dataframe
salary_df = jobs_all[['title', 'company_name', salary_column]] # select columns
salary_df = salary_df[salary_df[salary_column].notna()]
salary_df[salary_column] = salary_df[salary_column].astype(int)

# Final visualizations



try: 
    salary_chart = alt.Chart(salary_df).mark_bar(
        cornerRadiusTopLeft=10,
        cornerRadiusTopRight=10    
    ).encode(
        x=alt.X(salary_column, title="Salary", axis=alt.Axis(format='$,f', labelFontSize=20, titleFontSize=17), bin = alt.BinParams(maxbins = 20)), # bins = len(salary_df[salary_column])/4
        y=alt.Y('count()', title="Count of Job Postings", axis=alt.Axis(labelFontSize=17, titleFontSize=17)),
    )
    st.altair_chart(salary_chart, use_container_width=True)
    st.markdown("#### 💵 Table of Salaries")
    st.dataframe(salary_df)
    if salary_choice == list(salary_dict.keys())[0]:
        st.write("NOTE: 'Standardized' adjusts both 'Annual' and 'Hourly' salary data to a common unit of annual.")
except:
    st.markdown("# 🙅‍♂️ No results")

# Previous streamlit graph... didn't like look of axis and didn't support histogram
# range = (np.nanmin(column), np.nanmax(column))
# hist_values = np.histogram(column, bins=bins, range=range)
# hist_values = pd.DataFrame(hist_values).fillna(0).transpose()
# hist_values = hist_values.rename(columns={0: "Count", 1: "Salary ($USD)"})
# hist_values = hist_values.astype(int)
# st.bar_chart(data=hist_values, x='Salary ($USD)', y='Count')
