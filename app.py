import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# ==============================================================================
# 1. НАСТРОЙКА СТРАНИЦЫ
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

# Инициализация session_state
if 'selected_metric' not in st.session_state:
    st.session_state.selected_metric = None
if 'selected_metric_label' not in st.session_state:
    st.session_state.selected_metric_label = None
if 'dark_logo' not in st.session_state:
    st.session_state.dark_logo = False

# ==============================================================================
# CSS СТИЛИ (без широких селекторов, чтобы не ломать меню Streamlit)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

    h1, h2, h3, h4, h5, h6 { 
        font-family: 'Montserrat', sans-serif !important; 
        font-weight: 700 !important; 
    }

    .main-header { 
        font-family: 'Montserrat', sans-serif !important; 
        font-size: 34px !important; 
        font-weight: 700 !important; 
        margin-top: 6px !important; 
        margin-bottom: 6px !important; 
    }
    .sub-header { 
        font-family: 'Helvetica', Arial, sans-serif !important; 
        font-size: 15px !important; 
        font-weight: 300 !important; 
        opacity: .75; 
        margin-bottom: 24px !important; 
    }

    .brand-pattern { 
        height: 4px; 
        background: linear-gradient(90deg, #6B2D9D 0%, #7EDDD3 50%, #00C389 100%); 
        margin: 18px 0; 
        border-radius: 2px; 
    }
    .footer { 
        text-align: center; 
        padding: 18px 0; 
        margin-top: 36px; 
        border-top: 1px solid rgba(128,128,128,0.3); 
    }

    .stTabs [data-baseweb="tab-list"] { 
        gap: 18px; 
    }
    .stTabs [data-baseweb="tab"] { 
        font-family: 'Montserrat', sans-serif !important; 
        font-weight: 600 !important; 
        font-size: 15px !important; 
        background-color: rgba(128,128,128,0.10) !important; 
        border-radius: 8px 8px 0 0 !important; 
        padding: 8px 20px !important; 
    }
    .stTabs [aria-selected="true"] { 
        background-color: #6B2D9D !important; 
        color: #FFFFFF !important; 
    }

    .stButton > button { 
        border-radius: 12px !important; 
        padding: 14px 10px !important; 
        width: 100% !important; 
        font-family: 'Montserrat', sans-serif !important; 
        font-weight: 600 !important; 
        font-size: 14px !important; 
        transition: all .2s ease !important; 
    }
    .stButton > button:hover { 
        transform: translateY(-2px) !important; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important; 
    }

    .detail-section { 
        background: rgba(128,128,128,0.12); 
        border-radius: 16px; 
        padding: 26px; 
        margin-top: 24px; 
        border-left: 6px solid #7EDDD3; 
    }
    .stat-card { 
        background: rgba(128,128,128,0.15); 
        border-radius: 12px; 
        padding: 16px; 
        text-align: center; 
    }
    .stat-label { 
        font-family: 'Helvetica', Arial, sans-serif; 
        font-size: 11px; 
        opacity: .7; 
        text-transform: uppercase; 
        letter-spacing: 1px; 
        margin-bottom: 6px; 
        color: inherit; 
    }
    .stat-value { 
        font-family: 'Montserrat', sans-serif; 
        font-size: 20px; 
        font-weight: 700; 
        color: inherit; 
    }

    [data-testid="stToolbar"] {
        overflow: visible !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# ФУНКЦИЯ ЛОГОТИПА
# ==============================================================================
def render_logo():
    is_dark = st.session_state.dark_logo
    crescent = '#FFFFFF' if is_dark else '#6B2D9D'
    text     = '#FFFFFF' if is_dark else '#2D1B4E'
    st.markdown(f"""
    <svg width="280" height="80" viewBox="0 0 280 80" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <mask id="neo-crescent">
                <circle cx="45" cy="40" r="35" fill="white"/>
                <circle cx="50" cy="40" r="35" fill="black"/>
            </mask>
        </defs>
        <circle cx="45" cy="40" r="35" fill="{crescent}" mask="url(#neo-crescent)"/>
        <text x="25" y="52" font-family="Helvetica, Arial, sans-serif" font-size="28" font-weight="400" fill="{text}">neo</text>
        <text x="95" y="52" font-family="Helvetica, Arial, sans-serif" font-size="28" font-weight="400" fill="{text}">bank</text>
    </svg>
    """, unsafe_allow_html=True)

# Отображаем логотип с переключателем рядом
col_logo, col_toggle = st.columns([4, 1])
with col_logo:
    render_logo()
with col_toggle:
    if st.toggle("🌙", key="dark_logo", help="Белый логотип для тёмной темы"):
        st.rerun()

st.markdown('<div class="main-header">Оперативный мониторинг показателей</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Кликните на любой показатель для детального анализа</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-pattern"></div>', unsafe_allow_html=True)

# ==============================================================================
# 2. ДАННЫЕ
# ==============================================================================
def generate_mock_data():
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
    try:
        from sqlalchemy import create_engine
        db_user = os.getenv('DB_USER', 'dashboard_reader')
        db_pass = os.getenv('DB_PASS', 'change_me')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'bank_dwh')
        engine = create_engine(f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")
        query = """
            SELECT date, region, corp_loans, corp_current_accounts, corp_deposits,
                   corp_securities, retail_loans, retail_current_accounts, retail_deposits,
                   requirements_to_economy
            FROM v_neo_bank_dashboard
        """
        df = pd.read_sql(query, engine)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception:
        st.sidebar.warning("⚠️ Демо-режим: БД недоступна, показаны тестовые данные.")
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
def clickable_metric(label, key):
    latest_val = df_agg[key].iloc[-1]
    prev_val = df_agg[key].iloc[-2] if len(df_agg) > 1 else latest_val
    delta = calc_delta(latest_val, prev_val)
    delta_sign = "+" if delta >= 0 else ""
    delta_color = "#00C389" if delta >= 0 else "#F4364C"

    clicked = st.button(label, key=f"btn_{key}", use_container_width=True, help="Детальный анализ")

    st.markdown(f"""
    <div style="text-align:center; margin-top:6px;">
        <div style="font-family:'Montserrat',sans-serif; font-size:19px; font-weight:700; color:inherit; margin-bottom:2px;">
            {latest_val / 1_000_000:,.1f} млн BYN
        </div>
        <div style="font-family:'Helvetica',sans-serif; font-size:13px; font-weight:600; color:{delta_color};">
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
        <h2 style="font-family:'Montserrat',sans-serif; margin:0;">📊 Детальный анализ: {metric_label}</h2>
    </div>
    """, unsafe_allow_html=True)

    latest_val = df_agg[metric_key].iloc[-1]
    prev_val = df_agg[metric_key].iloc[-2] if len(df_agg) > 1 else latest_val
    min_val, max_val, mean_val = df_agg[metric_key].min(), df_agg[metric_key].max(), df_agg[metric_key].mean()
    delta = calc_delta(latest_val, prev_val)

    st.markdown("### Ключевая статистика за период")
    stat_cols = st.columns(5)
    stats = [
        ("Текущее", f"{latest_val/1e6:,.1f} млн"), ("Минимум", f"{min_val/1e6:,.1f} млн"),
        ("Максимум", f"{max_val/1e6:,.1f} млн"), ("Среднее", f"{mean_val/1e6:,.1f} млн"),
        ("Δ к пред.", f"{delta:+.2f}%")
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

    chart_layout = dict(
        font=dict(family="Helvetica, Arial", size=12, color="#2D1B4E"),
        plot_bgcolor='white', paper_bgcolor='white',
        hovermode="x unified", height=480, margin=dict(l=60, r=40, t=40, b=80),
        xaxis=dict(gridcolor='#E0E0E0', tickfont=dict(color="#2D1B4E", size=10), tickangle=-45),
        yaxis=dict(gridcolor='#E0E0E0', title="Сумма (BYN)", tickfont=dict(color="#2D1B4E", size=11))
    )

    fig_detail = go.Figure()
    if selected_region == "Все регионы":
        fig_detail.add_trace(go.Scatter(
            x=df_agg['date_str'], y=df_agg[metric_key], name='Сумма по всем регионам',
            mode='lines+markers', line=dict(color=COLORS['bright_neo'], width=3),
            marker=dict(size=7, color=COLORS['bright_neo'])
        ))
    else:
        region_data = df[df['region'] == selected_region].copy().set_index('date')
        region_agg = region_data.resample(freq)[metric_key].sum().reset_index()
        region_agg['date_str'] = region_agg['date'].dt.strftime('%d.%m.%Y' if timeframe == "День" else '%b %Y')
        fig_detail.add_trace(go.Scatter(
            x=region_agg['date_str'], y=region_agg[metric_key], name=selected_region,
            mode='lines+markers', line=dict(color=COLORS['bright_neo'], width=3),
            marker=dict(size=7, color=COLORS['bright_neo'])
        ))
    fig_detail.update_layout(**chart_layout)
    st.plotly_chart(fig_detail, use_container_width=True)

    st.markdown("### Разбивка по регионам (последний период)")
    recent_data = df[df['date'] >= df['date'].max() - timedelta(days=30)]
    if selected_region == "Все регионы":
        region_summary = recent_data.groupby('region')[metric_key].agg(['sum', 'mean', 'min', 'max']).reset_index()
        region_summary.columns = ['Регион', 'Сумма', 'Среднее', 'Минимум', 'Максимум']
        st.dataframe(region_summary.style.format({
            'Сумма': '{:,.0f}', 'Среднее': '{:,.0f}', 'Минимум': '{:,.0f}', 'Максимум': '{:,.0f}'
        }), use_container_width=True, height=250)
    else:
        st.info(f"📍 Данные только по региону: {selected_region}")

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
    cols = st.columns(len(corp_metrics))
    for i, (label, key) in enumerate(corp_metrics.items()):
        with cols[i]:
            clickable_metric(label, key)
    if st.session_state.selected_metric in corp_metrics.values():
        show_detail_analysis(st.session_state.selected_metric, st.session_state.selected_metric_label)

with tab_retail:
    st.markdown("### Ключевые показатели розничного блока")
    retail_metrics = {
        "💳 Кредиты ФЛ": "retail_loans",
        "👛 Тек. счета ФЛ": "retail_current_accounts",
        "🏦 Вклады ФЛ": "retail_deposits"
    }
    cols = st.columns(len(retail_metrics))
    for i, (label, key) in enumerate(retail_metrics.items()):
        with cols[i]:
            clickable_metric(label, key)
    if st.session_state.selected_metric in retail_metrics.values():
        show_detail_analysis(st.session_state.selected_metric, st.session_state.selected_metric_label)

# ==============================================================================
# 6. ФУТЕР
# ==============================================================================
st.markdown("---")
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    render_logo()
st.markdown(f"""
    <div class="footer">
        <div style="font-family:Helvetica,sans-serif; font-size:12px; opacity:.7; color:inherit;">
            Система мониторинга показателей Neo Bank | {datetime.now().strftime('%Y')}
        </div>
    </div>
""", unsafe_allow_html=True)