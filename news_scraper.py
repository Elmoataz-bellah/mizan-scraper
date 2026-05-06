import requests
from bs4 import BeautifulSoup
import os

# استخدام موقع اقتصاد مصر
CATEGORIES = {
    "اقتصاد": "https://eqtisadmisr.com/category/%d8%a3%d8%ae%d8%a8%d8%a7%d8%b1-%d8%a7%d9%84%d8%a7%d9%82%d8%aa%d8%b5%d8%a7%d8%af/",
    "عملات": "https://eqtisadmisr.com/category/%d8%a8%d9%86%d9%88%d9%83-%d9%88%d8%b9%d9%85%d9%84%d8%a7%d8%aa/",
    "ذهب": "https://eqtisadmisr.com/category/%d8%a3%d8%b3%d8%a7%d8%b1-%d8%a7%d9%84%d8%b0%d9%87%d8%a8/",
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
            print(f"📡 محاولة سحب قسم: {cat_name}...")
            res = requests.get(url, headers=headers, timeout=30)
            print(f"📥 حالة الاستجابة لـ {cat_name}: {res.status_code}")
            
            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.content, 'html.parser')
            # تعديل الـ selectors لضمان التقاط المحتوى
            articles = soup.select('article') or soup.select('.post-item') or soup.select('.type-post')
            
            print(f"🔎 عدد المقالات المكتشفة في {cat_name}: {len(articles)}")
            
            count = 0
            for art in articles:
                if count >= 3: break
                
                title_tag = art.select_one('h2 a') or art.select_one('h3 a') or art.find('a')
                if not title_tag: continue
                
                title = title_tag.text.strip()
                link = title_tag['href']
                
                img_tag = art.find('img')
                img = ""
                if img_tag:
                    img = img_tag.get('src') or img_tag.get('data-src') or img_tag.get('srcset', '').split(' ')[0]

                all_news.append({
                    "category": cat_name,
                    "title": title,
                    "description": "اقتصاد مصر: " + title,
                    "image": img if img else "https://via.placeholder.com/500",
                    "time": "منذ قليل"
                })
                count += 1
                
        except Exception as e:
            print(f"❌ خطأ في {cat_name}: {str(e)}")
            
    return all_news

# التنفيذ
news_data = scrape_news()

if news_data:
    print(f"✅ تم سحب {len(news_data)} خبر بنجاح.")
    if NEWS_SCRIPT_URL:
        try:
            # طباعة الرابط (للتأكد فقط، سيظهر مشفراً في GitHub)
            print(f"📤 إرسال إلى: {NEWS_SCRIPT_URL[:20]}...")
            res = requests.post(NEWS_SCRIPT_URL, json={"type": "update_news", "data": news_data})
            print(f"🚀 رد السيرفر: {res.text}")
        except Exception as e:
            print(f"❌ خطأ إرسال: {str(e)}")
    else:
        print("🚨 خطأ: الرابط NEWS_SCRIPT_URL غير موجود في إعدادات GitHub Secrets!")
else:
    print("⚠️ فشل السحب: لم يتم العثور على أي أخبار في الموقع!")
