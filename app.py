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

# Инициализация session_state
if 'selected_metric' not in st.session_state:
    st.session_state.selected_metric = None
if 'selected_metric_label' not in st.session_state:
    st.session_state.selected_metric_label = None

st.image(logo_data_uri, width=280)
st.markdown('<div class="main-header">Оперативный мониторинг показателей</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Кликните на любой показатель для детального анализа</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-pattern"></div>', unsafe_allow_html=True)

# Кастомный CSS
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
    
    .brand-pattern { 
        height: 4px; 
        background: linear-gradient(90deg, #6B2D9D 0%, #7EDDD3 50%, #00C389 100%); 
        margin: 20px 0; 
        border-radius: 2px; 
    }
    
    .footer { 
        text-align: center; 
        padding: 20px 0; 
        margin-top: 40px; 
        border-top: 1px solid #E0E0E0; 
    }
    
    .stTabs [data-baseweb="tab-list"] { 
        gap: 24px; 
    }
    
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
    
    /* Стили для кнопок-метрик */
    .stButton > button {
        background: linear-gradient(135deg, #F8F7FA 0%, #FFFFFF 100%) !important;
        border: 2px solid #E0E0E0 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin: 8px 4px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
        width: 100% !important;
        font-family: 'Helvetica', Arial, sans-serif !important;
        color: #2D1B4E !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
    }
    
    .stButton > button:hover {
        border-color: #6B2D9D !important;
        box-shadow: 0 4px 12px rgba(107, 45, 157, 0.15) !important;
        transform: translateY(-2px) !important;
    }
    
    .detail-section {
        background: #F8F7FA;
        border-radius: 16px;
        padding: 30px;
        margin-top: 30px;
        border-left: 6px solid #6B2D9D;
    }
    
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .stat-label {
        font-family: 'Helvetica', Arial, sans-serif;
        font-size: 12px;
        color: #6B2D9D;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    
    .stat-value {
        font-family: 'Montserrat', sans-serif;
        font-size: 22px;
        font-weight: 700;
        color: #2D1B4E;
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
    
    # Расчет "Требований к экономике"
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

# Кнопка сброса выбора
if st.session_state.selected_metric is not None:
    if st.sidebar.button("🔄 Сбросить выбор показателя"):
        st.session_state.selected_metric = None
        st.session_state.selected_metric_label = None
        st.rerun()

# 4. ФИЛЬТРАЦИЯ И АГРЕГАЦИЯ ДАННЫХ
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

# Функция расчета дельты
def calc_delta(latest, prev):
    if prev == 0: return 0
    return ((latest - prev) / prev) * 100

# ФУНКЦИЯ КЛИКАБЕЛЬНОЙ КНОПКИ-МЕТРИКИ
def clickable_metric(label, key, color='#6B2D9D'):
    """Создает кликабельную кнопку-метрику"""
    latest_val = df_agg[key].iloc[-1]
    prev_val = df_agg[key].iloc[-2] if len(df_agg) > 1 else latest_val
    delta = calc_delta(latest_val, prev_val)
    
    # Определяем знак дельты
    delta_sign = "+" if delta >= 0 else ""
    
    # Формируем текст кнопки
    button_text = f"{label}\n\n{latest_val / 1_000_000:,.1f} млн BYN\n\n{delta_sign}{delta:.1f}%"
    
    # Создаем кнопку
    button_key = f"btn_{key}"
    clicked = st.button(
        button_text, 
        key=button_key, 
        use_container_width=True,
        help="Нажмите для детального анализа"
    )
    
    if clicked:
        st.session_state.selected_metric = key
        st.session_state.selected_metric_label = label
        st.rerun()

# ФУНКЦИЯ ОТОБРАЖЕНИЯ ДЕТАЛЬНОГО АНАЛИЗА
# ==========================================================
# ФУНКЦИЯ ОТОБРАЖЕНИЯ ДЕТАЛЬНОГО АНАЛИЗА
# ==========================================================
def show_detail_analysis(metric_key, metric_label):
    """Показывает детальный график и статистику для выбранной метрики"""
    
    st.markdown("---")
    st.markdown(f"""
    <div class="detail-section">
        <h2 style="color: #6B2D9D; font-family: 'Montserrat', sans-serif; margin: 0;">
            📊 Детальный анализ: {metric_label}
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # --- СТАТИСТИКА ---
    latest_val = df_agg[metric_key].iloc[-1]
    prev_val = df_agg[metric_key].iloc[-2] if len(df_agg) > 1 else latest_val
    min_val = df_agg[metric_key].min()
    max_val = df_agg[metric_key].max()
    mean_val = df_agg[metric_key].mean()
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
    
    # --- ГРАФИК ДИНАМИКИ ---
    st.markdown("### Динамика показателя")
    
    if selected_region == "Все регионы":
        # Показываем ОДНУ суммарную линию по всем регионам
        fig_detail = go.Figure()
        fig_detail.add_trace(go.Scatter(
            x=df_agg['date_str'],
            y=df_agg[metric_key],
            name='Сумма по всем регионам',
            mode='lines+markers',
            line=dict(color=COLORS['bright_neo'], width=3),
            marker=dict(size=8, color=COLORS['bright_neo'])
        ))
        
        fig_detail.update_layout(
            font=dict(family="Helvetica, Arial", size=12),
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode="x unified",
            height=500,
            margin=dict(l=60, r=40, t=60, b=60),
            xaxis=dict(gridcolor='#E0E0E0', tickfont=dict(family="Helvetica", size=10), tickangle=-45),
            yaxis=dict(gridcolor='#E0E0E0', title="Сумма (BYN)", tickfont=dict(family="Helvetica", size=11))
        )
        
        st.plotly_chart(fig_detail, use_container_width=True)
        
    else:
        # Если выбран конкретный регион - показываем только его динамику
        region_data = df[df['region'] == selected_region].copy()
        region_data = region_data.set_index('date')
        region_agg = region_data.resample(freq)[metric_key].sum().reset_index()
        region_agg['date_str'] = region_agg['date'].dt.strftime('%d.%m.%Y' if timeframe == "День" else '%b %Y')
        
        fig_detail = go.Figure()
        fig_detail.add_trace(go.Scatter(
            x=region_agg['date_str'],
            y=region_agg[metric_key],
            name=selected_region,
            mode='lines+markers',
            line=dict(color=COLORS['bright_neo'], width=3),
            marker=dict(size=8, color=COLORS['bright_neo'])
        ))
        
        fig_detail.update_layout(
            font=dict(family="Helvetica, Arial", size=12),
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode="x unified",
            height=500,
            margin=dict(l=60, r=40, t=60, b=60),
            xaxis=dict(gridcolor='#E0E0E0', tickfont=dict(family="Helvetica", size=10), tickangle=-45),
            yaxis=dict(gridcolor='#E0E0E0', title="Сумма (BYN)", tickfont=dict(family="Helvetica", size=11))
        )
        
        st.plotly_chart(fig_detail, use_container_width=True)
    
    # --- ТАБЛИЦА ПО РЕГИОНАМ ---
    st.markdown("### Разбивка по регионам (последний период)")
    
    recent_data = df[df['date'] >= df['date'].max() - timedelta(days=30)]
    
    if selected_region == "Все регионы":
        region_summary = recent_data.groupby('region')[metric_key].agg(['sum', 'mean', 'min', 'max']).reset_index()
        region_summary.columns = ['Регион', 'Сумма', 'Среднее', 'Минимум', 'Максимум']
        
        st.dataframe(
            region_summary.style.format({
                'Сумма': '{:,.0f}',
                'Среднее': '{:,.0f}',
                'Минимум': '{:,.0f}',
                'Максимум': '{:,.0f}'
            }),
            use_container_width=True,
            height=250
        )
    else:
        st.info(f"📍 Отображаются данные только по региону: {selected_region}")

# 5. ВКЛАДКИ: КОРПОРАТИВНЫЙ И РОЗНИЧНЫЙ БИЗНЕС
tab_corp, tab_retail = st.tabs(["🏢 Корпоративный бизнес", "👤 Розничный бизнес"])

# ВКЛАДКА 1: КОРПОРАТИВНЫЙ БИЗНЕС
with tab_corp:
    st.markdown("### Ключевые показатели корпоративного блока")
    
    corp_metrics = {
        "💼 Кредиты корпоративные": "corp_loans",
        "🏦 Тек. счета корпоративные": "corp_current_accounts",
        "💰 Депозиты корпоративные": "corp_deposits",
        "📜 Ценные бумаги корп.": "corp_securities",
        "📊 Требования к экономике": "requirements_to_economy"
    }
    
    # Создаем кнопки в строку
    corp_cols = st.columns(len(corp_metrics))
    for i, (label, key) in enumerate(corp_metrics.items()):
        with corp_cols[i]:
            clickable_metric(label, key, COLORS['bright_neo'])
    
    # Показываем детальный анализ
    if st.session_state.selected_metric in corp_metrics.values():
        show_detail_analysis(
            st.session_state.selected_metric, 
            st.session_state.selected_metric_label
        )

# ВКЛАДКА 2: РОЗНИЧНЫЙ БИЗНЕС
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
    
    # Показываем детальный анализ
    if st.session_state.selected_metric in retail_metrics.values():
        show_detail_analysis(
            st.session_state.selected_metric, 
            st.session_state.selected_metric_label
        )

# 6. ФУТЕР
st.markdown("---")

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