import requests
from bs4 import BeautifulSoup
import os
import time

# روابط بوابة الأهرام (أقسام الاقتصاد)
CATEGORIES = {
    "اقتصاد": "https://gate.ahram.org.eg/Category/1/2/المال-والأعمال.aspx",
    "ذهب": "https://gate.ahram.org.eg/Search/ذهب.aspx",
    "عملات": "https://gate.ahram.org.eg/Search/أسعار-العملات.aspx",
    "طاقة": "https://gate.ahram.org.eg/Search/البترول.aspx"
}

NEWS_SCRIPT_URL = os.getenv("NEWS_SCRIPT_URL")

def scrape_news():
    all_news = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for cat_name, url in CATEGORIES.items():
        try:
            print(f"📡 فحص بوابة الأهرام - قسم: {cat_name}...")
            res = requests.get(url, headers=headers, timeout=20)
            res.encoding = 'utf-8' # لضمان قراءة اللغة العربية صح
            
            if res.status_code != 200:
                print(f"⚠️ فشل الوصول لـ {cat_name}: {res.status_code}")
                continue

            soup = BeautifulSoup(res.content, 'html.parser')
            
            # في بوابة الأهرام، الخبر غالباً بيكون داخل div كلاس "entry-item" أو "col-md-4"
            articles = soup.find_all('div', class_='col-md-4') or soup.find_all('div', class_='news-item')
            
            count = 0
            for art in articles:
                if count >= 3: break
                
                title_tag = art.find('a')
                if not title_tag or not title_tag.text.strip(): continue
                
                title = title_tag.text.strip()
                if len(title) < 15: continue # تخطي العناوين القصيرة جداً
                
                # جلب الصورة
                img_tag = art.find('img')
                img = ""
                if img_tag:
                    img = img_tag.get('src') or img_tag.get('data-src')
                
                # تصحيح مسار الصورة لو كان مسار نسبي
                if img and img.startswith('/'):
                    img = "https://gate.ahram.org.eg" + img

                all_news.append({
                    "category": cat_name,
                    "title": title,
                    "description": "بوابة الأهرام: " + title,
                    "image": img if img else "https://gate.ahram.org.eg/Content/Upload/Slider/2023/1/25/0_2023125152345.jpg",
                    "time": "آخر تحديث"
                })
                count += 1
            print(f"✅ تم العثور على {count} أخبار في {cat_name}")
                
        except Exception as e:
            print(f"❌ خطأ في {cat_name}: {e}")
            
    return all_news

# التنفيذ والإرسال
print("🚀 بدأ سكريبت بوابة الأهرام...")
news_data = scrape_news()

if news_data:
    print(f"✅ نجاح! تم سحب {len(news_data)} خبر.")
    if NEWS_SCRIPT_URL:
        try:
            res = requests.post(NEWS_SCRIPT_URL, json={"type": "update_news", "data": news_data})
            print(f"🚀 رد جوجل: {res.text}")
        except Exception as e:
            print(f"❌ فشل الإرسال لجوجل: {e}")
else:
    print("❌ فشل السكريبت بالكامل.")
