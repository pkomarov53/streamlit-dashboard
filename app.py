import time
import pandas as pd
import streamlit as st

from data.loader import load_sheet_data
from filters.sidebar import render_sidebar, apply_search_filter
from diagrams.charts import render_categorical_chart, render_timeline_chart
from report.generator import render_export_ui

st.set_page_config(
    page_title="Дашборд анкет ПК",
    layout="wide"
)

def main():
    try:
        st.sidebar.image("logo.png", use_container_width=True)
    except FileNotFoundError:
        st.sidebar.markdown("**[МЕСТО ДЛЯ ЛОГОТИПА]**")
        
    st.sidebar.markdown("---")

    params = render_sidebar()
    selected_sheet = params["selected_sheet"]
    
    raw_df = load_sheet_data(selected_sheet)
    
    st.title(selected_sheet)
    
    if raw_df.empty:
        return

    df = apply_search_filter(raw_df, params["search_query"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Всего ответов", len(df))
    
    if "Отметка времени" in df.columns and not df["Отметка времени"].isnull().all():
        last_date = df["Отметка времени"].max()
        c2.metric("Последний ответ", last_date.strftime("%d.%m.%Y %H:%M") if pd.notnull(last_date) else "—")
        
        week_ago = pd.Timestamp.now() - pd.Timedelta(days=7)
        c3.metric("За 7 дней", len(df[df["Отметка времени"] >= week_ago]))
    else:
        c2.metric("Столбцов", len(df.columns))
        c3.metric("Статус", "Активно")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Графики", "Таблица ответов", "Экспорт"])

    with tab1:
        render_timeline_chart(df)
        
        # Разделяем на вопросы с выбором вариантов (<20 уникальных) и открытые текстовые
        ignore_cols = ["Отметка времени", "Ваш e-mail для связи"]
        cat_cols = [c for c in df.columns if c not in ignore_cols and df[c].nunique() < 20]
        text_cols = [c for c in df.columns if c not in ignore_cols and df[c].nunique() >= 20]
        
        if cat_cols:
            st.markdown("### Детализация по вопросам")
            
            for col in cat_cols:
                col_title, col_selector = st.columns([3, 1])
                
                with col_title:
                    # Корректный вывод заголовка без лишних звездочек
                    st.subheader(col.strip())
                    
                with col_selector:
                    chart_type = st.selectbox(
                        "Вид графика:",
                        options=["Круговая", "Горизонтальная", "Вертикальная"],
                        key=f"chart_type_{col}",
                        label_visibility="collapsed"
                    )
                
                render_categorical_chart(df, col, chart_type, key=f"plotly_{col}")
                st.markdown("---")

        # Блок для просмотра открытых текстовых вопросов (например, Вопрос №1)
        if text_cols:
            st.markdown("### Текстовые ответы (открытые вопросы)")
            for col in text_cols:
                with st.expander(f"💬 {col.strip()}", expanded=False):
                    st.dataframe(df[[col]].dropna(), use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Детализация данных")
        
        all_columns = df.columns.tolist()
        default_cols = all_columns[:6] if len(all_columns) > 6 else all_columns
        
        selected_columns = st.multiselect(
            "Настройте видимые столбцы:",
            options=all_columns,
            default=default_cols
        )
        
        if selected_columns:
            st.dataframe(df[selected_columns], use_container_width=True, hide_index=True)
        else:
            st.info("Выберите хотя бы один столбец для отображения данных.")

    with tab3:
        render_export_ui(df, selected_sheet)

    if params["auto_refresh"]:
        time.sleep(params["refresh_interval"])
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()