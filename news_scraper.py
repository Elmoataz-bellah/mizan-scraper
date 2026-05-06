import requests
from bs4 import BeautifulSoup
import os

# روابط موقع اقتصاد مصر - تم تحديث الأقسام لتناسب الموقع
CATEGORIES = {
    "اقتصاد": "https://eqtisadmisr.com/category/%d8%a3%d8%ae%d8%a8%d8%a7%d8%b1-%d8%a7%d9%84%d8%a7%d9%82%d8%aa%d8%b5%d8%a7%d8%af/",
    "عملات": "https://eqtisadmisr.com/category/%d8%a8%d9%86%d9%88%d9%83-%d9%88%d8%b9%d9%85%d9%84%d8%a7%d8%aa/",
    "ذهب": "https://eqtisadmisr.com/category/%d8%a3%d8%b3%d8%b9%d8%a7%d8%b1-%d8%a7%d9%84%d8%b0%d9%87%d8%a8/",
    "طاقة": "https://eqtisadmisr.com/category/%d8%b7%d8%a7%d9%82%d8%a9-%d9%88%d8%aa%d8%b9%d8%af%d9%8a%d9%86/"
}

NEWS_SCRIPT_URL = os.getenv("NEWS_SCRIPT_URL")

def scrape_news():
    all_news = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for cat_name, url in CATEGORIES.items():
        try:
            print(f"📡 فحص قسم {cat_name} في اقتصاد مصر...")
            res = requests.get(url, headers=headers, timeout=20)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.content, 'html.parser')
            
            # المقالات في هذا الموقع غالباً ما تكون داخل عنصر article أو div بـ class محدد
            articles = soup.find_all('article') or soup.select('.post-item')
            
            count = 0
            for art in articles:
                if count >= 3: break
                
                title_tag = art.find('h2') or art.find('h3') or art.find('a')
                if not title_tag: continue
                
                title = title_tag.text.strip()
                if len(title) < 10: continue
                
                link_tag = art.find('a', href=True)
                link = link_tag['href'] if link_tag else ""
                
                # سحب الصورة (غالباً تكون في وسام img داخل الـ article)
                img_tag = art.find('img')
                img = ""
                if img_tag:
                    img = img_tag.get('src') or img_tag.get('data-src') or img_tag.get('srcset', '').split(' ')[0]
                
                if not img or not img.startswith('http'):
                    img = "https://via.placeholder.com/500x300?text=Eqtisad+Misr"

                all_news.append({
                    "category": cat_name,
                    "title": title,
                    "description": "اقتصاد مصر: " + title,
                    "image": img,
                    "time": "منذ قليل"
                })
                count += 1
                
        except Exception as e:
            print(f"❌ خطأ في {cat_name}: {e}")
            
    return all_news

# التنفيذ والإرسال
print("🚀 بدأ سكريبت اقتصاد مصر...")
news_data = scrape_news()

if news_data:
    print(f"✅ نجاح! تم سحب {len(news_data)} خبر.")
    if NEWS_SCRIPT_URL:
        try:
            res = requests.post(NEWS_SCRIPT_URL, json={"type": "update_news", "data": news_data})
            print(f"🚀 رد جوجل: {res.text}")
        except Exception as e:
            print(f"❌ فشل الإرسال: {e}")
    else:
        print("⚠️ تحذير: NEWS_SCRIPT_URL غير معرف")
else:
    print("❌ فشل السكريبت في العثور على أخبار.")
