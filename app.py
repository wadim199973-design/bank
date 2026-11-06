import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. НАСТРОЙКА СТРАНИЦЫ И ФИРМЕННОГО СТИЛЯ
st.set_page_config(page_title="Neo Bank Dashboard", layout="wide", page_icon="🏦")

# Фирменные цвета Neo Bank
COLORS = {
    'bright_neo': '#6B2D9D',
    'dark_neo': '#2D1B4E',
    'digital_crimson': '#F4364C',
    'digital_tiffany': '#7EDDD3',
    'digital_green': '#00C389',
    'digital_light': '#FFE04B',
    'white': '#FFFFFF',
}

# SVG логотип Neo Bank
LOGO_SVG = """
<svg width="280" height="80" viewBox="0 0 280 80" xmlns="http://www.w3.org/2000/svg">
    <!-- Графический элемент (полумесяц) -->
    <circle cx="45" cy="40" r="35" fill="none" stroke="#6B2D9D" stroke-width="8"/>
    <circle cx="50" cy="40" r="35" fill="white" stroke="none"/>
    
    <!-- Текст "neo" -->
    <text x="25" y="52" font-family="Helvetica, Arial, sans-serif" font-size="28" font-weight="400" fill="#2D1B4E">neo</text>
    
    <!-- Текст "bank" -->
    <text x="95" y="52" font-family="Helvetica, Arial, sans-serif" font-size="28" font-weight="400" fill="#2D1B4E">bank</text>
    
    <!-- Слоган "be in digital" -->
    <text x="95" y="68" font-family="Helvetica, Arial, sans-serif" font-size="12" font-weight="400" fill="#6B2D9D">be in digital</text>
</svg>
"""

