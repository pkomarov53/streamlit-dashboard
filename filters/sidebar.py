import streamlit as st
import pandas as pd
from typing import Dict, Any
from config import SHEET_NAMES

def render_sidebar() -> Dict[str, Any]:
    st.sidebar.title("Панель управления")
    
    selected_sheet = st.sidebar.selectbox("Выберите анкету:", SHEET_NAMES)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Поиск по данным")
    search_query = st.sidebar.text_input("Введите ключевое слово:")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Мониторинг ответов")
    
    auto_refresh = st.sidebar.checkbox("Включить автообновление", value=False)
    refresh_interval = st.sidebar.slider(
        "Интервал обновления (сек):", 
        min_value=10, 
        max_value=300, 
        value=30, 
        step=10
    )
    
    if st.sidebar.button("Обновить данные вручную"):
        st.cache_data.clear()
        st.rerun()
        
    return {
        "selected_sheet": selected_sheet,
        "auto_refresh": auto_refresh,
        "refresh_interval": refresh_interval,
        "search_query": search_query
    }

def apply_search_filter(df: pd.DataFrame, search_query: str) -> pd.DataFrame:
    if search_query:
        mask = df.astype(str).apply(
            lambda row: row.str.contains(search_query, case=False, na=False).any(), 
            axis=1
        )
        filtered_df = df[mask]
        st.sidebar.caption(f"Найдено совпадений: **{len(filtered_df)}** из **{len(df)}**")
        return filtered_df
    return df