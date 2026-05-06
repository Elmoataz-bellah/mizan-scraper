import requests
from bs4 import BeautifulSoup
import os

# الرابط الخاص ببيانات القطاعات والأسهم
url = "https://egksco-online.com/etrade/Sectors.aspx"
# يفضل دائماً استخدام Environment Variable للرابط، لكن وضعته لك هنا مباشرة كما طلبت
APP_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzHsQnJf_H8OHvg4bgH9qyBtqjYWVj3jaSDL0Nx5RLF-BNBS3Qno0fF35CA1v9pCRo/exec"

def clean_name(name):
    """تنظيف اسم الشركة ليحتوي على أول 3 كلمات فقط"""
    words = name.split()
    if len(words) > 3:
        return " ".join(words[:3])
    return name

def get_stocks_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        print("📡 جاري سحب بيانات الأسهم...")
        response = requests.get(url, headers=headers, timeout=25)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # البحث عن الجدول من خلال الـ ID
        table = soup.find("table", {"id": "ctl00_MainContent_SymbolsGridView1"})
        
        if not table:
            print("❌ لم يتم العثور على جدول البيانات")
            return []

        rows = table.find_all("tr")
        results = []
        
        # البدء من الصف الثاني لتخطي العناوين
        for row in rows[1:]: 
            cols = row.find_all("td")
            if len(cols) >= 10:
                # استخراج القيم الأساسية
                name_raw = cols[0].text.strip()
                price_val = cols[2].text.strip()    # السعر الحالي
                alt_price = cols[3].text.strip()    # سعر الإغلاق السابق (احتياطي)
                change_percent = cols[4].text.strip() # نسبة التغير

                # 1. اختيار السعر المناسب (لو الأساسي صفر ناخد الاحتياطي)
                last_price = price_val if price_val not in ["0", "0.00", "0.0", ""] else alt_price
                
                # 2. 🛑 فلترة الأصفار: لو لسه السعر صفر أو فاضي، نتخطى هذا السهم تماماً
                if last_price in ["0", "0.00", "0.0", ""]:
                    continue 

                # 3. معالجة الاسم وإضافة البيانات
                # نتأكد إن الاسم مش مجرد رقم (ID) بل نص حقيقي
                if name_raw and not name_raw.replace('.', '').isdigit():
                    results.append({
                        "name": clean_name(name_raw),
                        "price": last_price,
                        "change": change_percent
                    })
                elif len(cols) > 1:
                     name_alt = cols[1].text.strip()
                     if name_alt and not name_alt.replace('.', '').isdigit():
                         results.append({
                            "name": clean_name(name_alt),
                            "price": last_price,
                            "change": change_percent
                        })

        return results
    except Exception as e:
        print(f"❌ خطأ أثناء السحب: {e}")
        return []

# --- تنفيذ السكريبت ---
stocks = get_stocks_data()

if stocks:
    # حذف التكرار بناءً على اسم الشركة
    unique_stocks = list({v['name']: v for v in stocks}.values())
    
    print(f"✅ تم تصفية البيانات: متبقي {len(unique_stocks)} شركة (بعد حذف الأصفار والتكرار).")
    
    try:
        # إرسال البيانات إلى Google Apps Script
        res = requests.post(
            APP_SCRIPT_URL, 
            json={"type": "update_stocks", "data": unique_stocks},
            timeout=30
        )
        print(f"🚀 رد جوجل شيت: {res.text}")
    except Exception as e:
        print(f"❌ فشل الإرسال لجوجل: {e}")
else:
    print("⚠️ لا توجد بيانات صالحة لإرسالها.")
