import requests
from bs4 import BeautifulSoup
import os

# روابط أخبار جوجل
CATEGORIES = {
    "اقتصاد": "https://news.google.com/rss/search?q=اقتصاد+مصر&hl=ar&gl=EG&ceid=EG:ar",
    "ذهب": "https://news.google.com/rss/search?q=أسعار+الذهب+في+مصر&hl=ar&gl=EG&ceid=EG:ar",
    "عملات": "https://news.google.com/rss/search?q=أسعار+الدولار+والعملات+في+مصر&hl=ar&gl=EG&ceid=EG:ar",
    "طاقة": "https://news.google.com/rss/search?q=أسعار+البنزين+والطاقة+مصر&hl=ar&gl=EG&ceid=EG:ar"
}

# صور احترافية ثابتة لكل قسم في حال عدم وجود صورة للخبر
CATEGORY_DEFAULT_IMAGES = {
    "اقتصاد": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=500",
    "ذهب": "https://images.unsplash.com/photo-1610375461369-d613b564fd5f?w=500",
    "عملات": "https://images.unsplash.com/photo-1580519542036-c47de6196ba5?w=500",
    "طاقة": "https://images.unsplash.com/photo-1605902711622-cfb43c4437d1?w=500"
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
            res = requests.get(url, headers=headers, timeout=30)
            
            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.content, 'html.parser')
            items = soup.find_all('item')
            
            count = 0
            for item in items:
                if count >= 5: break
                
                title_text = item.title.text.strip() if item.title else "عنوان خبر"
                clean_title = title_text.split(' - ')[0]
                source = title_text.split(' - ')[-1] if ' - ' in title_text else "مصدر إخباري"
                
                # جلب رابط الخبر الأصلي
                link = item.link.text.strip() if item.link else ""
                
                # جلب الوقت (نأخذ أول 16 حرف من تاريخ النشر)
                pub_date = item.pubdate.text[:16] if item.find('pubdate') else "اليوم"

                all_news.append({
                    "category": cat_name,
                    "title": clean_title,
                    "description": f"المصدر: {source}",
                    # نستخدم الصورة المخصصة للقسم لضمان شكل جمالي
                    "image": CATEGORY_DEFAULT_IMAGES.get(cat_name, "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=500"),
                    "time": pub_date
                })
                count += 1
            print(f"✅ تم سحب {count} أخبار لـ {cat_name}")
                
        except Exception as e:
            print(f"❌ خطأ في {cat_name}: {str(e)}")
            
    return all_news

# الإرسال لجوجل شيت
print("🚀 بدأ سكريبت Google News...")
news_data = scrape_news()

if news_data:
    if NEWS_SCRIPT_URL:
        try:
            res = requests.post(NEWS_SCRIPT_URL, json={"type": "update_news", "data": news_data})
            print(f"🚀 رد جوجل شيت: {res.text}")
        except Exception as e:
            print(f"❌ فشل الإرسال: {e}")
else:
    print("❌ فشل السكريبت في تجميع البيانات.")