# Кастомный CSS с брендбуком
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        color: #2D1B4E !important;
    }
    
    .stMarkdown, p, div, label {
        font-family: 'Helvetica', Arial, sans-serif !important;
        font-weight: 400 !important;
        color: #2D1B4E !important;
    }
    
    .logo-container {
        text-align: left;
        margin-bottom: 20px;
        padding: 20px 0;
    }
    
    .main-header {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 36px !important;
        font-weight: 700 !important;
        color: #2D1B4E !important;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    
    .sub-header {
        font-family: 'Helvetica', sans-serif !important;
        font-size: 16px !important;
        font-weight: 300 !important;
        color: #6B2D9D !important;
        margin-bottom: 30px !important;
    }
    
    .stSidebar {
        background-color: #F8F7FA !important;
    }
    
    .stSidebar h2 {
        color: #6B2D9D !important;
        font-family: 'Montserrat', sans-serif !important;
    }
    
    [data-testid="stMetricValue"] {
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        color: #2D1B4E !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'Helvetica', sans-serif !important;
        font-weight: 400 !important;
        color: #6B2D9D !important;
    }
    
    .stButton>button {
        background-color: #6B2D9D !important;
        color: white !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
    }
    
    .stButton>button:hover {
        background-color: #2D1B4E !important;
    }
    
    .brand-pattern {
        height: 4px;
        background: linear-gradient(90deg, #6B2D9D 0%, #7EDDD3 50%, #00C389 100%);
        margin: 20px 0;
    }
    
    .footer {
        text-align: center;
        padding: 20px 0;
        margin-top: 40px;
        border-top: 1px solid #E0E0E0;
    }
</style>
""", unsafe_allow_html=True)

# 2. ГЕНЕРАЦИЯ ТЕСТОВЫХ ДАННЫХ
@st.cache_data 
def load_mock_data():
    np.random.seed(42)
    regions = ['Минск', 'Брестская обл.', 'Витебская обл.', 'Гомельская обл.', 'Гродненская обл.', 'Могилевская обл.']
    dates = pd.date_range(end=datetime.today(), periods=180).tolist() 
    
    data = []
    for region in regions:
        for date in dates:
            base_portfolio = np.random.randint(50_000_000, 200_000_000) 
            npl_ratio = np.random.uniform(1.5, 8.5) 
            nii = base_portfolio * np.random.uniform(0.001, 0.003) 
            
            data.append({
                'date': date,
                'region': region,
                'portfolio_volume': base_portfolio,
                'npl_ratio': npl_ratio,
                'nii': nii
            })
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_mock_data()

# 3. ШАПКА С ЛОГОТИПОМ
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
st.markdown(LOGO_SVG, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="main-header">Оперативный мониторинг показателей</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Динамика ключевых метрик с детализацией по регионам и периодам</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-pattern"></div>', unsafe_allow_html=True)

# 4. БОКОВАЯ ПАНЕЛЬ С ФИЛЬТРАМИ
st.sidebar.markdown("## ⚙️ Параметры отображения")

timeframe = st.sidebar.radio(
    "Период агрегации:",
    options=["День", "Неделя", "Месяц"],
    index=1
)

selected_region = st.sidebar.selectbox(
    "Регион:",
    options=["Все регионы"] + list(df['region'].unique())
)

# Фильтрация данных
if selected_region != "Все регионы":
    df_filtered = df[df['region'] == selected_region].copy()
else:
    df_filtered = df.groupby('date').agg({
        'portfolio_volume': 'sum',
        'npl_ratio': 'mean', 
        'nii': 'sum'
    }).reset_index()
    df_filtered['region'] = 'Все регионы'

# Агрегация по времени
freq_map = {"День": "D", "Неделя": "W-MON", "Месяц": "ME"}
freq = freq_map[timeframe]
df_filtered = df_filtered.set_index('date')

df_agg = df_filtered.resample(freq).agg({
    'portfolio_volume': 'sum',
    'npl_ratio': 'mean',
    'nii': 'sum'
}).reset_index()

df_agg['date_str'] = df_agg['date'].dt.strftime('%d.%m.%Y' if timeframe == "День" else '%b %Y')

# 5. KPI МЕТРИКИ
latest = df_agg.iloc[-1]
prev = df_agg.iloc[-2] if len(df_agg) > 1 else latest

delta_portfolio = ((latest['portfolio_volume'] - prev['portfolio_volume']) / prev['portfolio_volume'] * 100) if len(df_agg) > 1 else 0
delta_npl = latest['npl_ratio'] - prev['npl_ratio'] if len(df_agg) > 1 else 0
delta_nii = ((latest['nii'] - prev['nii']) / prev['nii'] * 100) if len(df_agg) > 1 else 0

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="💰 Кредитный портфель", 
        value=f"{latest['portfolio_volume'] / 1_000_000:,.1f} млн BYN",
        delta=f"{delta_portfolio:+.1f}%"
    )

with col2:
    st.metric(
        label="⚠️ Доля просрочки (NPL)", 
        value=f"{latest['npl_ratio']:.2f}%",
        delta=f"{delta_npl:+.2f}%",
        delta_color="inverse"
    )

with col3:
    st.metric(
        label="📈 Чистый процентный доход (NII)", 
        value=f"{latest['nii'] / 1_000:,.1f} тыс BYN",
        delta=f"{delta_nii:+.1f}%"
    )

st.markdown("---")

# 6. ГРАФИКИ
col_chart1, col_chart2 = st.columns([2, 1])

with col_chart1:
    st.markdown("### Динамика показателей")
    
    fig_trend = go.Figure()
    
    fig_trend.add_trace(go.Scatter(
        x=df_agg['date_str'],
        y=df_agg['portfolio_volume'],
        name='Кредитный портфель',
        line=dict(color=COLORS['bright_neo'], width=3),
        mode='lines+markers',
        marker=dict(size=6, color=COLORS['bright_neo'])
    ))
    
    fig_trend.add_trace(go.Scatter(
        x=df_agg['date_str'],
        y=df_agg['nii'],
        name='NII',
        line=dict(color=COLORS['digital_green'], width=3, dash='dash'),
        mode='lines+markers',
        marker=dict(size=6, color=COLORS['digital_green'])
    ))
    
    fig_trend.update_layout(
        font=dict(family="Helvetica, Arial", size=12),
        title_font=dict(family="Montserrat", size=16, color=COLORS['dark_neo']),
        legend_font=dict(family="Helvetica", size=11),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode="x unified",
        height=450,
        margin=dict(l=60, r=40, t=60, b=60),
        xaxis=dict(gridcolor='#E0E0E0', tickfont=dict(family="Helvetica", size=11)),
        yaxis=dict(gridcolor='#E0E0E0', tickfont=dict(family="Helvetica", size=11)),
        legend=dict(x=0, y=1.05, traceorder='normal', font=dict(family="Helvetica", size=11))
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)

with col_chart2:
    st.markdown("### Разбивка по регионам")
    
    recent_data = df[df['date'] >= (datetime.today() - timedelta(days=30))]
    
    if selected_region == "Все регионы":
        region_data = recent_data.groupby('region')['portfolio_volume'].sum().reset_index()
        
        fig_region = px.bar(
            region_data,
            x='portfolio_volume', 
            y='region', 
            orientation='h',
            color='portfolio_volume',
            color_continuous_scale=[COLORS['digital_tiffany'], COLORS['bright_neo'], COLORS['dark_neo']]
        )
        
        fig_region.update_layout(
            font=dict(family="Helvetica", size=11),
            title_font=dict(family="Montserrat", size=14, color=COLORS['dark_neo']),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400,
            margin=dict(l=120, r=20, t=40, b=40),
            xaxis=dict(gridcolor='#E0E0E0', tickfont=dict(family="Helvetica", size=10)),
            yaxis=dict(tickfont=dict(family="Helvetica", size=11)),
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig_region, use_container_width=True)
    else:
        st.info(f"✅ Выбран регион: {selected_region}")

# 7. ДЕТАЛЬНАЯ ТАБЛИЦА
with st.expander("📊 Детальные данные"):
    df_display = df_agg.copy()
    df_display['date'] = df_display['date'].dt.strftime('%d.%m.%Y')
    
    st.dataframe(
        df_display.style.format({
            'portfolio_volume': '{:,.0f}',
            'npl_ratio': '{:.2f}%',
            'nii': '{:,.0f}'
        }),
        use_container_width=True,
        height=300
    )

# 8. ФУТЕР С ЛОГОТИПОМ
st.markdown("---")
st.markdown('<div class="footer">', unsafe_allow_html=True)
st.markdown(LOGO_SVG, unsafe_allow_html=True)
st.markdown(f"""
    <div style='font-family: Helvetica; color: {COLORS["bright_neo"]}; font-size: 12px; margin-top: 10px;'>
        Система мониторинга показателей | {datetime.now().strftime('%Y')}
    </div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)