import requests
from bs4 import BeautifulSoup
import os

# روابط RSS Feed (مخصصة للتطبيقات ولا تعطي 403)
CATEGORIES = {
    "اقتصاد": "https://www.youm7.com/rss/Section/297", # قسم اقتصاد اليوم السابع
    "ذهب": "https://www.youm7.com/rss/Section/97",     # أخبار عامة (سنفلترها بالعنوان)
    "عملات": "https://www.youm7.com/rss/Section/297",  # نفس قسم الاقتصاد
    "طاقة": "https://www.youm7.com/rss/Section/297"
}

NEWS_SCRIPT_URL = os.getenv("NEWS_SCRIPT_URL")

def scrape_news():
    all_news = []
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    
    for cat_name, url in CATEGORIES.items():
        try:
            print(f"📡 سحب RSS لقسم: {cat_name}...")
            res = requests.get(url, headers=headers, timeout=20)
            
            if res.status_code != 200:
                print(f"⚠️ فشل RSS لـ {cat_name}: {res.status_code}")
                continue

            # تحليل الـ XML الخاص بالـ RSS
            soup = BeautifulSoup(res.content, 'xml')
            items = soup.find_all('item')
            
            count = 0
            for item in items:
                if count >= 3: break
                
                title = item.title.text.strip()
                # فلترة بسيطة للتأكد أن الخبر مناسب للقسم (اختياري)
                if cat_name == "ذهب" and "ذهب" not in title: continue
                if cat_name == "عملات" and ("دولار" not in title and "جنيه" not in title): continue

                link = item.link.text.strip()
                description = item.description.text.strip() if item.description else ""
                
                # استخراج الصورة من الـ RSS (غالباً في وسام enclosure أو description)
                img = ""
                enclosure = item.find('enclosure')
                if enclosure:
                    img = enclosure.get('url')
                
                if not img: # محاولة البحث في الوصف
                    desc_soup = BeautifulSoup(description, 'html.parser')
                    img_tag = desc_soup.find('img')
                    if img_tag: img = img_tag.get('src')

                all_news.append({
                    "category": cat_name,
                    "title": title,
                    "description": "اليوم السابع: " + title,
                    "image": img if img else "https://www.youm7.com/images/youm7-logo.png",
                    "time": "منذ قليل"
                })
                count += 1
            print(f"✅ تم سحب {count} خبر من RSS {cat_name}")
                
        except Exception as e:
            print(f"❌ خطأ في {cat_name}: {e}")
            
    return all_news

# التنفيذ والإرسال
print("🚀 بدأ سكريبت الـ RSS Feed...")
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
    print("❌ فشل السكريبت: لم يتم العثور على بيانات RSS.")
