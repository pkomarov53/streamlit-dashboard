import pandas as pd
import plotly.express as px
import streamlit as st
from applicaiton.config import PALETTE

def render_categorical_chart(df: pd.DataFrame, column_name: str, chart_type: str = "Круговая", key: str = '') -> None:
    clean_series = df[column_name].dropna()
    if clean_series.empty:
        st.caption("Нет данных для отображения.")
        return

    counts = clean_series.value_counts().reset_index()
    counts.columns = [column_name, "Количество"]
    
    max_label_length = 45
    counts["Label"] = counts[column_name].astype(str).apply(
        lambda x: x[:max_label_length] + "..." if len(x) > max_label_length else x
    )
    
    if chart_type == "Горизонтальная":
        counts = counts.sort_values(by="Количество", ascending=True)
        fig = px.bar(
            counts,
            x="Количество",
            y="Label",
            orientation="h",
            text="Количество",
            color="Количество",
            color_continuous_scale=PALETTE["colorscale"],
            hover_data=[column_name]
        )
        fig.update_layout(
            xaxis=dict(title="Количество", showgrid=True, gridcolor="#ECEFF1", dtick=1),
            yaxis=dict(title="", showgrid=False),
            coloraxis_showscale=False,
            height=max(350, len(counts) * 45)
        )
        fig.update_traces(
            textposition="outside", 
            marker_line_width=0,
            hovertemplate="<b>%{customdata[0]}</b><br>Количество: %{value}<extra></extra>"
        )

    elif chart_type == "Вертикальная":
        fig = px.bar(
            counts,
            x="Label",
            y="Количество",
            text="Количество",
            color="Количество",
            color_continuous_scale=PALETTE["colorscale"],
            hover_data=[column_name]
        )
        fig.update_layout(
            xaxis=dict(title="", tickangle=-25, showgrid=False),
            yaxis=dict(title="Количество", showgrid=True, gridcolor="#ECEFF1", dtick=1),
            coloraxis_showscale=False,
            height=450
        )
        fig.update_traces(
            textposition="outside", 
            marker_line_width=0,
            hovertemplate="<b>%{customdata[0]}</b><br>Количество: %{value}<extra></extra>"
        )

    else:
        fig = px.pie(
            counts,
            names="Label",
            values="Количество",
            color_discrete_sequence=PALETTE["colorscale"],
            hole=0.35,
            hover_data=[column_name]
        )
        fig.update_layout(
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.0),
            height=450
        )
        fig.update_traces(
            textposition="inside", 
            textinfo="percent",
            hovertemplate="<b>%{customdata[0]}</b><br><br>Количество: %{value}<br>Доля: %{percent}<extra></extra>"
        )
    
    # Явно задаем title="", чтобы избавиться от надписи undefined
    fig.update_layout(
        title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", size=12, color=PALETTE["text"]),
        margin=dict(l=20, r=20, t=10, b=30)
    )
    
    chart_key = key or f"plotly_chart_{column_name}"
    st.plotly_chart(fig, width='stretch', key=chart_key)

def render_timeline_chart(df: pd.DataFrame) -> None:
    if "Отметка времени" not in df.columns or df["Отметка времени"].isnull().all():
        return
        
    valid_dates = df["Отметка времени"].dropna()
    if valid_dates.empty:
        return

    timeline_df = valid_dates.dt.floor("D").value_counts().reset_index()
    timeline_df.columns = ["Дата", "Ответы"]
    timeline_df = timeline_df.sort_values("Дата")
    
    timeline_df["Дата_стр"] = timeline_df["Дата"].dt.strftime("%d.%m.%Y")
    
    fig = px.area(
        timeline_df,
        x="Дата_стр",
        y="Ответы",
        title="Динамика поступления анкет по дням",
        markers=True,
        color_discrete_sequence=[PALETTE["primary"]]
    )
    
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", size=12, color=PALETTE["text"]),
        xaxis=dict(title="", showgrid=False, type="category"),
        yaxis=dict(title="Количество", showgrid=True, gridcolor="#ECEFF1", dtick=1),
        height=300,
        margin=dict(l=20, r=20, t=40, b=30)
    )
    
    st.plotly_chart(fig, width='stretch', key="timeline_chart")