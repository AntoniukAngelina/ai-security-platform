import requests

def run_deep_audit(url):
    if not url.startswith("http"): url = "https://" + url
    
    # Заголовки, щоб сайт бачив нас як браузер
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    report = {"ssl": {}, "headers": {}, "stack": {}, "files": {}, "reputation": "Верифіковано"}
    
    # 1. Заголовки 
    try:
        resp = requests.head(url, timeout=5, allow_redirects=True, headers=headers)
        h = resp.headers
        required = ["Content-Security-Policy", "Strict-Transport-Security", "X-Frame-Options", "X-Content-Type-Options"]
        report["headers"] = {header: (header in h) for header in required}
        
        # Стек (Information Leakage)
        report["stack"] = {
            "Server": h.get("Server", "Unknown"),
            "X-Powered-By": h.get("X-Powered-By", "Not disclosed")
        }
    except requests.RequestException:
        report["headers"] = "Connection Error"

    # 2. Пошук "сміття"
    sensitive = ["/.env", "/.git/config", "/robots.txt"]
    for path in sensitive:
        try:
            res = requests.get(url + path, timeout=2, headers=headers)
            report["files"][path] = res.status_code == 200
        except requests.RequestException:
            report["files"][path] = False
            
    return report