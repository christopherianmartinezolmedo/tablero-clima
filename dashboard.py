import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Querétaro Live Weather",
    page_icon="⚡",
    layout="wide"
)

# Estilo personalizado para fondo oscuro
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Querétaro Real-Time Weather Analytics")
st.caption("Monitoreo automatizado con Open-Meteo & Plotly")

# Función para consultar la API (con caché de 5 minutos)
@st.cache_data(ttl=300)
def obtener_datos():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 20.5881,
        "longitude": -100.3899,
        "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "wind_speed_10m"],
        "hourly": ["temperature_2m", "relative_humidity_2m"],
        "timezone": "America/Mexico_City",
        "forecast_days": 1
    }
    res = requests.get(url, params=params)
    return res.json()

# Función para renderizar el panel
def render_dashboard():
    datos = obtener_datos()
    actual = datos["current"]
    historico = datos["hourly"]

    # 1. Encabezado e indicador de estado
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.success("🟢 Conexión activa con estación meteorológica", icon="📡")
    with col_header2:
        if st.button("🔄 Actualizar Datos"):
            st.cache_data.clear()
            st.rerun()

    # 2. Tarjetas de Métricas (KPI Cards)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.container(border=True).metric("Temperatura", f"{actual['temperature_2m']} °C")
    with c2:
        st.container(border=True).metric("Sensación Térmica", f"{actual['apparent_temperature']} °C")
    with c3:
        st.container(border=True).metric("Humedad Relativa", f"{actual['relative_humidity_2m']} %")
    with c4:
        st.container(border=True).metric("Viento", f"{actual['wind_speed_10m']} km/h")

    st.markdown("---")

    # 3. Velocímetros (Gauges)
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        fig_gauge_temp = go.Figure(go.Indicator(
            mode="gauge+number",
            value=actual['temperature_2m'],
            title={'text': "Temperatura Actual (°C)"},
            gauge={
                'axis': {'range': [0, 45]},
                'bar': {'color': "#FF4B4B"},
                'bgcolor': "#1F2937",
                'steps': [
                    {'range': [0, 15], 'color': "#0083B8"},
                    {'range': [15, 28], 'color': "#2E7D32"},
                    {'range': [28, 45], 'color': "#D32F2F"}
                ]
            }
        ))
        fig_gauge_temp.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
        st.plotly_chart(fig_gauge_temp, width='stretch')

    with col_g2:
        fig_gauge_hum = go.Figure(go.Indicator(
            mode="gauge+number",
            value=actual['relative_humidity_2m'],
            title={'text': "Humedad Relativa (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#00D2FF"},
                'bgcolor': "#1F2937",
                'steps': [
                    {'range': [0, 30], 'color': "#E65100"},
                    {'range': [30, 70], 'color': "#2E7D32"},
                    {'range': [70, 100], 'color': "#1565C0"}
                ]
            }
        ))
        fig_gauge_hum.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
        st.plotly_chart(fig_gauge_hum, width='stretch')

    # 4. Gráfica de Doble Eje (Usando make_subplots para evitar errores)
    df = pd.DataFrame({
        "Hora": pd.to_datetime(historico["time"]),
        "Temperatura (°C)": historico["temperature_2m"],
        "Humedad (%)": historico["relative_humidity_2m"]
    })

    # Crear figura con soporte nativo de doble eje secundario
    fig_timeline = make_subplots(specs=[[{"secondary_y": True}]])

    # Traza de Temperatura (Eje Izquierdo)
    fig_timeline.add_trace(
        go.Scatter(
            x=df["Hora"], 
            y=df["Temperatura (°C)"],
            name="Temperatura (°C)",
            mode='lines+markers',
            line=dict(color='#FF4B4B', width=3, shape='spline'),
            hovertemplate='%{y:.1f} °C'
        ),
        secondary_y=False
    )

    # Traza de Humedad (Eje Derecho)
    fig_timeline.add_trace(
        go.Scatter(
            x=df["Hora"], 
            y=df["Humedad (%)"],
            name="Humedad (%)",
            mode='lines+markers',
            line=dict(color='#00D2FF', width=2, dash='dot', shape='spline'),
            hovertemplate='%{y:.1f} %'
        ),
        secondary_y=True
    )

    # Actualizar formato de layout y ejes de forma segura
    fig_timeline.update_layout(
        title_text="<b>Comportamiento de las últimas 24 Horas</b>",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig_timeline.update_xaxes(title_text="Hora del día", gridcolor='#262730')
    fig_timeline.update_yaxes(
        title_text="Temperatura (°C)", 
        title_font=dict(color="#FF4B4B"), 
        tickfont=dict(color="#FF4B4B"), 
        gridcolor='#262730', 
        secondary_y=False
    )
    fig_timeline.update_yaxes(
        title_text="Humedad (%)", 
        title_font=dict(color="#00D2FF"), 
        tickfont=dict(color="#00D2FF"), 
        secondary_y=True
    )

    st.plotly_chart(fig_timeline, width='stretch')

# Ejecución de la app
render_dashboard()
