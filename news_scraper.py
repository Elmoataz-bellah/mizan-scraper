import requests
from bs4 import BeautifulSoup
import os

# روابط Investing لكل قسم (أمثلة)
CATEGORIES = {
    "اقتصاد": "https://ar.investing.com/news/economy",
    "عملات": "https://ar.investing.com/news/forex-news",
    "ذهب": "https://ar.investing.com/news/commodities-news/1", # الذهب تبع السلع
    "طاقة": "https://ar.investing.com/news/commodities-news/2" # البترول والطاقة
}

NEWS_SCRIPT_URL = os.getenv("NEWS_SCRIPT_URL")

def scrape_news():
    all_news = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for cat_name, url in CATEGORIES.items():
        try:
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.content, 'html.parser')
            # البحث عن البلوك الخاص بالخبر (تأكد من الـ class من الموقع)
            articles = soup.find_all('article', limit=5) 
            
            for art in articles:
                title = art.find('a', {'class': 'title'}).text.strip()
                img = art.find('img')['src'] if art.find('img') else ""
                desc = art.find('p').text.strip() if art.find('p') else "لا يوجد تفاصيل"
                time = "منذ قليل" # ممكن تسحب الوقت الحقيقي برضه
                
                all_news.append({
                    "category": cat_name,
                    "title": title,
                    "description": desc,
                    "image": img,
                    "time": time
                })
        except:
            continue
    return all_news

news_data = scrape_news()
if news_data and NEWS_SCRIPT_URL:
    requests.post(NEWS_SCRIPT_URL, json={"type": "update_news", "data": news_data})
