import urllib.parse
import pandas as pd
import streamlit as st
from config import SPREADSHEET_ID, CACHE_TTL

@st.cache_data(ttl=CACHE_TTL, show_spinner="Загрузка данных из Google Sheets...")
def load_sheet_data(sheet_name: str, spreadsheet_id: str = SPREADSHEET_ID) -> pd.DataFrame:
    """Загружает конкретный лист Google Таблицы через CSV endpoint."""
    encoded_sheet_name = urllib.parse.quote(sheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    
    try:
        df = pd.read_csv(url)
        df = df.dropna(how="all").dropna(axis=1, how="all")
        
        if "Отметка времени" in df.columns:
            df["Отметка времени"] = pd.to_datetime(df["Отметка времени"], dayfirst=True, errors="coerce")
            
        return df
    except Exception as e:
        st.error(f"Ошибка при загрузке листа '{sheet_name}': {e}")
        return pd.DataFrame()