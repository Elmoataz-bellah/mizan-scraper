import requests
from bs4 import BeautifulSoup
import os
import urllib.parse

# روابط أخبار جوجل للأقسام الاقتصادية في مصر (مضمونة 100%)
CATEGORIES = {
    "اقتصاد": "https://news.google.com/rss/search?q=اقتصاد+مصر&hl=ar&gl=EG&ceid=EG:ar",
    "ذهب": "https://news.google.com/rss/search?q=أسعار+الذهب+في+مصر&hl=ar&gl=EG&ceid=EG:ar",
    "عملات": "https://news.google.com/rss/search?q=أسعار+الدولار+والعملات+في+مصر&hl=ar&gl=EG&ceid=EG:ar",
    "طاقة": "https://news.google.com/rss/search?q=أسعار+البنزين+والطاقة+مصر&hl=ar&gl=EG&ceid=EG:ar"
}

NEWS_SCRIPT_URL = os.getenv("NEWS_SCRIPT_URL")

def scrape_news():
    all_news = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for cat_name, url in CATEGORIES.items():
        try:
            print(f"📡 سحب من أخبار جوجل لقسم: {cat_name}...")
            # تحويل الرابط لصيغة تفهمها أخبار جوجل
            res = requests.get(url, headers=headers, timeout=30)
            
            if res.status_code != 200:
                print(f"⚠️ فشل الوصول لجوجل {cat_name}: {res.status_code}")
                continue

soup = BeautifulSoup(res.content, 'html.parser')
            items = soup.find_all('item')
            
            count = 0
            for item in items:
                if count >= 5: break # سحب 5 أخبار لكل قسم
                
                title = item.title.text.strip()
                # جوجل بيحط اسم المصدر في نهاية العنوان، هنشيله عشان الشكل
                clean_title = title.split(' - ')[0]
                source = title.split(' - ')[-1] if ' - ' in title else "مصدر إخباري"
                
                link = item.link.text.strip()
                pub_date = item.pubDate.text.strip() if item.pubDate else "اليوم"

                all_news.append({
                    "category": cat_name,
                    "title": clean_title,
                    "description": f"المصدر: {source}",
                    "image": "https://www.gstatic.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png", # صورة افتراضية لأن جوجل RSS لا يرسل صوراً مباشرة
                    "time": pub_date
                })
                count += 1
            print(f"✅ تم سحب {count} أخبار من جوجل لـ {cat_name}")
                
        except Exception as e:
            print(f"❌ خطأ في {cat_name}: {e}")
            
    return all_news

# الإرسال
print("🚀 بدأ سكريبت Google News RSS...")
news_data = scrape_news()

if news_data:
    print(f"✅ تم تجميع {len(news_data)} خبر.")
    if NEWS_SCRIPT_URL:
        try:
            res = requests.post(NEWS_SCRIPT_URL, json={"type": "update_news", "data": news_data})
            print(f"🚀 رد جوجل شيت: {res.text}")
        except Exception as e:
            print(f"❌ فشل الإرسال: {e}")
else:
    print("❌ فشل السكريبت: حتى جوجل لم يرجع بيانات!")
