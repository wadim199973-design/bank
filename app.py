import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# 1. НАСТРОЙКА СТРАНИЦЫ
st.set_page_config(page_title="Банковский Дашборд", layout="wide", page_icon="🏦")

# 2. ГЕНЕРАЦИЯ ТЕСТОВЫХ ДАННЫХ (В реальности здесь будет pd.read_sql)
@st.cache_data # Кэшируем данные, чтобы не перегенерировать при каждом клике
def load_mock_data():
    np.random.seed(42)
    regions = ['Минск', 'Брестская обл.', 'Витебская обл.', 'Гомельская обл.', 'Гродненская обл.', 'Могилевская обл.']
    dates = pd.date_range(end=datetime.today(), periods=180).tolist() # Последние 180 дней
    
    data = []
    for region in regions:
        for date in dates:
            # Имитация реалистичных финансовых данных
            base_portfolio = np.random.randint(50_000_000, 200_000_000) # Кредитный портфель
            npl_ratio = np.random.uniform(1.5, 8.5) # Доля просрочки (NPL), %
            nii = base_portfolio * np.random.uniform(0.001, 0.003) # Чистый процентный доход
            
            data.append({
                'date': date,
                'region': region,
                'portfolio_volume': base_portfolio,
                'npl_ratio': npl_ratio,
                'nii': nii
            })
    
    df = pd.DataFrame(data)
    # ВАЖНО: Оставляем как pandas datetime, НЕ конвертируем в .dt.date
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_mock_data()

# 3. ИНТЕРФЕЙС И ФИЛЬТРЫ (САЙДБАР)
st.sidebar.header("⚙️ Настройки отображения")

# Фильтр по таймфрейму
timeframe = st.sidebar.radio(
    "Выберите период агрегации:",
    options=["День", "Неделя", "Месяц"],
    index=1 # По умолчанию неделя
)

# Фильтр по региону
selected_region = st.sidebar.selectbox(
    "Выберите регион:",
    options=["Все регионы"] + list(df['region'].unique())
)

st.title("🏦 Оперативный мониторинг показателей банка")
st.markdown("Динамика ключевых метрик с детализацией по регионам и периодам.")
st.markdown("---")

# 4. БИЗНЕС-ЛОГИКА: АГРЕГАЦИЯ ДАННЫХ
# Фильтрация по региону
if selected_region != "Все регионы":
    df_filtered = df[df['region'] == selected_region].copy()
else:
    df_filtered = df.groupby('date').agg({
        'portfolio_volume': 'sum',
        'npl_ratio': 'mean', # Средневзвешенную лучше считать в SQL, для MVP берем среднее
        'nii': 'sum'
    }).reset_index()
    # Добавим фиктивный регион для корректной работы графиков
    df_filtered['region'] = 'Все регионы'

# Агрегация по времени (Resample)
freq_map = {"День": "D", "Неделя": "W-MON", "Месяц": "ME"}
freq = freq_map[timeframe]

# Устанавливаем дату как индекс для ресемпла
df_filtered = df_filtered.set_index('date')

# Агрегируем данные
df_agg = df_filtered.resample(freq).agg({
    'portfolio_volume': 'sum',
    'npl_ratio': 'mean',
    'nii': 'sum'
}).reset_index()

# Форматируем дату для красивого отображения на графике (ПОСЛЕ ресемпла)
df_agg['date_str'] = df_agg['date'].dt.strftime('%d.%m.%Y' if timeframe == "День" else '%b %Y')

# 5. ВИЗУАЛИЗАЦИЯ: KPI КАРТОЧКИ (ВЕРХНИЙ УРОВЕНЬ)
# Берем последние доступные данные из агрегированного набора
latest = df_agg.iloc[-1]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="💰 Кредитный портфель", 
        value=f"{latest['portfolio_volume'] / 1_000_000:,.1f} млн BYN",
        delta=f"{np.random.uniform(-2, 5):.1f}%" # Имитация дельты к прошлому периоду
    )
with col2:
    st.metric(
        label="⚠️ Доля просрочки (NPL)", 
        value=f"{latest['npl_ratio']:.2f}%",
        delta=f"{np.random.uniform(-0.5, 0.5):.2f}%",
        delta_color="inverse" # Красный цвет при росте (ухудшении)
    )
with col3:
    st.metric(
        label="📈 Чистый процентный доход (NII)", 
        value=f"{latest['nii'] / 1_000:,.1f} тыс BYN",
        delta=f"{np.random.uniform(-1, 3):.1f}%"
    )

st.markdown("---")

# 6. ВИЗУАЛИЗАЦИЯ: ГРАФИКИ
col_chart1, col_chart2 = st.columns([2, 1]) # Левая колонка шире

with col_chart1:
    st.subheader(f"Динамика показателей ({timeframe})")
    # График с двумя осями Y для портфеля и NII
    fig_trend = px.line(
        df_agg, x='date_str',  # Используем отформатированную строку
        y=['portfolio_volume', 'nii'],
        labels={'value': 'Сумма (BYN)', 'date_str': 'Период', 'variable': 'Показатель'},
        title="Динамика Портфеля и Дохода"
    )
    fig_trend.update_layout(legend_title_text='Метрика', hovermode="x unified")
    st.plotly_chart(fig_trend, use_container_width=True)

with col_chart2:
    st.subheader("Разбивка по регионам (Текущий период)")
    # Для региональной разбивки берем исходные данные за последние 30 дней, чтобы график был репрезентативным
    recent_data = df[df['date'] >= (datetime.today() - timedelta(days=30))]
    
    if selected_region == "Все регионы":
        fig_region = px.bar(
            recent_data.groupby('region')['portfolio_volume'].sum().reset_index(),
            x='portfolio_volume', y='region', orientation='h',
            labels={'portfolio_volume': 'Объем портфеля (BYN)', 'region': 'Регион'},
            color='portfolio_volume',
            color_continuous_scale='Blues'
        )
        fig_region.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_region, use_container_width=True)
    else:
        st.info(f"Выбран конкретный регион: {selected_region}. Детализация по регионам скрыта.")

# 7. ТАБЛИЦА СЫРЫХ ДАННЫХ (для глубокого анализа)
with st.expander("📊 Посмотреть детальные данные (Таблица)"):
    # Создаем копию для отображения с отформатированной датой
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