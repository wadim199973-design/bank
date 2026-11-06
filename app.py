import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64

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
logo_svg = """
<svg width="280" height="80" viewBox="0 0 280 80" xmlns="http://www.w3.org/2000/svg">
    <circle cx="45" cy="40" r="35" fill="none" stroke="#6B2D9D" stroke-width="8"/>
    <circle cx="50" cy="40" r="35" fill="white" stroke="none"/>
    <text x="25" y="52" font-family="Helvetica, Arial, sans-serif" font-size="28" font-weight="400" fill="#2D1B4E">neo</text>
    <text x="95" y="52" font-family="Helvetica, Arial, sans-serif" font-size="28" font-weight="400" fill="#2D1B4E">bank</text>
    <text x="95" y="68" font-family="Helvetica, Arial, sans-serif" font-size="12" font-weight="400" fill="#6B2D9D">be in digital</text>
</svg>
"""

logo_b64 = base64.b64encode(logo_svg.encode('utf-8')).decode('utf-8')
logo_data_uri = f"data:image/svg+xml;base64,{logo_b64}"

st.image(logo_data_uri, width=280)
st.markdown('<div class="main-header">Оперативный мониторинг показателей</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Динамика ключевых метрик с детализацией по регионам и периодам</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-pattern"></div>', unsafe_allow_html=True)

