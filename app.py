import time
import pandas as pd
import streamlit as st

from data.loader import load_sheet_data
from filters.sidebar import render_sidebar, apply_search_filter
from diagrams.charts import render_categorical_chart, render_timeline_chart
from report.generator import render_export_ui

st.set_page_config(
    page_title="Дашборд анкет ПК",
    page_icon="📊",
    layout="wide"
)

def main():
    # Сайдбар
    params = render_sidebar()
    selected_sheet = params["selected_sheet"]
    
    # Загрузка данных
    raw_df = load_sheet_data(selected_sheet)
    
    st.title(f"📊 {selected_sheet}")
    
    if raw_df.empty:
        st.warning("В данном листе нет данных или доступ ограничен.")
        return

    # Фильтрация
    df = apply_search_filter(raw_df)

    # Метрики (KPI)
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

    # Вкладки визуализации, данных и экспорта
    tab1, tab2, tab3 = st.tabs(["📈 Графики", "📋 Таблица ответов", "📥 Экспорт"])

    with tab1:
        render_timeline_chart(df)
        
        # Выбор вопросов с ограниченным набором ответов
        cat_cols = [c for c in df.columns if c not in ["Отметка времени", "Ваш e-mail для связи"] and df[c].nunique() < 25]
        if cat_cols:
            selected_col = st.selectbox("Выберите вопрос для анализа:", cat_cols)
            render_categorical_chart(df, selected_col)
        else:
            st.info("На этом листе большинство ответов — развернутые текстовые поля.")

    with tab2:
        st.dataframe(df, use_container_width=True)

    with tab3:
        render_export_ui(df, selected_sheet)

    # Цикл автообновления
    if params["auto_refresh"]:
        time.sleep(params["refresh_interval"])
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()