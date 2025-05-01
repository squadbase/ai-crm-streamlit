import os, pathlib
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

attio_api_key = os.environ.get("ATTIO_ACCESS_TOKEN")
ATTIO_API_BASE = "https://api.attio.com/v2"

def get_company_name(record_id):
    """
    Fetch company name using the record ID
    
    Args:
        record_id: Company record ID
        
    Returns:
        Company name or None if not found
    """
    url = f"{ATTIO_API_BASE}/objects/companies/records/{record_id}"
    response = requests.get(
        url, 
        headers={
            "Authorization": f"Bearer {attio_api_key}", 
            "Content-Type": "application/json"
        }, 
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("data") and data["data"].get("values") and data["data"]["values"].get("name"):
            for name_entry in data["data"]["values"]["name"]:
                if name_entry.get("value"):
                    return name_entry["value"]
    return None

st.logo('assets/squadbase.png', link='https://squadbase.dev', icon_image='assets/squadbase_icon.png')
st.title("Notes Dashboard")
st.write("View the total number of notes created within a selected date range.")

@st.cache_data(ttl=300)  # 5 minute cache
def fetch_notes(page_size: int = 50) -> pd.DataFrame:
    """
    Fetch notes from Attio API
    
    Args:
        page_size: Number of notes to fetch per page (max 50)
        
    Returns:
        DataFrame containing notes data
    """
    url = f"{ATTIO_API_BASE}/notes"
    params = {"limit": page_size}
    all_rows = []

    while True:
        list_notes = requests.get(
            url, 
            headers={
                "Authorization": f"Bearer {attio_api_key}", 
                "Content-Type": "application/json"
            }, 
            params=params, 
            timeout=30
        )
        list_notes.raise_for_status()  # Raise exception for 4xx/5xx errors
        payload = list_notes.json()    # {"data":[…], "next_cursor": "...", "has_more": true}
        all_rows.extend(payload["data"])

        if payload.get("has_more") and payload.get("next_cursor"):
            params["page[after]"] = payload["next_cursor"]
        else:
            break

    df = pd.json_normalize(all_rows)
    return df

def filter_notes_by_date(notes_df: pd.DataFrame, start_date, end_date) -> pd.DataFrame:
    """
    Filter notes by date range
    
    Args:
        notes_df: DataFrame containing notes
        start_date: Start date for filtering
        end_date: End date for filtering
        
    Returns:
        Filtered DataFrame
    """
    if 'created_at' not in notes_df.columns:
        return pd.DataFrame()
    
    notes_df['created_at_dt'] = pd.to_datetime(notes_df['created_at'])
    
    notes_df['created_at_date'] = notes_df['created_at_dt'].dt.date
    
    start_date_obj = start_date
    end_date_obj = end_date
    
    # Filter by date range using date objects
    filtered_df = notes_df[
        (notes_df['created_at_date'] >= start_date_obj) & 
        (notes_df['created_at_date'] <= end_date_obj)
    ]
    
    return filtered_df

col1, col2 = st.columns(2)
with col1:
    default_start_date = datetime.now().date() - timedelta(days=30)
    start_date = st.date_input("Start Date", value=default_start_date)
with col2:
    end_date = st.date_input("End Date", value=datetime.now().date())

if start_date > end_date:
    st.error("Error: Start date must be before end date")
else:
    with st.spinner("Fetching notes..."):
        notes_df = fetch_notes()
    
    filtered_notes = filter_notes_by_date(notes_df, start_date, end_date)
    
    st.subheader("Notes Summary")
    st.metric("Total Notes", len(filtered_notes))
    
    company_info = ""
    if not filtered_notes.empty and 'parent_object' in filtered_notes.columns:
        company_notes = filtered_notes[filtered_notes['parent_object'] == 'companies']
        if not company_notes.empty and 'parent_record_id' in company_notes.columns:
            company_ids = company_notes['parent_record_id'].unique()
            company_names = []
            
            # Fetch company names
            for company_id in company_ids:
                company_name = get_company_name(company_id)
                if company_name:
                    company_names.append(company_name)
            
            if company_names:
                company_info = f" for companies: {', '.join(company_names)}"
    
    st.write(f"Showing notes created between {start_date} and {end_date}{company_info}")
    
    with st.expander("View Notes Details"):
        if not filtered_notes.empty:
            if 'title' in filtered_notes.columns and 'created_at' in filtered_notes.columns:
                display_df = filtered_notes[['title', 'created_at']].copy()
                display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                
                if 'parent_object' in filtered_notes.columns and 'parent_record_id' in filtered_notes.columns:
                    display_df['company'] = None
                    
                    # Create a mapping of record IDs to company names
                    company_names = {}
                    for i, (_, row) in enumerate(filtered_notes.iterrows()):
                        if row.get('parent_object') == 'companies' and row.get('parent_record_id'):
                            if row['parent_record_id'] not in company_names:
                                company_name = get_company_name(row['parent_record_id'])
                                if company_name:
                                    company_names[row['parent_record_id']] = company_name
                    
                    for i, (idx, row) in enumerate(filtered_notes.iterrows()):
                        if row.get('parent_object') == 'companies' and row.get('parent_record_id') in company_names:
                            display_df.at[idx, 'company'] = company_names[row['parent_record_id']]
                
                st.dataframe(display_df)
            else:
                st.dataframe(filtered_notes)
        else:
            st.write("No notes found in the selected date range.")
