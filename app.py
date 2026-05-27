import streamlit as st
import os
from dotenv import load_dotenv
from modules import infrastructure, ai_engine, pdf_generator, deep_audit

load_dotenv()


# Налаштування сторінки
st.set_page_config(
    page_title="Платформа аналізу безпеки",
    page_icon="🛡️",
    layout="wide"
)

# --- ДИЗАЙН ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Montserrat:wght@200;300;400;500;600&display=swap');
    
    .stApp {
        background-color: #080808 !important;
        color: #dcdcdc !important;
        font-family: 'Montserrat', sans-serif !important;
    }
    
    h1, h2, h3, [data-testid="stHeader"] {
        color: #ffffff !important;
        font-family: 'Playfair Display', serif !important;
        font-weight: 400 !important;
        letter-spacing: 1.5px !important;
    }
    
    .premium-card {
        background: linear-gradient(145deg, #111111, #161616);
        border: 1px solid #222222;
        border-radius: 12px;
        padding: 25px;
        margin-top: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    
    div[data-testid="element-container"] .stTextInput input {
        background-color: #121212 !important;
        color: #ffffff !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 6px !important;
        padding: 12px !important;
    }
    
    .stButton>button { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 2px !important;
        font-size: 12px !important;
        border-radius: 4px !important; 
        border: 1px solid #ffffff !important;
        padding: 14px 28px !important;
        width: 100% !important;
        margin-top: 15px;
    }
    .stButton>button:hover { 
        background-color: #000000 !important; 
        color: #ffffff !important; 
        box-shadow: 0 0 25px rgba(255, 255, 255, 0.15) !important;
    }
    
    button[data-baseweb="tab"] {
        color: #888888 !important;
        font-family: 'Montserrat', sans-serif !important;
        padding: 12px 24px !important;
    }
    button[aria-selected="true"] {
        color: #ffffff !important;
        border-bottom: 2px solid #ffffff !important;
    }
    
    div[data-testid="stExpander"] {
        background-color: #111111 !important;
        border: 1px solid #222222 !important;
        border-radius: 8px !important;
    }
    
    .status-badge {
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 15px;
    }
    .badge-red { background-color: rgba(231, 76, 60, 0.1); color: #e74c3c; border: 1px solid #e74c3c; }
    .badge-yellow { background-color: rgba(241, 196, 15, 0.1); color: #f1c40f; border: 1px solid #f1c40f; }
    .badge-green { background-color: rgba(46, 204, 113, 0.1); color: #2ecc71; border: 1px solid #2ecc71; }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


# --- 1. ПЕРЕВІРКА КОНФІДЕНЦІЙНОСТІ (GDPR) ---
if "gdpr_accepted" not in st.session_state:
    st.session_state.gdpr_accepted = False

if not st.session_state.gdpr_accepted:
    st.markdown("""
        <style>
        .stApp { background-color: #080808 !important; color: #dcdcdc !important; }
        .gdpr-box {
            background: linear-gradient(145deg, #111111, #161616);
            border: 1px solid #222222;
            border-radius: 12px;
            padding: 30px;
            margin: 50px auto;
            max-width: 650px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }
        h2 { color: #ffffff !important; font-family: 'Playfair Display', serif; font-weight: 400; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(
        "<div class='gdpr-box'>"
        "<h2>🔒 ПОЛІТИКА КОНФІДЕНЦІЙНОСТІ </h2>"
        "<p style='color: #888888; font-size: 14px; margin-bottom: 25px;'>Платформа відповідає стандартам цифрової гігієни та європейським регламентам захисту персональних даних.</p>"
        "<p style='font-size: 14px; line-height: 1.6;'>Усі технічні дані сканування, рядки паролів або номери карток обробляються виключно всередині "
        "ізольованої оперативної пам'яті поточної сесії. Дані не зберігаються на серверній стороні "
        "й безповоротно знищуються після завершення роботи з інтерфейсом або генерації PDF-документа. " \
        " Користувач зобов'язується застосовувати платформу виключно для законних цілей.</p>"
        "</div>", 
        unsafe_allow_html=True
    )
    
    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b2:
        if st.button("ПІДТВЕРДИТИ ЗГОДУ ТА УВІЙТИ"):
            st.session_state.gdpr_accepted = True
            st.rerun()
    st.stop()


# --- ОСНОВНИЙ ІНТЕРФЕЙС ПЛАТФОРМИ ---

st.markdown("<h1 style='text-align: center; margin-top: 20px;'>🛡️ ПЛАТФОРМА АНАЛІЗУ БЕЗПЕКИ</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777777; font-style: italic; font-size: 14px; letter-spacing: 1px;'>Автоматизований аналіз інфраструктури та гігієни даних</p>", unsafe_allow_html=True)
st.markdown("<hr style='border-color: #1a1a1a; margin-bottom: 30px;'>", unsafe_allow_html=True)

with st.expander("📖 КЕРІВНИЦТВО КОРИСТУВАЧА — ЯК ПРАЦЮЄ СИСТЕМА"):
    st.markdown("""
    ### 🛡️ Як ми захищаємо ваші дані:
    
    * **🌐 Мережева інфраструктура:** Виконуємо технічний аудит через низькорівневі запити. 
      - Аналіз **SSL/TLS**: надійність шифрування з'єднання.
      - **Security Headers**: захист від XSS та Clickjacking-атак.
      - **Information Leakage**: перевірка на витік технічних даних сервера.
                
    * **🔐 Гігієна даних:** 
      - **Аудит витоків**: пошук Email у підозрілих базах.
      - **Валідація**: оцінка стійкості паролів та платіжних даних.
      - **Аналіз посилань**: виявлення фішингу.
                
    * **🤖 Штучний інтелект:** Агрегація технічних метрик та генерація зрозумілого вердикту з рекомендаціями через **Gemini API**.

    ---
    *Наш підхід: перетворюємо складні технічні метрики на прості кроки для захисту вашого цифрового простору.*
    """)
st.markdown("<br>", unsafe_allow_html=True)

# --- ВКЛАДКИ ---
tab1, tab2 = st.tabs(["🌐 АНАЛІЗ ЗОВНІШНЬОЇ ІНФРАСТРУКТУРИ", "🔐 ПЕРСОНАЛЬНА БЕЗПЕКА"])

# --- ВКЛАДКА 1: ЗОВНІШНЯ ІНФРАСТРУКТУРА ---
with tab1:
    st.markdown(
        "<div class='premium-card'>"
        "<h3>🌐 АНАЛІЗ ЗОВНІШНЬОЇ ІНФРАСТРУКТУРИ</h3>"
        "<p style='color:#666666; font-size:12px; margin-bottom:15px;'>Сканування веб-ресурсів та інфраструктурних хостів </p>"
        "</div>", 
        unsafe_allow_html=True
    )
    target_url = st.text_input("Введіть цільовий домен:", placeholder="наприклад: example.com", key="input_url")
    run_scan = st.button("ЗАПУСТИТИ МОДУЛЬ АУДИТУ")

# --- ВКЛАДКА 2: ПЕРСОНАЛЬНА БЕЗПЕКА ---
with tab2:
    st.markdown(
        "<div class='premium-card'>"
        "<h3>🔐 ПЕРСОНАЛЬНА БЕЗПЕКА</h3>"
        "<p style='color:#666666; font-size:12px; margin-bottom:15px;'>Локальне тестування гігієни даних, аудит витоків та фішингових загроз</p>"
        "</div>", 
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    with col1:
        test_password = st.text_input("Експрес-оцінка стійкості пароля:", type="password", placeholder="••••••••••••", key="input_pass")
        test_email = st.text_input("Перевірка Email на витоки в підозрілих базах:", placeholder="your-email@gmail.com", key="input_email")
    with col2:
        test_card = st.text_input("Валідація платіжної карти:", max_chars=16, placeholder="4441 •••• •••• ••••", key="input_card")
        test_link = st.text_input("Аналіз підозрілих посилань або реквізитів зборів:", placeholder="https://dopomoga-oon.com або номер IBAN", key="input_link")
    
    run_personal_audit = st.button("ЗАПУСТИТИ МОДУЛЬ ПЕРСОНАЛЬНОГО АУДИТУ")


# --- ЛОГІКА РОБОТИ: ЗОВНІШНЯ ІНФРАСТРУКТУРА ---
if run_scan and target_url:
    with st.spinner("Виконується безпечне сканування та аналіз..."):
        infra_results = infrastructure.scan_ports(target_url)
        ssl_results = infrastructure.check_ssl(target_url)
        
        # --- DEEP AUDIT ---
        deep_results = deep_audit.run_deep_audit(target_url)

            
        ai_response = ai_engine.evaluate_security_risk(infra_results, ssl_results,{})
        
        # Передача даних Deep Audit у звіт
        ai_response["deep_audit"] = deep_results
        
        st.markdown("<hr style='border-color: #222222; margin: 40px 0;'>", unsafe_allow_html=True)
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2>📊 АНАЛІТИЧНИЙ ВЕРДИКТ СИСТЕМИ: {target_url}</h2>", unsafe_allow_html=True)
        
        risk_color = ai_response.get("color_code", "GREEN").upper()
        if risk_color == "RED":
            st.markdown(f"<span class='status-badge badge-red'>🚨 КРИТИЧНИЙ РІВЕНЬ: {ai_response.get('risk_level')}</span>", unsafe_allow_html=True)
        elif risk_color == "YELLOW":
            st.markdown(f"<span class='status-badge badge-yellow'>⚠️ СЕРЕДНІЙ РІВЕНЬ: {ai_response.get('risk_level')}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span class='status-badge badge-green'>🟢 НИЗЬКИЙ РІВЕНЬ: {ai_response.get('risk_level')}</span>", unsafe_allow_html=True)
            
        st.markdown(f"<p style='font-size: 16px; color: #ffffff;'><b>Резюме аудиту:</b> {ai_response.get('summary')}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: #262626; margin: 20px 0;'>", unsafe_allow_html=True)
        
        st.markdown("### 📋 РЕКОМЕНДАЦІЇ З ОПТИМІЗАЦІЇ:")
        for rec in ai_response.get("recommendations", []):
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 8px; color: #bbbbbb;'>▪️ {rec}</p>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        if risk_color == "RED":
            st.markdown("<div style='border-left: 3px solid #e74c3c; padding-left: 15px; color: #e74c3c; font-size: 13px;'><b>⚠️ ЗВЕРНЕННЯ ДО СПЕЦІАЛІСТА:</b> Виявлені архітектурні вразливості мають високий пріоритет загрози. Рекомендовано залучити SecOps-інженера.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='border-left: 3px solid #2ecc71; padding-left: 15px; color: #2ecc71; font-size: 13px;'><b>💡 САМОСТІЙНЕ ВИПРАВЛЕННЯ:</b> Інфраструктура стабільна. Виявлені зауваження мають рекомендаційний характер.</div>", unsafe_allow_html=True)
            
        st.markdown("<br><br>### 📥 ОФІЦІЙНИЙ ЕКСПОРТ ДАНИХ", unsafe_allow_html=True)
        try:
            pdf_filename = pdf_generator.generate_security_report(
                report_data=ai_response, 
                output_filename=f"SecOps_Report_{target_url}.pdf"
            )
            
            if os.path.exists(pdf_filename):
                with open(pdf_filename, "rb") as pdf_file:
                    st.download_button(
                        label="ЗАВАНТАЖИТИ ПОВНИЙ ЗВІТ (PDF)",
                        data=pdf_file,
                        file_name=pdf_filename,
                        mime="application/pdf"
                    )
            else:
                st.error("Помилка: Файлу звіту не знайдено на сервері після генерації.")
        except Exception as e:
            st.error(f"Помилка створення PDF: {str(e)}")
            
        st.markdown("</div>", unsafe_allow_html=True)

# --- Вивід результатів ---
def display_result(title, status, verdict, color, guide=None):
    st.markdown(f"""
    <div style='background: linear-gradient(145deg, #111111, #161616); 
                border: 1px solid #222222; border-radius: 12px; padding: 20px; 
                margin-bottom: 20px; border-left: 5px solid {color};'>
        <h4 style='color: #ffffff; margin-top:0;'>{title}</h4>
        <p style='color: {color}; font-weight: bold; margin-bottom: 10px;'>{status}</p>
        <p style='color: #cccccc; font-size: 14px;'>{verdict}</p>
        {f"<p style='color: #888888; font-style: italic; font-size: 13px; margin-top: 10px;'>💡 <b>Порада:</b> {guide}</p>" if guide else ""}
    </div>
    """, unsafe_allow_html=True)

# --- ЛОГІКА РОБОТИ: ПЕРСОНАЛЬНА БЕЗПЕКА ---
if run_personal_audit:
    if test_password or test_card or test_email or test_link:
        st.markdown("<hr style='border-color: #222222; margin: 30px 0;'>", unsafe_allow_html=True)
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.markdown("<h3>📊 МОНІТОРИНГ ОСОБИСТИХ МЕТРИК БЕЗПЕКИ</h3>", unsafe_allow_html=True)
        
        # 1. Аналіз пароля
        if test_password:
            pass_analysis = ai_engine.analyze_password_strength(test_password)
            st.markdown(f"<p style='margin-bottom:5px;'><b>Статус пароля:</b> <span style='color:{pass_analysis['color']}'>{pass_analysis['status']}</span></p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#aaaaaa; font-size:14px; margin-bottom:20px;'>{pass_analysis['verdict']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#aaaaaa; font-size:14px; margin-bottom:20px;'>{pass_analysis['guide']}</p>", unsafe_allow_html=True)
            
        # 2. Аналіз платіжної карти
        if test_card:
            if len(test_card) == 16:
                card_analysis = ai_engine.evaluate_card_safety(test_card)
                st.markdown(f"<p style='margin-bottom:5px;'><b>Валідація карти:</b> <span>{card_analysis['status']}</span></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:#aaaaaa; font-size:14px; margin-bottom:20px;'>{card_analysis['verdict']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:#aaaaaa; font-size:14px; margin-bottom:20px;'>{card_analysis['guide']}</p>", unsafe_allow_html=True)
            else:
                st.warning("Номер карти повинен складатися рівно з 16 цифр для запуску перевірки.")
            
    
        # 3. Аналіз Email 
        if test_email:
            st.markdown("<hr style='border-color: #262626; margin: 15px 0;'>", unsafe_allow_html=True)
            with st.spinner("Перевірка емейлу в базах даних..."):
                # Функція з ai_engine
                email_res = ai_engine.check_email_leaks(test_email)
                
                # Логіка визначення кольору та статусу
                if email_res.get("leaked") is True:
                    e_color, e_status = "#e74c3c", "🚨 ЗНАЙДЕНО У ВИТОКАХ"
                elif email_res.get("leaked") is False:
                    e_color, e_status = "#2ecc71", "🟢 ЕМЕЙЛ БЕЗПЕЧНИЙ"
                else:
                    e_color, e_status = "#f1c40f", "⚠️ СТАТУС НЕВІДОМИЙ"
                
                # Вивід результату
                display_result(
                    "📧 Аудит Email-безпеки",
                    e_status,
                    email_res.get("verdict"),
                    e_color
                )
                

        # 4. Аналіз посилань та реквізитів донатів
        if test_link:
            
            with st.spinner("ШІ виконує інтелектуальний аналіз..."):
                link_analysis = ai_engine.analyze_url_or_donation(test_link)
                
                # Статус для заголовка картки
                l_color = link_analysis["status_color"]
                if l_color == "red":
                    status_text = "🚨 КРИТИЧНИЙ РИЗИК"
                    display_color = "#e74c3c"
                elif l_color == "yellow":
                    status_text = "⚠️ ПОТРЕБУЄ ПЕРЕВІРКИ"
                    display_color = "#f1c40f"
                else:
                    status_text = "🟢 ВЕРИФІКОВАНО"
                    display_color = "#2ecc71"
                
                # Вивід 
                display_result(
                    "🔗 Аналіз посилання / донату", 
                    status_text, 
                    link_analysis['verdict'], 
                    display_color
                )
    else:
        st.info("Будь ласка, заповніть хоча б одне поле для запуску персонального аудиту.")
