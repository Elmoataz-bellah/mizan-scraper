import requests
from bs4 import BeautifulSoup
import os

# روابط RSS مصراوي - شغالة ومستقرة جداً
CATEGORIES = {
    "اقتصاد": "https://www.masrawy.com/rss/economy",
    "ذهب": "https://www.masrawy.com/rss/listing?id=126", # قسم الذهب والأسعار
    "عملات": "https://www.masrawy.com/rss/listing?id=127", # أسعار العملات
    "طاقة": "https://www.masrawy.com/rss/listing?id=518"  # طاقة وبترول
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
                print(f"⚠️ فشل الوصول لرابط {cat_name}: {res.status_code}")
                continue

            # تحليل الـ XML
            soup = BeautifulSoup(res.content, 'xml')
            items = soup.find_all('item')
            
            count = 0
            for item in items:
                if count >= 4: break # هنسحب 4 أخبار لكل قسم
                
                title = item.title.text.strip()
                link = item.link.text.strip()
                
                # استخراج الصورة (في مصراوي بتكون في tag اسمه media:content أو enclosure)
                img = ""
                media_content = item.find('media:content')
                if media_content:
                    img = media_content.get('url')
                elif item.find('enclosure'):
                    img = item.find('enclosure').get('url')
                
                # لو مفيش صورة، بنحاول نجيبها من الـ Description
                if not img and item.description:
                    desc_soup = BeautifulSoup(item.description.text, 'html.parser')
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
            print(f"✅ تم سحب {count} أخبار من قسم {cat_name}")
                
        except Exception as e:
            print(f"❌ خطأ في {cat_name}: {e}")
            
    return all_news

# التنفيذ والإرسال لجوجل شيت
print("🚀 بدأ سكريبت مصراوي RSS...")
news_data = scrape_news()

if news_data:
    print(f"✅ تم تجميع {len(news_data)} خبر.")
    if NEWS_SCRIPT_URL:
        try:
            res = requests.post(NEWS_SCRIPT_URL, json={"type": "update_news", "data": news_data})
            print(f"🚀 رد جوجل: {res.text}")
        except Exception as e:
            print(f"❌ فشل الإرسال لجوجل: {e}")
else:
    print("❌ فشل السكريبت: الروابط لم ترجع أي بيانات.")
