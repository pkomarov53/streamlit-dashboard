import pandas as pd
import plotly.express as px
import streamlit as st
from config import PALETTE

def render_categorical_chart(df: pd.DataFrame, column_name: str) -> None:
    counts = df[column_name].value_counts().reset_index()
    counts.columns = [column_name, "Количество"]
    
    fig = px.bar(
        counts,
        x=column_name,
        y="Количество",
        text="Количество",
        title=f"Распределение: {column_name}",
        color="Количество",
        color_continuous_scale=PALETTE["colorscale"]
    )
    
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", size=12, color=PALETTE["text"]),
        title_font=dict(size=14, color=PALETTE["secondary"]),
        xaxis=dict(title="", tickangle=-25, showgrid=False),
        yaxis=dict(title="Количество", showgrid=True, gridcolor="#ECEFF1"),
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=50, b=50),
        height=420
    )
    fig.update_traces(textposition="outside", marker_line_width=0)
    
    st.plotly_chart(fig, use_container_width=True)

def render_timeline_chart(df: pd.DataFrame) -> None:
    if "Отметка времени" not in df.columns or df["Отметка времени"].isnull().all():
        return
        
    timeline_df = df.set_index("Отметка времени").resample("D").size().reset_index(name="Ответы")
    
    fig = px.line(
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