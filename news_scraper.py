import requests
from bs4 import BeautifulSoup
import os

# روابط الأقسام المحدثة
CATEGORIES = {
    "اقتصاد": "https://ar.investing.com/news/economy",
    "عملات": "https://ar.investing.com/news/forex-news",
    "ذهب": "https://ar.investing.com/news/commodities-news",
    "طاقة": "https://ar.investing.com/news/commodities-news" 
}

NEWS_SCRIPT_URL = os.getenv("NEWS_SCRIPT_URL")

def scrape_news():
    all_news = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3'
    }
    
    for cat_name, url in CATEGORIES.items():
        try:
            print(f"جاري سحب أخبار قسم: {cat_name}...")
            res = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(res.content, 'html.parser')
            
            # المواقع الحديثة بتستخدم التاج <article> أو <div> مع داتا أتربيوتس
            # السطر ده بيدور على العناصر اللي شايلة الخبر بشكل أعم
            articles = soup.select('article[data-test="article-item"]') or soup.select('.articleItem') or soup.find_all('article', limit=5)
            
            if not articles:
                print(f"⚠️ تحذير: لم يتم العثور على مقالات في قسم {cat_name}")
                continue

            for art in articles[:5]: # نكتفي بـ 5 أخبار لكل قسم
                try:
                    # محاولة سحب العنوان (أهم سطر)
                    title_tag = art.select_one('a[data-test="article-title-link"]') or art.find('a', class_='title') or art.find('a')
                    title = title_tag.text.strip() if title_tag else ""
                    
                    # محاولة سحب الرابط
                    link = title_tag['href'] if title_tag and title_tag.has_attr('href') else ""
                    if link and not link.startswith('http'):
                        link = "https://ar.investing.com" + link

                    # محاولة سحب الصورة
                    img_tag = art.find('img')
                    img = img_tag.get('src') or img_tag.get('data-src') if img_tag else ""

                    # محاولة سحب الوصف
                    desc_tag = art.select_one('p[data-test="article-description"]') or art.find('p')
                    desc = desc_tag.text.strip() if desc_tag else "اضغط للمزيد من التفاصيل"
                    
                    # محاولة سحب الوقت
                    time_tag = art.select_one('time') or art.find('span', class_='date')
                    time = time_tag.text.strip() if time_tag else "منذ قليل"
                    
                    if title:
                        all_news.append({
                            "category": cat_name,
                            "title": title,
                            "description": desc,
                            "image": img,
                            "time": time,
                            "link": link
                        })
                except Exception as e:
                    print(f"خطأ في سحب خبر مفرد: {e}")
                    continue
                    
        except Exception as e:
            print(f"خطأ في الاتصال بالقسم {cat_name}: {e}")
            continue
            
    return all_news

# التنفيذ
news_data = scrape_news()

if news_data:
    print(f"✅ تم سحب {len(news_data)} خبر بنجاح!")
    if NEWS_SCRIPT_URL:
        try:
            res = requests.post(NEWS_SCRIPT_URL, json={"type": "update_news", "data": news_data})
            print(f"🚀 رد جوجل: {res.text}")
        except Exception as e:
            print(f"❌ خطأ في الإرسال: {e}")
    else:
        print("⚠️ رابط NEWS_SCRIPT_URL غير معرف في الـ Secrets")
else:
    print("❌ فشل السكريبت في الحصول على أي أخبار.")
