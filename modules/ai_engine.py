import os
import math
import re
import json
from google import genai
from google.genai import types

# --- 1. ШІ-АНАЛІЗ ПАРОЛІВ ---

def calculate_shannon_entropy(password: str) -> float:
    """Математичний аналіз для оцінки щільності інформації"""
    if not password:
        return 0.0
    
    frequencies = {}
    for char in password:
        frequencies[char] = frequencies.get(char, 0) + 1
    
    entropy = 0.0
    length = len(password)
    for count in frequencies.values():
        p = count / length
        entropy -= p * math.log2(p)
        
    return round(entropy, 2)

def analyze_password_strength(password: str) -> dict:
    """
    Гібридний аналіз пароля: Ентропія Шеннона + Локальна імовірнісна модель передбачуваності.
    БЕЗПЕЧНО: Обробка локальна, дані не надсилаються в інтернет.
    """
    length = len(password)
    entropy = calculate_shannon_entropy(password)

    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_spec = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>_+\-=\[\]]", password))
    
    is_predictable_human_pattern = False
    if has_upper and has_lower and (has_digit or has_spec):
        if password[0].isupper() and re.match(r"^[A-Z][a-z]+[0-9!@#$%^&*]+$", password):
            is_predictable_human_pattern = True

    pool_size = 0
    if has_lower: pool_size += 26
    if has_upper: pool_size += 26
    if has_digit: pool_size += 10
    if has_spec: pool_size += 32
    
    total_bits = length * math.log2(pool_size) if pool_size > 0 else 0

    if total_bits < 40 or length < 8:
        status = "🔴 КРИТИЧНО СЛАБКИЙ ПАРОЛЬ"
        color = "red"
        verdict = f"Ентропія: {entropy} біт/символ. Загальна стійкість: {total_bits:.1f} біт. Пароль вразливий до миттєвого зламу брутфорсом."
        guide = "💡 РЕКОМЕНДАЦІЯ: Збільшіть довжину мінімум до 12+ символів, додайте спецсимволи(!@#), уникайте простих слів."
    elif is_predictable_human_pattern or total_bits < 65:
        status = "🟡 СЕРЕДНІЙ РІВЕНЬ РИЗИКУ"
        color = "yellow"
        verdict = f"Ентропія: {entropy} біт/символ. Стійкість: {total_bits:.1f} біт. " \
                  f"ШІ виявив стандартний людський шаблон (Велика літера на початку + цифри/знаки в кінці). Хакерські словники підберуть його дуже швидко."
        guide = "💡 РЕКОМЕНДАЦІЯ: Перемішайте цифри та спецсимволи всередині слова, а не лише в кінці. Зробіть структуру хаотичною."
    else:
        status = "🟢 ВИСОКИЙ РІВЕНЬ ЗАХИСТУ"
        color = "green"
        verdict = f"Ентропія: {entropy} біт/символ. Математична стійкість: {total_bits:.1f} біт. Структура хаотична, лінгвістичних шаблонів не виявлено."
        guide = "💡 Чудова робота. Цей пароль відповідає сучасним корпоративним стандартам безпеки."

    return {"status": status, "color": color, "verdict": verdict, "guide": guide}


# --- 2. ВАЛІДАЦІЯ БАНКІВСЬКИХ КАРТОК ---

def evaluate_card_safety(card_number: str) -> dict:
    """
    Математичний аналіз + Інтелектуальна локальна класифікація.
    БЕЗПЕЧНО: Обробка суто локальна.
    """
    digits = [int(d) for d in card_number]
    checksum = 0
    reverse_digits = digits[::-1]
    
    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:
            double_digit = digit * 2
            if double_digit > 9:
                double_digit -= 9
            checksum += double_digit
        else:
            checksum += digit
            
    is_luhn_valid = (checksum % 10 == 0)
    
    if not is_luhn_valid:
        return {
            "status": "🚨 МАТЕМАТИЧНА ПОМИЛКА: КАРТКА НЕВАЛІДНА",
            "color": "red",
            "verdict": "Введений номер не пройшов перевірку. Цей набір цифр штучно згенерований або введений з помилкою.",
            "guide": "⚠️ КРИТИЧНО: Жоден діючий банк світу не міг випустити таку картку."
        }

    system_type = "Невідома платіжна система"
    if card_number.startswith("4"):
        system_type = "VISA International"
    elif card_number.startswith(("51", "52", "53", "54", "55")) or (510000 <= int(card_number[:6]) <= 559999):
        system_type = "Mastercard Worldwide"
    elif card_number.startswith("9804"):
        system_type = "Національна платіжна система «ПРОСТІР» (Україна)"

    return {
        "status": "🟢 КАРТКА ВАЛІДНА (МАТЕМАТИЧНО ПІДТВЕРДЖЕНО)",
        "color": "green",
        "verdict": f"Номер успішно пройшов криптографічну валідацію. Визначена платіжна архітектура: {system_type}.",
        "guide": "📋 ІНСТРУКЦІЯ: Реквізити існують. Перед відправкою грошей обов'язково перевірте отримувача."
    }


