import requests
from bs4 import BeautifulSoup

url = "https://egksco-online.com/etrade/Sectors.aspx"
APP_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzHsQnJf_H8OHvg4bgH9qyBtqjYWVj3jaSDL0Nx5RLF-BNBS3Qno0fF35CA1v9pCRo/exec"

def clean_name(name):
    words = name.split()
    if len(words) > 3:
        return " ".join(words[:3])
    return name

def get_stocks_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find("table", {"id": "ctl00_MainContent_SymbolsGridView1"})
        
        if not table: return []

        rows = table.find_all("tr")
        results = []
        
        for row in rows[1:]: 
            cols = row.find_all("td")
            if len(cols) >= 10:
                name_raw = cols[0].text.strip()
                
                # --- التعديل هنا لتجنب الأصفار ---
                price_val = cols[2].text.strip()    # السعر اللي بيجي صفر
                alt_price = cols[3].text.strip()    # السعر الاحتياطي من العمود اللي جنبه
                
                # لو السعر الأساسي صفر، خد الاحتياطي، لو الاتنين صفر خليه صفر زي ما هو
                last_price = price_val if price_val not in ["0", "0.00", ""] else alt_price
                # -------------------------------
                
                change_percent = cols[4].text.strip()

                if name_raw and not name_raw.replace('.','').isdigit():
                    results.append({
                        "name": clean_name(name_raw),
                        "price": last_price,
                        "change": change_percent
                    })
                elif len(cols) > 1:
                     name_alt = cols[1].text.strip()
                     if name_alt and not name_alt.replace('.','').isdigit():
                         results.append({
                            "name": clean_name(name_alt),
                            "price": last_price,
                            "change": change_percent
                        })

        return results
    except Exception as e:
        print(f"Error: {e}")
        return []

stocks = get_stocks_data()
if stocks:
    unique_stocks = {v['name']: v for v in stocks}.values()
    print(f"تم سحب {len(unique_stocks)} شركة بنجاح!")
    res = requests.post(APP_SCRIPT_URL, json={"type": "update_stocks", "data": list(unique_stocks)})
    print(f"رد جوجل: {res.text}")
