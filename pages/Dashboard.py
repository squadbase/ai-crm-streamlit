import os, pathlib
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

attio_api_key = os.environ.get("ATTIO_ACCESS_TOKEN")
ATTIO_API_BASE = "https://api.attio.com/v2"

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
    
    st.write(f"Showing notes created between {start_date} and {end_date}")
    
    with st.expander("View Notes Details"):
        if not filtered_notes.empty:
            if 'title' in filtered_notes.columns and 'created_at' in filtered_notes.columns:
                display_df = filtered_notes[['title', 'created_at']].copy()
                display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                st.dataframe(display_df)
            else:
                st.dataframe(filtered_notes)
        else:
            st.write("No notes found in the selected date range.")