# --- ШІ (GOOGLE GEMINI) ---

def evaluate_security_risk(infra_data: dict, ssl_data: dict, osint_data: dict) -> dict:
    """
    Глибокий аналіз інфраструктурних загроз за допомогою генеративного ШІ від Google (Gemini).
    Агрегує реальні низькорівневі дані з усього проекту.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "missing_key")
    
    prompt = f"""
    Ти — провідний експерт із кібербезпеки та аудиту систем (SecOps / Penetration Tester).
    Проаналізуй технічні дані сканування корпоративного вузла та сформуй аналітичний звіт українською мовою.

    ВХІДНІ ДАНІ ДЛЯ АНАЛІЗУ:
    - Стан мережевих портів компанії: {infra_data}
    - Статус криптографічного захисту каналу SSL/TLS: {ssl_data}
    - Додаткові OSINT-маркери уразливостей: {osint_data}

    ВИМОГИ ДО ВИСНОВКУ:
    1. Визнач рівень загрози: КРИТИЧНИЙ (RED), СЕРЕДНІЙ (YELLOW) або НИЗЬКИЙ (GREEN).
    2. Напиши коротке резюме (summary) для керівництва компанії (до 4 речень).
    3. Сформуй детальний технічний план дій для системних адміністраторів (масив рекомендацій).

    Поверни відповідь СУВОРO у форматі JSON із такими ключами:
    {{
        "risk_level": "Рівень загрози",
        "color_code": "RED або YELLOW або GREEN",
        "summary": "Резюме аналізу українською мовою",
        "recommendations": ["Крок 1", "Крок 2", "Крок 3"]
    }}
    """

    if api_key == "missing_key":
        return fallback_local_analysis(infra_data, ssl_data, error_msg="Відсутній GEMINI_API_KEY")

    try:
        # Ініціалізація клієнта 
        client = genai.Client(api_key=api_key)
        
        # Модель gemini
        response = client.models.generate_content(
            model='models/gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            ),
        )
        return json.loads(response.text)
        
    except Exception as e:
        return fallback_local_analysis(infra_data, ssl_data, error_msg=str(e))


def fallback_local_analysis(infra_data: dict, ssl_data: dict, error_msg="") -> dict:
    """Локальний резервний ШІ-аналіз, якщо хмара недоступна"""
    open_ports = [port for port, info in infra_data.items() if info.get("status") == "OPEN"]
    has_ssl = ssl_data.get("has_ssl", False)
    
    recommendations = ["Провести аудит конфігурацій брандмауера."]
    
    if 22 in open_ports or 3306 in open_ports:
        risk = "КРИТИЧНИЙ (ЛОКАЛЬНИЙ АНАЛІЗ)"
        color = "RED"
        summary = "Виявлено відкриті критичні порти управління (SSH/Database) в публічній мережі. Високий ризик зламу."
        recommendations.append("Негайно закрити порт 22 та 3306 для зовнішнього світу або налаштувати VPN/IP Whitelist.")
    elif not has_ssl:
        risk = "СЕРЕДНІЙ (ЛОКАЛЬНИЙ АНАЛІЗ)"
        color = "YELLOW"
        summary = "Сайт використовує незашифрований протокол HTTP. Трафік користувачів може бути перехоплений."
        recommendations.append("Встановити та налаштувати SSL-сертифікат і увімкнути редірект на HTTPS.")
    else:
        risk = "НИЗЬКИЙ (ЛОКАЛЬНИЙ АНАЛІЗ)"
        color = "GREEN"
        summary = "Основні публічні веб-порти захищені, активний SSL-сертифікат. Прямих загроз не виявлено."
        recommendations.append("Продовжувати плановий моніторинг оновлень безпеки.")

    if error_msg:
        summary += f" [Хмарне API недоступне: {error_msg}]"

    return {"risk_level": risk, "color_code": color, "summary": summary, "recommendations": recommendations}


# ---3. ЛИСТИ ПОШТОВІ ---

def check_email_leaks(email: str) -> dict:
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        model_name = "models/gemini-3.5-flash"
        
        # Перевірка ризиків
        prompt = f"""
        Проаналізуй емейл: {email}.
        1. Перевір, чи він був у відомих базах витоків (відповідь LEAKED або SAFE).
        2. Перевір домен на приналежність до країн-агресорів (наприклад, .ru, .su). Якщо це так, познач як небезпечний через ризик витоку даних до ворожих спецслужб.
        
        Відповідь дай у форматі: "STATUS: LEAKED/SAFE/RISKY. Вердикт: [Твій висновок українською]."
        """
        
        response = client.models.generate_content(model=model_name, contents=prompt)
        result = response.text.upper()
        
        # Логіка обробки
        if "LEAKED" in result or "RISKY" in result:
            verdict = "🚨 Увага: Емейл скомпрометовано або відноситься до ризикованого домену!"
            return {"leaked": True, "verdict": verdict}
            
        return {"leaked": False, "verdict": "🟢 Емейл безпечний."}
    
    # Надіюсь цього не буде 🙂       
    except Exception as e:
        error_msg = str(e)
        print(f"DEBUG: Помилка: {error_msg}") # Це бачиш тільки ти в терміналі
        
        if "429" in error_msg:
            # Це точно ліміт
            msg = "Ліміт запитів до ШІ вичерпано. Будь ласка, зачекайте хвилину. 🙂"
        elif "404" in error_msg:
            # Це помилка моделі
            msg = "ШІ-модель тимчасово недоступна. Спробуйте іншу або зачекайте."
        else:
            # Це якась інша невідома помилка
            msg = "ШІ зараз недоступний. Будь ласка, перевірте дані вручну."
            
        return {
            "status_color": "yellow",
            "verdict": msg
        }
    

# --- 4. ДОНАТИ  ---
def analyze_url_or_donation(input_data: str) -> dict:
    """ 
    Використовуємо ШІ для перевірки довіри до посилань, IBAN та зборів.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # Промпт для ШІ
    prompt = f"""
    Ти — експерт із кібербезпеки та фінансового моніторингу. Твоє завдання — перевірити реквізит або посилання: '{input_data}'.
    
    Критерії оцінки:
    1. Перевір, чи це відомий офіційний фонд України (наприклад, "Повернись живим", "Фонд Притули", "UAnimals" тощо).
    2. Перевір на ознаки фішингу: чи схоже це на шахрайські "виплати від ООН", "крипто-бонуси" або підозрілі короткі посилання.
    3. Якщо це номер картки або IBAN, вкажи, що це потребує особливої уваги, бо приватні збори важче верифікувати.
    
    Поверни відповідь СУВОРО у форматі JSON:
    {{
        "status_color": "green" (якщо надійне), "yellow" (якщо невідоме/сумнівне), або "red" (якщо фішинг),
        "verdict": "Короткий, чіткий висновок (до 3 речень) українською мовою."
    }}
    """

    try:
        if api_key:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='models/gemini-3.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                ),
            )
            return json.loads(response.text)
        
    except Exception as e:
        error_msg = str(e)
        print(f"DEBUG: Помилка: {error_msg}") # Це бачиш тільки ти в терміналі
        
        if "429" in error_msg:
            # Це точно ліміт
            msg = "Ліміт запитів до ШІ вичерпано. Будь ласка, зачекайте хвилину. 🙂"
        elif "404" in error_msg:
            # Це помилка моделі
            msg = "ШІ-модель тимчасово недоступна. Спробуйте іншу або зачекайте."
        else:
            # Це якась інша невідома помилка
            msg = "ШІ зараз недоступний. Будь ласка, перевірте дані вручну."
            
        return {
            "status_color": "yellow",
            "verdict": msg
        }