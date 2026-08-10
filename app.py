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
    # Логотип в левом верхнем углу
    # Замени "logo.png" на путь к реальному файлу
    try:
        st.sidebar.image("logo.png", use_container_width=True)
    except FileNotFoundError:
        st.sidebar.markdown("**[МЕСТО ДЛЯ ЛОГОТИПА]**")
        
    st.sidebar.markdown("---")

    # Сайдбар и загрузка данных
    params = render_sidebar()
    selected_sheet = params["selected_sheet"]
    
    raw_df = load_sheet_data(selected_sheet)
    
    st.title(selected_sheet)
    
    # Временный отказ от визуального предупреждения
    if raw_df.empty:
        return

    # Применение фильтров (теперь в сайдбаре)
    df = apply_search_filter(raw_df, params["search_query"])

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

    # Вкладки без лишних символов
    tab1, tab2, tab3 = st.tabs(["Графики", "Таблица ответов", "Экспорт"])

    with tab1:
        render_timeline_chart(df)
        
        cat_cols = [c for c in df.columns if c not in ["Отметка времени", "Ваш e-mail для связи"] and df[c].nunique() < 12]
        
        if cat_cols:
            st.markdown("### Детализация по вопросам")
            
            # Вывод графиков для всех вопросов друг за другом
            for col in cat_cols:
                render_categorical_chart(df, col)
                st.markdown("---") # Визуальный разделитель между графиками
        else:
            st.info("На этом листе большинство ответов — развернутые текстовые поля.")

    with tab2:
        st.subheader("Детализация данных")
        
        # Получаем список всех колонок
        all_columns = df.columns.tolist()
        
        # По умолчанию показываем первые 5-6 колонок (например, дату, email и пару первых вопросов)
        default_cols = all_columns[:6] if len(all_columns) > 6 else all_columns
        
        # Селектор для выбора отображаемых столбцов
        selected_columns = st.multiselect(
            "Настройте видимые столбцы:",
            options=all_columns,
            default=default_cols
        )
        
        if selected_columns:
            # Скрываем индекс для более чистого отображения таблицы
            st.dataframe(df[selected_columns], use_container_width=True, hide_index=True)
        else:
            st.info("Выберите хотя бы один столбец для отображения данных.")

    with tab3:
        render_export_ui(df, selected_sheet)

    # Цикл автообновления
    if params["auto_refresh"]:
        time.sleep(params["refresh_interval"])
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()