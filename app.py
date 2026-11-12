import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
import os
from sqlalchemy import create_engine

# ==============================================================================
# 1. НАСТРОЙКА СТРАНИЦЫ И ФИРМЕННОГО СТИЛЯ
# ==============================================================================
st.set_page_config(page_title="Neo Bank Dashboard", layout="wide", page_icon="🏦")

COLORS = {
    'bright_neo': '#6B2D9D',
    'dark_neo': '#2D1B4E',
    'digital_crimson': '#F4364C',
    'digital_tiffany': '#7EDDD3',
    'digital_green': '#00C389',
    'digital_light': '#FFE04B',
    'white': '#FFFFFF',
}

# SVG логотип Neo Bank (адаптивный для темной темы)
logo_svg = """
<svg width="280" height="80" viewBox="0 0 280 80" xmlns="http://www.w3.org/2000/svg">
    <circle cx="45" cy="40" r="35" fill="none" stroke="#6B2D9D" stroke-width="8"/>
    <circle cx="50" cy="40" r="35" fill="white" stroke="none"/>
    <text x="25" y="52" font-family="Helvetica, Arial, sans-serif" font-size="28" font-weight="400" fill="#2D1B4E" class="logo-text">neo</text>
    <text x="95" y="52" font-family="Helvetica, Arial, sans-serif" font-size="28" font-weight="400" fill="#2D1B4E" class="logo-text">bank</text>
    <text x="95" y="68" font-family="Helvetica, Arial, sans-serif" font-size="12" font-weight="400" fill="#6B2D9D" class="logo-slogan">be in digital</text>
</svg>
"""

logo_b64 = base64.b64encode(logo_svg.encode('utf-8')).decode('utf-8')
logo_data_uri = f"data:image/svg+xml;base64,{logo_b64}"

if 'selected_metric' not in st.session_state:
    st.session_state.selected_metric = None
if 'selected_metric_label' not in st.session_state:
    st.session_state.selected_metric_label = None

st.image(logo_data_uri, width=280)
st.markdown('<div class="main-header">Оперативный мониторинг показателей</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Кликните на любой показатель для детального анализа</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-pattern"></div>', unsafe_allow_html=True)

