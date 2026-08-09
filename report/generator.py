import io
import pandas as pd
import streamlit as st

def generate_excel_report(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Ответы", index=False)
        
        # Генерация базовой сводки
        summary_list = []
        for col in df.columns:
            if col != "Отметка времени":
                top_val = df[col].mode().iloc[0] if not df[col].mode().empty else "—"
                summary_list.append({
                    "Вопрос": col,
                    "Всего ответов": df[col].notnull().sum(),
                    "Уникальных вариантов": df[col].nunique(),
                    "Самый популярный ответ": str(top_val)[:100]
                })
        
        pd.DataFrame(summary_list).to_excel(writer, sheet_name="Сводка", index=False)
        
    return output.getvalue()

def render_export_ui(df: pd.DataFrame, sheet_name: str) -> None:
    st.markdown("### 📥 Экспорт данных")
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📄 Скачать CSV",
            data=csv_data,
            file_name=f"{sheet_name}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    with col2:
        excel_data = generate_excel_report(df)
        st.download_button(
            label="📊 Скачать Excel с аналитикой",
            data=excel_data,
            file_name=f"{sheet_name}_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )