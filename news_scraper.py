import requests
from bs4 import BeautifulSoup
import os

# روابط مباشر مصر
CATEGORIES = {
    "اقتصاد": "https://www.mubasher.info/markets/EGX/news",
    "عملات": "https://www.mubasher.info/markets/currencies/news",
    "ذهب": "https://www.mubasher.info/markets/commodities/news",
    "طاقة": "https://www.mubasher.info/markets/commodities/news"
}

# سحب الرابط من Secrets جيت هاب
NEWS_SCRIPT_URL = os.getenv("NEWS_SCRIPT_URL")

def scrape_news():
    all_news = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for cat_name, url in CATEGORIES.items():
        try:
            print(f"📡 جاري فحص قسم: {cat_name}...")
            res = requests.get(url, headers=headers, timeout=20)
            soup = BeautifulSoup(res.content, 'html.parser')
            
            # محاولة البحث عن المقالات بأكثر من طريقة (الـ Selector ده أدق لموقع مباشر)
            articles = soup.select('a.mi-article-list-item__title') or \
                       soup.select('.mi-article-list-item') or \
                       soup.find_all('a', href=True)
            
            count = 0
            for art in articles:
                if count >= 5: break # نكتفي بـ 5 أخبار لكل قسم
                
                title = art.text.strip()
                # التأكد إن النص مش فاضي وإنه خبر فعلاً (طويل كفاية)
                if not title or len(title) < 10: continue 
                
                link = art['href'] if art.has_attr('href') else ""
                if link and not link.startswith('http'):
                    link = "https://www.mubasher.info" + link

                # سحب الصورة لو موجودة
                img_tag = art.find_parent().find('img') if art.find_parent() else None
                img = img_tag.get('src') or img_tag.get('data-src') if img_tag else "https://via.placeholder.com/150"

                all_news.append({
                    "category": cat_name,
                    "title": title,
                    "description": "اضغط للمزيد من التفاصيل حول: " + title,
                    "image": img,
                    "time": "منذ قليل"
                })
                count += 1
                
        except Exception as e:
            print(f"❌ خطأ في القسم {cat_name}: {e}")
            continue
            
    return all_news

# التنفيذ
print("🚀 بدأ سكريبت الأخبار...")
news_data = scrape_news()

if news_data:
    print(f"✅ تم سحب {len(news_data)} خبر بنجاح!")
    if NEWS_SCRIPT_URL:
        try:
            print(f"📤 جاري إرسال البيانات إلى Google Sheets...")
            res = requests.post(NEWS_SCRIPT_URL, json={"type": "update_news", "data": news_data})
            print(f"🚀 رد جوجل النهائي: {res.text}")
        except Exception as e:
            print(f"❌ خطأ في الإرسال: {e}")
    else:
        print("⚠️ تحذير: NEWS_SCRIPT_URL غير معرف في Secrets جيت هاب.")
else:
    print("❌ فشل السكريبت في العثور على أي أخبار، تأكد من الروابط.")