# ==============================================================================
# КАСТОМНЫЙ CSS С CSS-ПЕРЕМЕННЫМИ (Правильная работа с темами)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
    
    /* CSS-ПЕРЕМЕННЫЕ ДЛЯ СВЕТЛОЙ ТЕМЫ (по умолчанию) */
    :root {
        --bg-primary: #FFFFFF;
        --bg-secondary: #F8F7FA;
        --bg-sidebar: #F8F7FA;
        --text-primary: #2D1B4E;
        --text-secondary: #6B2D9D;
        --text-accent: #7EDDD3;
        --border-color: #E0E0E0;
        --button-bg: linear-gradient(135deg, #F8F7FA 0%, #FFFFFF 100%);
        --button-border: #E0E0E0;
        --button-text: #2D1B4E;
        --button-hover-border: #6B2D9D;
        --detail-bg: #F8F7FA;
        --detail-border: #6B2D9D;
        --stat-card-bg: #FFFFFF;
        --stat-label-color: #6B2D9D;
        --stat-value-color: #2D1B4E;
        --logo-text-color: #2D1B4E;
        --logo-slogan-color: #6B2D9D;
        --brand-gradient: linear-gradient(90deg, #6B2D9D 0%, #7EDDD3 50%, #00C389 100%);
    }

    /* CSS-ПЕРЕМЕННЫЕ ДЛЯ ТЕМНОЙ ТЕМЫ */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #2D1B4E;
            --bg-secondary: #1E1235;
            --bg-sidebar: #1E1235;
            --text-primary: #FFFFFF;
            --text-secondary: #7EDDD3;
            --text-accent: #7EDDD3;
            --border-color: #6B2D9D;
            --button-bg: linear-gradient(135deg, #6B2D9D 0%, #4A1E6E 100%);
            --button-border: #7EDDD3;
            --button-text: #FFFFFF;
            --button-hover-border: #FFFFFF;
            --detail-bg: #3D2866;
            --detail-border: #7EDDD3;
            --stat-card-bg: #6B2D9D;
            --stat-label-color: #7EDDD3;
            --stat-value-color: #FFFFFF;
            --logo-text-color: #FFFFFF;
            --logo-slogan-color: #7EDDD3;
            --brand-gradient: linear-gradient(90deg, #7EDDD3 0%, #6B2D9D 50%, #00C389 100%);
        }
    }

    /* БАЗОВЫЕ СТИЛИ */
    .stApp, .main, .block-container { 
        background-color: var(--bg-primary) !important; 
        color: var(--text-primary) !important; 
    }
    
    h1, h2, h3, h4, h5, h6 { 
        font-family: 'Montserrat', sans-serif !important; 
        font-weight: 700 !important; 
        color: var(--text-primary) !important; 
    }
    
    .stMarkdown, p, div, label, span { 
        font-family: 'Helvetica', Arial, sans-serif !important; 
        font-weight: 400 !important; 
        color: var(--text-primary) !important; 
    }
    
    .main-header { 
        font-family: 'Montserrat', sans-serif !important; 
        font-size: 36px !important; 
        font-weight: 700 !important; 
        color: var(--text-primary) !important; 
        margin-top: 10px !important; 
        margin-bottom: 10px !important; 
    }
    
    .sub-header { 
        font-family: 'Helvetica', sans-serif !important; 
        font-size: 16px !important; 
        font-weight: 300 !important; 
        color: var(--text-secondary) !important; 
        margin-bottom: 30px !important; 
    }
    
    .stSidebar { 
        background-color: var(--bg-sidebar) !important; 
    }
    
    .stSidebar h2 { 
        color: var(--text-secondary) !important; 
        font-family: 'Montserrat', sans-serif !important; 
    }
    
    .brand-pattern { 
        height: 4px; 
        background: var(--brand-gradient); 
        margin: 20px 0; 
        border-radius: 2px; 
    }
    
    .footer { 
        text-align: center; 
        padding: 20px 0; 
        margin-top: 40px; 
        border-top: 1px solid var(--border-color); 
    }
    
    /* ВКЛАДКИ */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 24px; 
    }
    
    .stTabs [data-baseweb="tab"] { 
        font-family: 'Montserrat', sans-serif !important; 
        font-weight: 600 !important; 
        font-size: 16px !important; 
        color: var(--text-secondary) !important; 
        background-color: var(--bg-secondary) !important; 
        border-radius: 8px 8px 0 0 !important; 
        padding: 10px 24px !important; 
    }
    
    .stTabs [aria-selected="true"] { 
        background-color: #6B2D9D !important; 
        color: #FFFFFF !important; 
    }
    
    /* КНОПКИ */
    .stButton > button {
        background: var(--button-bg) !important;
        border: 2px solid var(--button-border) !important;
        border-radius: 12px !important;
        padding: 15px !important;
        margin: 8px 4px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
        width: 100% !important;
        font-family: 'Montserrat', sans-serif !important;
        color: var(--button-text) !important;
        font-size: 15px !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover { 
        border-color: var(--button-hover-border) !important; 
        box-shadow: 0 4px 12px rgba(126, 221, 211, 0.3) !important; 
        transform: translateY(-2px) !important; 
    }
    
    /* ДЕТАЛЬНЫЙ АНАЛИЗ */
    .detail-section { 
        background-color: var(--detail-bg); 
        border-radius: 16px; 
        padding: 30px; 
        margin-top: 30px; 
        border-left: 6px solid var(--detail-border); 
    }
    
    .detail-section h2 { 
        color: var(--text-secondary) !important; 
    }
    
    .stat-card { 
        background-color: var(--stat-card-bg); 
        border-radius: 12px; 
        padding: 20px; 
        text-align: center; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
    }
    
    .stat-label { 
        font-family: 'Helvetica', Arial, sans-serif; 
        font-size: 12px; 
        color: var(--stat-label-color) !important; 
        text-transform: uppercase; 
        letter-spacing: 1px; 
        margin-bottom: 8px; 
    }
    
    .stat-value { 
        font-family: 'Montserrat', sans-serif; 
        font-size: 22px; 
        font-weight: 700; 
        color: var(--stat-value-color) !important; 
    }
    
    /* SVG ЛОГОТИП */
    .logo-text {
        fill: var(--logo-text-color) !important;
    }
    
    .logo-slogan {
        fill: var(--logo-slogan-color) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. ЗАГРУЗКА ДАННЫХ
# ==============================================================================
def generate_mock_data():
    """Генератор тестовых данных"""
    np.random.seed(42)
    regions = ['Минск', 'Брестская обл.', 'Витебская обл.', 'Гомельская обл.', 'Гродненская обл.', 'Могилевская обл.']
    dates = pd.date_range(end=datetime.today(), periods=180).tolist() 
    
    data = []
    for region in regions:
        for date in dates:
            data.append({
                'date': date, 'region': region,
                'corp_loans': np.random.randint(100_000_000, 500_000_000),
                'corp_current_accounts': np.random.randint(50_000_000, 200_000_000),
                'corp_deposits': np.random.randint(150_000_000, 600_000_000),
                'corp_securities': np.random.randint(20_000_000, 100_000_000),
                'retail_loans': np.random.randint(50_000_000, 300_000_000),
                'retail_current_accounts': np.random.randint(30_000_000, 150_000_000),
                'retail_deposits': np.random.randint(100_000_000, 400_000_000)
            })
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df['requirements_to_economy'] = df['corp_loans'] + df['corp_current_accounts'] + df['corp_securities']
    return df

@st.cache_data(ttl=300)
def load_data_from_view():
    """Попытка загрузить данные из БД"""
    try:
        db_user = os.getenv('DB_USER', 'dashboard_reader')
        db_pass = os.getenv('DB_PASS', 'your_secure_password')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'bank_dwh')
        
        db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(db_url)
        
        query = """
            SELECT date, region, corp_loans, corp_current_accounts, corp_deposits, 
                   corp_securities, retail_loans, retail_current_accounts, retail_deposits, 
                   requirements_to_economy 
            FROM v_neo_bank_dashboard
        """
        df = pd.read_sql(query, engine)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.sidebar.warning("⚠️ Режим демо: подключение к БД не установлено. Используются тестовые данные.")
        return generate_mock_data()

df = load_data_from_view()

# ==============================================================================
# 3. БОКОВАЯ ПАНЕЛЬ И АГРЕГАЦИЯ
# ==============================================================================
st.sidebar.markdown("## ⚙️ Параметры отображения")

timeframe = st.sidebar.radio("Период агрегации:", options=["День", "Неделя", "Месяц"], index=1)
selected_region = st.sidebar.selectbox("Регион:", options=["Все регионы"] + list(df['region'].unique()))

if st.session_state.selected_metric is not None:
    if st.sidebar.button("🔄 Сбросить выбор показателя"):
        st.session_state.selected_metric = None
        st.session_state.selected_metric_label = None
        st.rerun()

if selected_region != "Все регионы":
    df_filtered = df[df['region'] == selected_region].copy()
else:
    agg_cols = ['corp_loans', 'corp_current_accounts', 'corp_deposits', 'corp_securities', 
                'retail_loans', 'retail_current_accounts', 'retail_deposits', 'requirements_to_economy']
    df_filtered = df.groupby('date')[agg_cols].sum().reset_index()
    df_filtered['region'] = 'Все регионы'

freq_map = {"День": "D", "Неделя": "W-MON", "Месяц": "ME"}
freq = freq_map[timeframe]
df_filtered = df_filtered.set_index('date')
df_agg = df_filtered.resample(freq).sum().reset_index()
df_agg['date_str'] = df_agg['date'].dt.strftime('%d.%m.%Y' if timeframe == "День" else '%b %Y')

def calc_delta(latest, prev):
    if prev == 0: return 0
    return ((latest - prev) / prev) * 100

# ==============================================================================
# 4. ФУНКЦИИ ОТОБРАЖЕНИЯ
# ==============================================================================
def clickable_metric(label, key, color='#6B2D9D'):
    latest_val = df_agg[key].iloc[-1]
    prev_val = df_agg[key].iloc[-2] if len(df_agg) > 1 else latest_val
    delta = calc_delta(latest_val, prev_val)
    
    delta_sign = "+" if delta >= 0 else ""
    delta_color = "#00C389" if delta >= 0 else "#F4364C"
    
    button_key = f"btn_{key}"
    clicked = st.button(label, key=button_key, use_container_width=True, help="Нажмите для детального анализа")
    
    st.markdown(f"""
    <div style="text-align: center; margin-top: 8px;">
        <div style="font-family: 'Montserrat', sans-serif; font-size: 20px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px;">
            {latest_val / 1_000_000:,.1f} млн BYN
        </div>
        <div style="font-family: 'Helvetica', Arial, sans-serif; font-size: 14px; font-weight: 600; color: {delta_color};">
            {delta_sign}{delta:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if clicked:
        st.session_state.selected_metric = key
        st.session_state.selected_metric_label = label
        st.rerun()

def show_detail_analysis(metric_key, metric_label):
    st.markdown("---")
    st.markdown(f"""
    <div class="detail-section">
        <h2 style="font-family: 'Montserrat', sans-serif; margin: 0;">📊 Детальный анализ: {metric_label}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    latest_val = df_agg[metric_key].iloc[-1]
    prev_val = df_agg[metric_key].iloc[-2] if len(df_agg) > 1 else latest_val
    min_val, max_val, mean_val = df_agg[metric_key].min(), df_agg[metric_key].max(), df_agg[metric_key].mean()
    delta = calc_delta(latest_val, prev_val)
    
    st.markdown("### Ключевая статистика за период")
    stat_cols = st.columns(5)
    stats = [
        ("Текущее значение", f"{latest_val / 1_000_000:,.1f} млн BYN"),
        ("Минимум", f"{min_val / 1_000_000:,.1f} млн BYN"),
        ("Максимум", f"{max_val / 1_000_000:,.1f} млн BYN"),
        ("Среднее", f"{mean_val / 1_000_000:,.1f} млн BYN"),
        ("Изменение к пред. периоду", f"{delta:+.2f}%")
    ]
    
    for i, (label, value) in enumerate(stats):
        with stat_cols[i]:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">{label}</div>
                <div class="stat-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### Динамика показателя")
    
    grid_color = '#E0E0E0'
    
    if selected_region == "Все регионы":
        fig_detail = go.Figure()
        fig_detail.add_trace(go.Scatter(
            x=df_agg['date_str'], y=df_agg[metric_key], name='Сумма по всем регионам',
            mode='lines+markers', line=dict(color=COLORS['bright_neo'], width=3), marker=dict(size=8, color=COLORS['bright_neo'])
        ))
        fig_detail.update_layout(
            font=dict(family="Helvetica, Arial", size=12), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            hovermode="x unified", height=500, margin=dict(l=60, r=40, t=60, b=60),
            xaxis=dict(gridcolor=grid_color, tickfont=dict(family="Helvetica", size=10), tickangle=-45),
            yaxis=dict(gridcolor=grid_color, title="Сумма (BYN)", tickfont=dict(family="Helvetica", size=11))
        )
        st.plotly_chart(fig_detail, use_container_width=True)
    else:
        region_data = df[df['region'] == selected_region].copy().set_index('date')
        region_agg = region_data.resample(freq)[metric_key].sum().reset_index()
        region_agg['date_str'] = region_agg['date'].dt.strftime('%d.%m.%Y' if timeframe == "День" else '%b %Y')
        
        fig_detail = go.Figure()
        fig_detail.add_trace(go.Scatter(
            x=region_agg['date_str'], y=region_agg[metric_key], name=selected_region,
            mode='lines+markers', line=dict(color=COLORS['bright_neo'], width=3), marker=dict(size=8, color=COLORS['bright_neo'])
        ))
        fig_detail.update_layout(
            font=dict(family="Helvetica, Arial", size=12), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            hovermode="x unified", height=500, margin=dict(l=60, r=40, t=60, b=60),
            xaxis=dict(gridcolor=grid_color, tickfont=dict(family="Helvetica", size=10), tickangle=-45),
            yaxis=dict(gridcolor=grid_color, title="Сумма (BYN)", tickfont=dict(family="Helvetica", size=11))
        )
        st.plotly_chart(fig_detail, use_container_width=True)
    
    st.markdown("### Разбивка по регионам (последний период)")
    recent_data = df[df['date'] >= df['date'].max() - timedelta(days=30)]
    
    if selected_region == "Все регионы":
        region_summary = recent_data.groupby('region')[metric_key].agg(['sum', 'mean', 'min', 'max']).reset_index()
        region_summary.columns = ['Регион', 'Сумма', 'Среднее', 'Минимум', 'Максимум']
        st.dataframe(
            region_summary.style.format({'Сумма': '{:,.0f}', 'Среднее': '{:,.0f}', 'Минимум': '{:,.0f}', 'Максимум': '{:,.0f}'}),
            use_container_width=True, height=250
        )
    else:
        st.info(f"📍 Отображаются данные только по региону: {selected_region}")

# ==============================================================================
# 5. ВКЛАДКИ
# ==============================================================================
tab_corp, tab_retail = st.tabs(["🏢 Корпоративный бизнес", "👤 Розничный бизнес"])

with tab_corp:
    st.markdown("### Ключевые показатели корпоративного блока")
    corp_metrics = {
        "💼 Кредиты корпоративные": "corp_loans",
        "🏦 Тек. счета корпоративные": "corp_current_accounts",
        "💰 Депозиты корпоративные": "corp_deposits",
        "📜 Ценные бумаги корп.": "corp_securities",
        "📊 Требования к экономике": "requirements_to_economy"
    }
    corp_cols = st.columns(len(corp_metrics))
    for i, (label, key) in enumerate(corp_metrics.items()):
        with corp_cols[i]:
            clickable_metric(label, key, COLORS['bright_neo'])
    
    if st.session_state.selected_metric in corp_metrics.values():
        show_detail_analysis(st.session_state.selected_metric, st.session_state.selected_metric_label)

with tab_retail:
    st.markdown("### Ключевые показатели розничного блока")
    retail_metrics = {
        "💳 Кредиты ФЛ": "retail_loans",
        "👛 Тек. счета ФЛ": "retail_current_accounts",
        "🏦 Вклады ФЛ": "retail_deposits"
    }
    retail_cols = st.columns(len(retail_metrics))
    for i, (label, key) in enumerate(retail_metrics.items()):
        with retail_cols[i]:
            clickable_metric(label, key, COLORS['digital_crimson'])
    
    if st.session_state.selected_metric in retail_metrics.values():
        show_detail_analysis(st.session_state.selected_metric, st.session_state.selected_metric_label)

# ==============================================================================
# 6. ФУТЕР
# ==============================================================================
st.markdown("---")
col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    st.image(logo_data_uri, width=200)

st.markdown(f"""
    <div class="footer">
        <div style='font-family: Helvetica, Arial, sans-serif; color: var(--text-secondary); font-size: 12px;'>
            Система мониторинга показателей Neo Bank | {datetime.now().strftime('%Y')}
        </div>
    </div>
""", unsafe_allow_html=True)