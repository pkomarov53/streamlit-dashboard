import pandas as pd
import plotly.express as px
import streamlit as st
from config import PALETTE

def render_categorical_chart(df: pd.DataFrame, column_name: str) -> None:
    counts = df[column_name].value_counts().reset_index()
    counts.columns = [column_name, "Количество"]
    
    # Усекаем слишком длинные ответы для легенды, чтобы они не ломали верстку
    max_label_length = 45
    counts["Label"] = counts[column_name].astype(str).apply(
        lambda x: x[:max_label_length] + "..." if len(x) > max_label_length else x
    )
    
    fig = px.pie(
        counts,
        names="Label",
        values="Количество",
        title=f"Распределение: {column_name}",
        color_discrete_sequence=PALETTE["colorscale"],
        hole=0.35,
        hover_data=[column_name] # Показываем полный текст ответа при наведении
    )
    
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", size=12, color=PALETTE["text"]),
        title_font=dict(size=14, color=PALETTE["secondary"]),
        margin=dict(l=20, r=20, t=50, b=50),
        height=500,
        # Вертикальная легенда справа с автоматическим позиционированием
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.0) 
    )
    
    # Оставляем только проценты внутри секторов для чистоты визуализации
    fig.update_traces(
        textposition="inside", 
        textinfo="percent",
        hovertemplate="<b>%{customdata[0]}</b><br><br>Количество: %{value}<br>Доля: %{percent}<extra></extra>"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_timeline_chart(df: pd.DataFrame) -> None:
    if "Отметка времени" not in df.columns or df["Отметка времени"].isnull().all():
        return
        
    timeline_df = df.set_index("Отметка времени").resample("D").size().reset_index(name="Ответы")
    
    fig = px.area(
        timeline_df,
        x="Отметка времени",
        y="Ответы",
        title="Динамика поступления анкет по дням",
        markers=True,
        color_discrete_sequence=[PALETTE["primary"]]
    )
    
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", size=12, color=PALETTE["text"]),
        xaxis=dict(title="", showgrid=False),
        yaxis=dict(title="Количество", showgrid=True, gridcolor="#ECEFF1"),
        height=300,
        margin=dict(l=20, r=20, t=40, b=30)
    )
    
    st.plotly_chart(fig, use_container_width=True)