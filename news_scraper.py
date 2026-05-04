import requests
from bs4 import BeautifulSoup
import os

# روابط الأقسام من موقع مباشر مصر
CATEGORIES = {
    "اقتصاد": "https://www.mubasher.info/markets/EGX/news",
    "عملات": "https://www.mubasher.info/markets/currencies/news",
    "ذهب": "https://www.mubasher.info/markets/commodities/news",
    "طاقة": "https://www.mubasher.info/markets/commodities/news" # مباشر بيجمعهم في قسم السلع
}

NEWS_SCRIPT_URL = os.getenv("NEWS_SCRIPT_URL")

def scrape_news():
    all_news = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for cat_name, url in CATEGORIES.items():
        try:
            print(f"جاري سحب أخبار قسم: {cat_name} من مباشر...")
            res = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(res.content, 'html.parser')
            
            # في موقع مباشر، المقالات بتكون داخل تاجات <a> أو وحدات mi-article
            articles = soup.select('.mi-article-list-item') or soup.find_all('div', class_='mi-article-list-item')
            
            if not articles:
                # محاولة تانية لو الموقع غير التصميم
                articles = soup.find_all('a', class_='mi-article-list-item__title')[:5]

            for art in articles[:5]:
                try:
                    # سحب العنوان والرابط
                    title_tag = art.select_one('.mi-article-list-item__title') or art
                    title = title_tag.text.strip()
                    link = "https://www.mubasher.info" + title_tag['href'] if title_tag.has_attr('href') else ""
                    
                    # سحب الصورة
                    img_tag = art.find('img')
                    img = img_tag.get('src') or img_tag.get('data-src') if img_tag else ""
                    
                    # سحب الوقت
                    time_tag = art.select_one('.mi-article-list-item__time') or art.select_one('span')
                    time = time_tag.text.strip() if time_tag else "منذ قليل"
                    
                    # الوصف (مباشر مش بيحط وصف كبير في القائمة فبناخد العنوان كبداية)
                    desc = "اضغط للمزيد من التفاصيل حول " + title

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
                    continue
                    
        except Exception as e:
            print(f"❌ خطأ في القسم {cat_name}: {e}")
            continue
            
    return all_news

# التنفيذ والإرسال
news_data = scrape_news()

if news_data:
    print(f"✅ تم سحب {len(news_data)} خبر من مباشر بنجاح!")
    if NEWS_SCRIPT_URL:
        try:
            res = requests.post(NEWS_SCRIPT_URL, json={"type": "update_news", "data": news_data})
            print(f"🚀 رد جوجل: {res.text}")
        except Exception as e:
            print(f"❌ خطأ في الإرسال: {e}")
    else:
        print("⚠️ NEWS_SCRIPT_URL غير معرف")
else:
    print("❌ فشل السكريبت في الحصول على أخبار من مباشر.")