# Кастомный CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
    h1, h2, h3, h4, h5, h6 { font-family: 'Montserrat', sans-serif !important; font-weight: 700 !important; color: #2D1B4E !important; }
    .stMarkdown, p, div, label { font-family: 'Helvetica', Arial, sans-serif !important; font-weight: 400 !important; color: #2D1B4E !important; }
    .main-header { font-family: 'Montserrat', sans-serif !important; font-size: 36px !important; font-weight: 700 !important; color: #2D1B4E !important; margin-top: 10px !important; margin-bottom: 10px !important; }
    .sub-header { font-family: 'Helvetica', sans-serif !important; font-size: 16px !important; font-weight: 300 !important; color: #6B2D9D !important; margin-bottom: 30px !important; }
    .stSidebar { background-color: #F8F7FA !important; }
    .stSidebar h2 { color: #6B2D9D !important; font-family: 'Montserrat', sans-serif !important; }
    [data-testid="stMetricValue"] { font-family: 'Montserrat', sans-serif !important; font-weight: 700 !important; color: #2D1B4E !important; }
    [data-testid="stMetricLabel"] { font-family: 'Helvetica', sans-serif !important; font-weight: 400 !important; color: #6B2D9D !important; }
    .brand-pattern { height: 4px; background: linear-gradient(90deg, #6B2D9D 0%, #7EDDD3 50%, #00C389 100%); margin: 20px 0; border-radius: 2px; }
    .footer { text-align: center; padding: 20px 0; margin-top: 40px; border-top: 1px solid #E0E0E0; }
    
    /* Стилизация вкладок */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { 
        font-family: 'Montserrat', sans-serif !important; 
        font-weight: 600 !important; 
        font-size: 16px !important;
        color: #6B2D9D !important;
        background-color: #F8F7FA !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 24px !important;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #6B2D9D !important; 
        color: white !important; 
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
            data.append({
                'date': date,
                'region': region,
                # Корпоративный блок
                'corp_loans': np.random.randint(100_000_000, 500_000_000),
                'corp_current_accounts': np.random.randint(50_000_000, 200_000_000),
                'corp_deposits': np.random.randint(150_000_000, 600_000_000),
                'corp_securities': np.random.randint(20_000_000, 100_000_000),
                # Розничный блок
                'retail_loans': np.random.randint(50_000_000, 300_000_000),
                'retail_current_accounts': np.random.randint(30_000_000, 150_000_000),
                'retail_deposits': np.random.randint(100_000_000, 400_000_000)
            })
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    
    # !!! ВАЖНО: Расчет "Требований к экономике" прямо в коде !!!
    # Формула: Кредиты корп. + Текущие счета корп. + Ценные бумаги корп.
    df['requirements_to_economy'] = df['corp_loans'] + df['corp_current_accounts'] + df['corp_securities']
    
    return df

df = load_mock_data()

# 3. БОКОВАЯ ПАНЕЛЬ С ФИЛЬТРАМИ
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

# 4. ФИЛЬТРАЦИЯ И АГРЕГАЦИЯ ДАННЫХ
if selected_region != "Все регионы":
    df_filtered = df[df['region'] == selected_region].copy()
else:
    # Список всех числовых колонок для агрегации
    agg_cols = ['corp_loans', 'corp_current_accounts', 'corp_deposits', 'corp_securities', 
                'retail_loans', 'retail_current_accounts', 'retail_deposits', 'requirements_to_economy']
    
    df_filtered = df.groupby('date')[agg_cols].sum().reset_index()
    df_filtered['region'] = 'Все регионы'

freq_map = {"День": "D", "Неделя": "W-MON", "Месяц": "ME"}
freq = freq_map[timeframe]
df_filtered = df_filtered.set_index('date')

df_agg = df_filtered.resample(freq).sum().reset_index()
df_agg['date_str'] = df_agg['date'].dt.strftime('%d.%m.%Y' if timeframe == "День" else '%b %Y')

# Функция для расчета дельты
def calc_delta(latest, prev):
    if prev == 0: return 0
    return ((latest - prev) / prev) * 100

# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ОТОБРАЖЕНИЯ МЕТРИК
def display_metrics(data_dict, prefix=""):
    cols = st.columns(len(data_dict))
    for i, (label, key) in enumerate(data_dict.items()):
        latest_val = df_agg[key].iloc[-1]
        prev_val = df_agg[key].iloc[-2] if len(df_agg) > 1 else latest_val
        delta = calc_delta(latest_val, prev_val)
        
        with cols[i]:
            st.metric(
                label=label, 
                value=f"{latest_val / 1_000_000:,.1f} млн BYN",
                delta=f"{delta:+.1f}%"
            )

# ==========================================================
# 5. ВКЛАДКИ: КОРПОРАТИВНЫЙ И РОЗНИЧНЫЙ БИЗНЕС
# ==========================================================
tab_corp, tab_retail = st.tabs(["🏢 Корпоративный бизнес", "👤 Розничный бизнес"])

# ----------------------------------------------------------
# ВКЛАДКА 1: КОРПОРАТИВНЫЙ БИЗНЕС
# ----------------------------------------------------------
with tab_corp:
    st.markdown("### Ключевые показатели корпоративного блока")
    
    corp_metrics = {
        "💼 Кредиты корпоративные": "corp_loans",
        "🏦 Текущие счета корпоративные": "corp_current_accounts",
        "💰 Депозиты корпоративные": "corp_deposits",
        "📜 Ценные бумаги корпоративные": "corp_securities",
        "📊 Требования к экономике (расчетный)": "requirements_to_economy"
    }
    display_metrics(corp_metrics)
    
    st.markdown("---")
    col_chart1, col_chart2 = st.columns([2, 1])
    
    with col_chart1:
        st.markdown("#### Динамика: Требования к экономике vs Депозиты")
        fig_corp_trend = go.Figure()
        fig_corp_trend.add_trace(go.Scatter(
            x=df_agg['date_str'], y=df_agg['requirements_to_economy'],
            name='Требования к экономике', line=dict(color=COLORS['bright_neo'], width=3),
            mode='lines+markers', marker=dict(size=6, color=COLORS['bright_neo'])
        ))
        fig_corp_trend.add_trace(go.Scatter(
            x=df_agg['date_str'], y=df_agg['corp_deposits'],
            name='Депозиты корпоративные', line=dict(color=COLORS['digital_green'], width=3, dash='dash'),
            mode='lines+markers', marker=dict(size=6, color=COLORS['digital_green'])
        ))
        fig_corp_trend.update_layout(
            font=dict(family="Helvetica, Arial", size=12), plot_bgcolor='white', paper_bgcolor='white',
            hovermode="x unified", height=400, margin=dict(l=60, r=40, t=40, b=60),
            xaxis=dict(gridcolor='#E0E0E0'), yaxis=dict(gridcolor='#E0E0E0', title="Сумма (BYN)")
        )
        st.plotly_chart(fig_corp_trend, use_container_width=True)
        
    with col_chart2:
        st.markdown("#### Структура по регионам (Кредиты)")
        recent_data = df[df['date'] >= (datetime.today() - timedelta(days=30))]
        if selected_region == "Все регионы":
            region_data = recent_data.groupby('region')['corp_loans'].sum().reset_index()
            fig_corp_region = px.bar(
                region_data, x='corp_loans', y='region', orientation='h',
                color='corp_loans', color_continuous_scale=[COLORS['digital_tiffany'], COLORS['bright_neo'], COLORS['dark_neo']]
            )
            fig_corp_region.update_layout(
                plot_bgcolor='white', paper_bgcolor='white', height=400, margin=dict(l=120, r=20, t=20, b=40),
                xaxis=dict(gridcolor='#E0E0E0'), coloraxis_showscale=False, yaxis=dict(tickfont=dict(size=11))
            )
            st.plotly_chart(fig_corp_region, use_container_width=True)
        else:
            st.info(f"✅ Выбран регион: {selected_region}")

# ----------------------------------------------------------
# ВКЛАДКА 2: РОЗНИЧНЫЙ БИЗНЕС
# ----------------------------------------------------------
with tab_retail:
    st.markdown("### Ключевые показатели розничного блока")
    
    retail_metrics = {
        "💳 Кредиты ФЛ": "retail_loans",
        "👛 Текущие счета ФЛ": "retail_current_accounts",
        "🏦 Вклады ФЛ": "retail_deposits"
    }
    display_metrics(retail_metrics)
    
    st.markdown("---")
    col_chart1, col_chart2 = st.columns([2, 1])
    
    with col_chart1:
        st.markdown("#### Динамика: Кредиты ФЛ vs Вклады ФЛ")
        fig_retail_trend = go.Figure()
        fig_retail_trend.add_trace(go.Scatter(
            x=df_agg['date_str'], y=df_agg['retail_loans'],
            name='Кредиты ФЛ', line=dict(color=COLORS['digital_crimson'], width=3),
            mode='lines+markers', marker=dict(size=6, color=COLORS['digital_crimson'])
        ))
        fig_retail_trend.add_trace(go.Scatter(
            x=df_agg['date_str'], y=df_agg['retail_deposits'],
            name='Вклады ФЛ', line=dict(color=COLORS['digital_light'], width=3),
            mode='lines+markers', marker=dict(size=6, color=COLORS['digital_light'])
        ))
        fig_retail_trend.update_layout(
            font=dict(family="Helvetica, Arial", size=12), plot_bgcolor='white', paper_bgcolor='white',
            hovermode="x unified", height=400, margin=dict(l=60, r=40, t=40, b=60),
            xaxis=dict(gridcolor='#E0E0E0'), yaxis=dict(gridcolor='#E0E0E0', title="Сумма (BYN)")
        )
        st.plotly_chart(fig_retail_trend, use_container_width=True)
        
    with col_chart2:
        st.markdown("#### Структура по регионам (Кредиты ФЛ)")
        recent_data = df[df['date'] >= (datetime.today() - timedelta(days=30))]
        if selected_region == "Все регионы":
            region_data = recent_data.groupby('region')['retail_loans'].sum().reset_index()
            fig_retail_region = px.bar(
                region_data, x='retail_loans', y='region', orientation='h',
                color='retail_loans', color_continuous_scale=[COLORS['digital_tiffany'], COLORS['digital_crimson'], COLORS['dark_neo']]
            )
            fig_retail_region.update_layout(
                plot_bgcolor='white', paper_bgcolor='white', height=400, margin=dict(l=120, r=20, t=20, b=40),
                xaxis=dict(gridcolor='#E0E0E0'), coloraxis_showscale=False, yaxis=dict(tickfont=dict(size=11))
            )
            st.plotly_chart(fig_retail_region, use_container_width=True)
        else:
            st.info(f"✅ Выбран регион: {selected_region}")

# ==========================================================
# 6. ДЕТАЛЬНАЯ ТАБЛИЦА И ФУТЕР
# ==========================================================
st.markdown("---")
with st.expander("📊 Посмотреть детальные данные (Таблица)"):
    df_display = df_agg.copy()
    df_display['date'] = df_display['date'].dt.strftime('%d.%m.%Y')
    
    # Переименуем колонки для читаемости в таблице
    df_display = df_display.rename(columns={
        'corp_loans': 'Кредиты корп.', 'corp_current_accounts': 'Тек. счета корп.',
        'corp_deposits': 'Депозиты корп.', 'corp_securities': 'Ценные бумаги корп.',
        'requirements_to_economy': 'Треб. к экономике',
        'retail_loans': 'Кредиты ФЛ', 'retail_current_accounts': 'Тек. счета ФЛ',
        'retail_deposits': 'Вклады ФЛ'
    })
    
    st.dataframe(
        df_display.style.format({
            'Кредиты корп.': '{:,.0f}', 'Тек. счета корп.': '{:,.0f}', 'Депозиты корп.': '{:,.0f}',
            'Ценные бумаги корп.': '{:,.0f}', 'Треб. к экономике': '{:,.0f}',
            'Кредиты ФЛ': '{:,.0f}', 'Тек. счета ФЛ': '{:,.0f}', 'Вклады ФЛ': '{:,.0f}'
        }),
        use_container_width=True, height=300
    )

# Футер
col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    st.image(logo_data_uri, width=200)

st.markdown(f"""
    <div class="footer">
        <div style='font-family: Helvetica, Arial, sans-serif; color: {COLORS["bright_neo"]}; font-size: 12px;'>
            Система мониторинга показателей Neo Bank | {datetime.now().strftime('%Y')}
        </div>
    </div>
""", unsafe_allow_html=True)