from fpdf import FPDF
import datetime

def generate_security_report(report_data, output_filename):
    pdf = FPDF()
    
    # Один і той самий файл шрифту як для звичайного, так і для напівжирного стилю
    pdf.add_font('DejaVu', '', 'Dejavu_Sans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVu_Sans.ttf', uni=True)
    
    pdf.add_page()
    
    # Наш шрифт
    pdf.set_font('DejaVu', '', 16)
    pdf.cell(200, 10, txt="Звіт з аудиту безпеки", ln=True, align='C')
    
    pdf.set_font('DejaVu', '', 12)
    pdf.cell(200, 10, txt=f"Дата: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
    pdf.ln(10)

    # --- СЕКЦІЯ 1: ЗАГАЛЬНИЙ РИЗИК ---
    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(200, 10, txt="1. Оцінка безпеки (AI Assessment)", ln=True)
    pdf.set_font('DejaVu', '', 12)
    
    risk_text = f"Рівень ризику: {report_data.get('risk_level', 'N/A')}\n\nРезюме: {report_data.get('summary', 'N/A')}"
    pdf.multi_cell(0, 10, txt=risk_text)
    pdf.ln(5)

    # --- СЕКЦІЯ 1.5: ТЕХНІЧНИЙ АУДИТ ---
    deep = report_data.get("deep_audit", {})
    if deep:
        pdf.set_font('DejaVu', 'B', 14)
        pdf.cell(200, 10, txt="2. Технічний аудит (Deep Audit)", ln=True)
        pdf.set_font('DejaVu', '', 11)
        
        pdf.cell(200, 8, txt="Заголовки безпеки:", ln=True)
        headers = deep.get("headers", {})
        if isinstance(headers, dict):
            for h, status in headers.items():
                status_text = "Присутній" if status else "Відсутній"
                pdf.cell(200, 7, txt=f"- {h}: {status_text}", ln=True)
        
        pdf.ln(2)
        pdf.cell(200, 8, txt="Файли конфігурації:", ln=True)
        files = deep.get("files", {})
        if isinstance(files, dict):
            for path, found in files.items():
                status_text = "!!! ЗНАЙДЕНО (Вразливо)" if found else "OK (Захищено)"
                pdf.cell(200, 7, txt=f"- {path}: {status_text}", ln=True)
        pdf.ln(5)

    # --- СЕКЦІЯ 3: РЕКОМЕНДАЦІЇ ---
    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(200, 10, txt="3. Рекомендації", ln=True)
    pdf.set_font('DejaVu', '', 12)
    for rec in report_data.get("recommendations", []):
        pdf.multi_cell(0, 7, txt=f"- {rec}")

    pdf.output(output_filename)
    return output_filename