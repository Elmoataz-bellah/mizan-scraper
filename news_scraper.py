import requests
from bs4 import BeautifulSoup
import os
import time
import random

CATEGORIES = {
    "اقتصاد": "https://eqtisadmisr.com/category/%d8%a3%d8%ae%d8%a8%d8%a7%d8%b1-%d8%a7%d9%84%d8%a7%d9%82%d8%aa%d8%b5%d8%a7%d8%af/",
    "عملات": "https://eqtisadmisr.com/category/%d8%a8%d9%86%d9%88%d9%83-%d9%88%d8%b9%d9%85%d9%84%d8%a7%d8%aa/",
    "ذهب": "https://eqtisadmisr.com/category/%d8%a3%d8%b3%d8%b9%d8%a7%d8%b1-%d8%a7%d9%84%d8%b0%d9%87%d8%a8/",
    "طاقة": "https://eqtisadmisr.com/category/%d8%b7%d8%a7%d9%82%d8%a9-%d9%88%d8%aa%d8%b9%d8%af%d9%8a%d9%86/"
}

NEWS_SCRIPT_URL = os.getenv("NEWS_SCRIPT_URL")

def scrape_news():
    all_news = []
    # إنشاء جلسة للحفاظ على الـ Cookies كأننا متصفح حقيقي
    session = requests.Session()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
        'Referer': 'https://www.google.com/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    cat_items = list(CATEGORIES.items())
    random.shuffle(cat_items) # تغيير الترتيب عشان منبقاش متوقعين

    for cat_name, url in cat_items:
        try:
            print(f"📡 محاولة سحب قسم: {cat_name}...")
            
            # انتظر وقت عشوائي بين 3 لـ 7 ثواني عشان الموقع ميعملش بلوك
            wait_time = random.uniform(3, 7)
            time.sleep(wait_time)
            
            res = session.get(url, headers=headers, timeout=30)
            print(f"📥 حالة الاستجابة لـ {cat_name}: {res.status_code}")
            
            if res.status_code == 429:
                print(f"⚠️ الموقع اكتشف البوت في قسم {cat_name}، جاري التخطي...")
                continue

            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.content, 'html.parser')
            articles = soup.select('article') or soup.select('.post-item')
            
            count = 0
            for art in articles:
                if count >= 3: break
                
                title_tag = art.select_one('h2 a') or art.select_one('h3 a') or art.find('a')
                if not title_tag or not title_tag.text.strip(): continue
                
                title = title_tag.text.strip()
                img_tag = art.find('img')
                img = img_tag.get('src') if img_tag else ""

                all_news.append({
                    "category": cat_name,
                    "title": title,
                    "description": "اقتصاد مصر: " + title,
                    "image": img if img and img.startswith('http') else "https://via.placeholder.com/500",
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
            res = requests.post(NEWS_SCRIPT_URL, json={"type": "update_news", "data": news_data})
            print(f"🚀 رد السيرفر: {res.text}")
        except Exception as e:
            print(f"❌ خطأ إرسال: {str(e)}")
else:
    print("⚠️ فشل السحب: الموقع لسه عامل حظر 429.")
