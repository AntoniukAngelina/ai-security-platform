import socket
import ssl

def scan_ports(host: str) -> dict:
    """Сканування основних критичних портів сервера"""
    # Очищення від http/https, якщо користувач їх ввів
    clean_host = host.replace("https://", "").replace("http://", "").split("/")[0]
    
    # Список критичних портів для перевірки
    ports_to_scan = {
        22: "SSH (Віддалений доступ до сервера)",
        80: "HTTP (Веб-сайт без шифрування даних)",
        443: "HTTPS (Захищений веб-сайт із шифруванням)",
        3306: "MySQL (Порт бази даних)"
    }
    
    scan_results = {}
    
    for port, service in ports_to_scan.items():
        # Підключення через сокети з часом 1.5 секунди
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        result = s.connect_ex((clean_host, port))
        
        if result == 0:
            scan_results[port] = {"service": service, "status": "OPEN (Вразливо)"}
        else:
            scan_results[port] = {"service": service, "status": "CLOSED (Безпечно)"}
        s.close()
        
    return scan_results

def check_ssl(host: str) -> dict:
    """Перевірка наявності та валідності SSL-сертифіката"""
    clean_host = host.replace("https://", "").replace("http://", "").split("/")[0]
    ctx = ssl.create_default_context()
    
    try:
        with socket.create_connection((clean_host, 443), timeout=3) as sock:
            with ctx.wrap_socket(sock, server_hostname=clean_host) as ssock:
                ssock.getpeercert()
                return {"has_ssl": True, "details": "SSL-сертифікат активний та захищає дані користувачів."}
    except Exception:
        return {"has_ssl": False, "details": "SSL-сертифікат не знайдено або він протермінований! Дані користувачів під загрозою перехоплення."}