import requests
from bs4 import BeautifulSoup

url = "https://egksco-online.com/etrade/Sectors.aspx"
APP_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzHsQnJf_H8OHvg4bgH9qyBtqjYWVj3jaSDL0Nx5RLF-BNBS3Qno0fF35CA1v9pCRo/exec"

# 1. دالة اختصار الاسم ليكون بحد أقصى 3 كلمات
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
        # البحث عن الجدول بالـ ID المحدد
        table = soup.find("table", {"id": "ctl00_MainContent_SymbolsGridView1"})
        
        if not table: 
            print("لم يتم العثور على جدول البيانات")
            return []

        rows = table.find_all("tr")
        results = []
        
        for row in rows[1:]: 
            cols = row.find_all("td")
            if len(cols) >= 10:
                name_raw = cols[1].text.strip() # اسم الشركة
                
                # جلب كل قيم الأسعار المتاحة لضمان عدم ظهور 0.00
                last_close = cols[2].text.strip()   # سعر الإقفال السابق
                current_val = cols[3].text.strip()  # السعر الحالي (أثناء الجلسة)
                open_price = cols[5].text.strip()   # سعر الفتح
                
                # منطق اختيار السعر: يبحث عن أول قيمة "ليست صفراً" بالترتيب
                final_price = "0.00"
                for p in [current_val, last_close, open_price]:
                    if p and p not in ["0", "0.00", "0.0", ""]:
                        final_price = p
                        break
                
                change_percent = cols[4].text.strip() # نسبة التغير

                # التأكد أن الصف يحتوي على اسم شركة حقيقي وليس مجرد أرقام
                if name_raw and not name_raw.replace('.','').isdigit():
                    results.append({
                        "name": clean_name(name_raw),
                        "price": final_price,
                        "change": change_percent
                    })

        return results
    except Exception as e:
        print(f"حدث خطأ أثناء السحب: {e}")
        return []

# التنفيذ والإرسال لجوجل شيت
stocks = get_stocks_data()

if stocks:
    # حذف التكرار بناءً على الاسم لضمان نظافة البيانات قبل الإرسال
    unique_stocks_dict = {v['name']: v for v in stocks}
    unique_stocks_list = list(unique_stocks_dict.values())
    
    print(f"تم سحب {len(unique_stocks_list)} شركة بنجاح!")
    
    try:
        res = requests.post(APP_SCRIPT_URL, json={"type": "update_stocks", "data": unique_stocks_list})
        print(f"رد جوجل: {res.text}")
    except Exception as e:
        print(f"خطأ في إرسال البيانات لجوجل: {e}")
else:
    print("لم يتم العثور على أي بيانات لإرسالها.")
