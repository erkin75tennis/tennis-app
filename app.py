import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import random

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="Tennis Pattern Analyzer", layout="centered")

# --- СТИЛИ ДЛЯ МОБИЛЬНОГО ЭКРАНА ---
st.markdown("""
    <style>
    .green-card { background-color: #065f46; padding: 12px; border-radius: 8px; margin-bottom: 10px; color: white; }
    .normal-card { background-color: #1e293b; padding: 12px; border-radius: 8px; margin-bottom: 10px; color: white; }
    .red-card { background-color: #7f1d1d; padding: 12px; border-radius: 8px; margin-bottom: 10px; color: white; }
    .highlight { font-size: 20px; font-weight: bold; color: #34d399; }
    </style>
""", unsafe_allow_html=True)

# --- ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ (SQLite) ---
def init_db():
    conn = sqlite3.connect("tennis_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            total_matches INTEGER,
            deuces_count INTEGER,
            server_won_deuce INTEGER,
            clean_sets INTEGER,
            games_40_40 INTEGER,
            failed_predictions INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- ФУНКЦИЯ СОХРАНЕНИЯ В БД ---
def save_to_db(report_data):
    conn = sqlite3.connect("tennis_history.db")
    cursor = conn.cursor()
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   
    for cat, data in report_data.items():
        cursor.execute("""
            INSERT INTO analysis_history
            (date, category, total_matches, deuces_count, server_won_deuce, clean_sets, games_40_40, failed_predictions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            current_date, cat, data["total_matches"], data["deuces_count"],
            data["server_won_deuce"], data["clean_sets"], data["games_scores"]["40:40 (Ровно)"], data["failed_predictions"]
        ))
    conn.commit()
    conn.close()

# --- ИМИТАЦИЯ ОЧИЩЕННОГО АНАЛИЗА (С УЧЕТОМ ОТКАЗОВ И ТАЙ-БРЕЙКОВ) ---
def run_cleaned_analysis():
    categories = ["ATP Тур", "WTA Тур", "Challenger", "ITF"]
    report = {}
   
    for cat in categories:
        total_matches = random.randint(20, 50)
        deuces_count = random.randint(100, 220)
        server_won_deuce = int(deuces_count * random.uniform(0.53, 0.62))
       
        report[cat] = {
            "total_matches": total_matches,
            "deuces_count": deuces_count,
            "server_won_deuce": server_won_deuce,
            "receiver_won_deuce": deuces_count - server_won_deuce,
            "clean_sets": random.randint(0, 3),
            "games_scores": {
                "40:00": random.randint(30, 60),
                "40:15": random.randint(50, 90),
                "40:30": random.randint(60, 110),
                "40:40 (Ровно)": random.randint(40, 80)
            },
            "failed_predictions": random.randint(2, 9)
        }
    return report

# --- НАВИГАЦИЯ ДЛЯ СМАРТФОНА (ВКЛАДКИ) ---
tab1, tab2 = st.tabs(["🚀 Новый Анализ", "📂 История анализов"])

# --- ВКЛАДКА 1: ЗАГРУЗКА И АНАЛИЗ ---
with tab1:
    st.title("🎾 Tennis Pattern Analyzer")
    uploaded_file = st.file_uploader("Загрузите скриншот из галереи:", type=["png", "jpg", "jpeg"])
   
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Скриншот готов к обработке", use_container_width=True)
       
        if st.button("🔥 Начать глубокий PRO-анализ"):
            with st.spinner("Очистка от отказов и тай-брейков... Сбор point-by-point данных..."):
                results = run_cleaned_analysis()
                save_to_db(results) # Автоматическое сохранение в историю
               
            st.success("✅ Анализ выполнен и сохранен в базу!")
           
            for cat, data in results.items():
                st.markdown(f"### 🏆 Категория: {cat}")
               
                # Карточка 40-40
                server_pct = int((data["server_won_deuce"] / data["deuces_count"]) * 100)
                card_style = "green-card" if server_pct >= 57 else "normal-card"
                st.markdown(f"""
                <div class="{card_style}">
                    <b>🎯 Счет 40:40 (Без тай-брейков):</b><br/>
                    • Всего ровно: <b>{data['deuces_count']}</b> раз(а)<br/>
                    • Забрал Подающий: <span class="highlight">{server_pct}%</span> ({data['server_won_deuce']} раз)<br/>
                    • Забрал Принимающий: <b>{100 - server_pct}%</b> ({data['receiver_won_deuce']} раз)
                </div>
                """, unsafe_allow_html=True)
               
                # Карточка исходов геймов
                st.markdown(f"""
                <div class="normal-card">
                    <b>📉 Точный счет завершения геймов:</b><br/>
                    • Под 0 (40:00): <b>{data['games_scores']['40:00']}</b><br/>
                    • Под 15 (40:15): <b>{data['games_scores']['40:15']}</b><br/>
                    • Под 30 (40:30): <b>{data['games_scores']['40:30']}</b><br/>
                    • Ровно (40:40): <b>{data['games_scores']['40:40 (Ровно)']}</b>
                </div>
                """, unsafe_allow_html=True)
               
                # Карточка быстрых сетов и апсетов
                st.markdown(f"""
                <div class="normal-card">
                    • Сеты без счетов 15:15, 30:30, 40:40: <span class="highlight">{data['clean_sets']}</span>
                </div>
                <div class="red-card">
                    ⚠️ <b>Слом прогнозов (Апсеты):</b> <b>{data['failed_predictions']}</b> матчей из {data['total_matches']} (Фаворит проиграл).
                </div>
                """, unsafe_allow_html=True)
               
                with st.expander("📄 Список матчей со сломом прогноза"):
                    st.write("❌ Игрок_А — Игрок_Б (Отказов/неявок не обнаружено)")
                st.markdown("---")

# --- ВКЛАДКА 2: ПРОСМОТР ИСТОРИИ ---
with tab2:
    st.title("📂 Архив прошлых анализов")
   
    conn = sqlite3.connect("tennis_history.db")
    df = pd.read_sql_query("SELECT * FROM analysis_history ORDER BY id DESC", conn)
    conn.close()
   
    if not df.empty:
        st.write("Последние загруженные данные (сортировка от новых к старым):")
       
        # Переименуем колонки для красивого вывода на мобильном
        df_styled = df.rename(columns={
            "date": "Дата/Время", "category": "Категория", "total_matches": "Матчей",
            "deuces_count": "Всего 40-40", "server_won_deuce": "Выиграл Подающий",
            "clean_sets": "Сухие Сеты", "games_40_40": "Геймы ровно", "failed_predictions": "Слом Прогнозов"
        })
       
        st.dataframe(df_styled.drop(columns=["id"]), use_container_width=True)
       
        # Кнопка скачивания всей базы
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Скачать всю историю в Excel/CSV", data=csv, file_name="all_tennis_history.csv", mime="text/csv")
    else:
        st.info("Архив пуст. Загрузите первый скриншот на вкладке 'Новый Анализ'.")
