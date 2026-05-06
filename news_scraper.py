import requests
from bs4 import BeautifulSoup
import os

# روابط RSS مصراوي الرسمية (الأقسام المطلوبة)
CATEGORIES = {
    "اقتصاد": "https://www.masrawy.com/rss/feed/206/%D8%A5%D9%82%D8%AA%D8%B5%D8%A7%D8%AF",
    "ذهب": "https://www.masrawy.com/rss/feed/126/%D8%A3%D8%B3%D8%B9%D8%A7%D8%B1-%D8%A7%D9%84%D8%B0%D9%87%D8%A8",
    "عملات": "https://www.masrawy.com/rss/feed/127/%D8%A3%D8%B3%D8%B9%D8%A7%D8%B1-%D8%A7%D9%84%D8%B9%D9%85%D9%84%D8%A7%D8%aa",
    "طاقة": "https://www.masrawy.com/rss/feed/518/%D8%B7%D8%A7%D9%82%D8%A9"
}

NEWS_SCRIPT_URL = os.getenv("NEWS_SCRIPT_URL")

def scrape_news():
    all_news = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for cat_name, url in CATEGORIES.items():
        try:
            print(f"📡 محاولة سحب RSS مصراوي لقسم: {cat_name}...")
            res = requests.get(url, headers=headers, timeout=25)
            
            if res.status_code != 200:
                print(f"⚠️ فشل الوصول لـ {cat_name}: {res.status_code}")
                continue

            # هنستخدم html.parser عشان نضمن إنه يشتغل في بيئة GitHub Actions بدون lxml
            soup = BeautifulSoup(res.content, 'html.parser')
            items = soup.find_all('item')
            
            count = 0
            for item in items:
                if count >= 5: break # هنسحب 5 أخبار لكل قسم
                
                title = item.find('title').text.strip() if item.find('title') else "عنوان خبر"
                
                # استخراج الصورة من وسام enclosure
                img = ""
                enclosure = item.find('enclosure')
                if enclosure:
                    img = enclosure.get('url')
                
                # لو مفيش enclosure، هنبحث في الوصف (description)
                if not img and item.find('description'):
                    desc_content = item.find('description').text
                    desc_soup = BeautifulSoup(desc_content, 'html.parser')
                    img_tag = desc_soup.find('img')
                    if img_tag: img = img_tag.get('src')

                all_news.append({
                    "category": cat_name,
                    "title": title,
                    "description": "مصراوي: " + title,
                    "image": img if img else "https://media.masrawy.com/Images/masrawy-logo.png",
                    "time": "منذ قليل"
                })
                count += 1
            print(f"✅ تم سحب {count} أخبار من {cat_name}")
                
        except Exception as e:
            print(f"❌ خطأ في {cat_name}: {str(e)}")
            
    return all_news

# الإرسال لجوجل شيت
print("🚀 بدأ سكريبت مصراوي Feed...")
news_data = scrape_news()

if news_data:
    print(f"✅ إجمالي الأخبار المجمعة: {len(news_data)}")
    if NEWS_SCRIPT_URL:
        try:
            res = requests.post(NEWS_SCRIPT_URL, json={"type": "update_news", "data": news_data})
            print(f"🚀 رد جوجل شيت: {res.text}")
        except Exception as e:
            print(f"❌ فشل الإرسال: {e}")
else:
    print("❌ فشل السكريبت في جلب البيانات.")
