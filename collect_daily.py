"""
Daily Data Collection Script
Run this ONCE per day for 30 days to build your training dataset
"""

import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import time

# Load API keys
load_dotenv()
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

# Major ports to monitor (reduced to 15 for free tier limits)
PORTS = {
    'Rotterdam': {'lat': 51.9225, 'lon': 4.47917, 'country': 'Netherlands'},
    'Singapore': {'lat': 1.2897, 'lon': 103.8501, 'country': 'Singapore'},
    'Shanghai': {'lat': 31.2304, 'lon': 121.4737, 'country': 'China'},
    'Los Angeles': {'lat': 33.7405, 'lon': -118.2708, 'country': 'USA'},
    'Dubai': {'lat': 25.2854, 'lon': 55.3308, 'country': 'UAE'},
    'Hong Kong': {'lat': 22.3193, 'lon': 114.1694, 'country': 'China'},
    'Hamburg': {'lat': 53.5511, 'lon': 9.9937, 'country': 'Germany'},
    'Antwerp': {'lat': 51.2194, 'lon': 4.4025, 'country': 'Belgium'},
    'Busan': {'lat': 35.1796, 'lon': 129.0756, 'country': 'South Korea'},
    'Long Beach': {'lat': 33.7701, 'lon': -118.1937, 'country': 'USA'},
    'New York': {'lat': 40.6895, 'lon': -74.0447, 'country': 'USA'},
    'Qingdao': {'lat': 36.0671, 'lon': 120.3826, 'country': 'China'},
    'Guangzhou': {'lat': 23.1291, 'lon': 113.2644, 'country': 'China'},
    'Shenzhen': {'lat': 22.5431, 'lon': 114.0579, 'country': 'China'},
    'Ningbo': {'lat': 29.8683, 'lon': 121.544, 'country': 'China'},
}

def get_weather_data(port_name, lat, lon):
    """Get current weather for a port"""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                'port': port_name,
                'temperature': data['main']['temp'],
                'wind_speed': data['wind']['speed'],
                'visibility': data.get('visibility', 10000) / 1000,
                'weather': data['weather'][0]['main'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure']
            }
    except Exception as e:
        print(f"  Weather error for {port_name}: {str(e)}")
    
    return None

def calculate_weather_risk(weather_data):
    """Calculate weather risk score (0-100)"""
    if not weather_data:
        return 20
    
    risk = 0
    
    # Wind risk
    wind = weather_data.get('wind_speed', 0)
    if wind > 20:
        risk += 40
    elif wind > 15:
        risk += 25
    elif wind > 10:
        risk += 10
    
    # Visibility risk
    vis = weather_data.get('visibility', 10)
    if vis < 2:
        risk += 30
    elif vis < 5:
        risk += 15
    
    # Weather condition risk
    weather = weather_data.get('weather', '').lower()
    if 'storm' in weather or 'thunder' in weather:
        risk += 30
    elif 'rain' in weather:
        risk += 10
    
    return min(100, risk)

def get_news_sentiment(port_name):
    """Get news sentiment for a port"""
    url = "https://newsapi.org/v2/everything"
    
    # Search for port-related news
    query = f'"{port_name}" AND (port OR shipping OR delay OR strike OR congestion)'
    
    params = {
        'q': query,
        'language': 'en',
        'sortBy': 'relevancy',
        'apiKey': NEWS_API_KEY,
        'pageSize': 5
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            if not articles:
                return {
                    'port': port_name,
                    'article_count': 0,
                    'sentiment_score': 50
                }
            
            # Simple sentiment analysis based on keywords
            negative_keywords = ['delay', 'strike', 'congestion', 'closed', 'disruption', 
                               'problem', 'issue', 'crisis', 'shortage']
            positive_keywords = ['efficient', 'improved', 'expansion', 'growth', 'upgrade']
            
            neg_count = 0
            pos_count = 0
            
            for article in articles:
                text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
                neg_count += sum(1 for word in negative_keywords if word in text)
                pos_count += sum(1 for word in positive_keywords if word in text)
            
            total = neg_count + pos_count
            if total == 0:
                sentiment = 50
            else:
                sentiment = (neg_count / total) * 100
            
            return {
                'port': port_name,
                'article_count': len(articles),
                'sentiment_score': round(sentiment, 2)
            }
    except Exception as e:
        print(f"  News error for {port_name}: {str(e)}")
    
    return {
        'port': port_name,
        'article_count': 0,
        'sentiment_score': 50
    }

def estimate_vessel_congestion(port_name):
    """Estimate vessel congestion based on port characteristics"""
    import random
    from datetime import datetime
    
    port_base_levels = {
        'Shanghai': 25, 'Singapore': 22, 'Rotterdam': 18, 'Dubai': 16,
        'Los Angeles': 20, 'Long Beach': 18, 'Hong Kong': 17, 'Hamburg': 15,
        'Antwerp': 14, 'Busan': 16, 'New York': 15, 'Qingdao': 20,
        'Guangzhou': 18, 'Shenzhen': 17, 'Ningbo': 19
    }
    
    base = port_base_levels.get(port_name, 15)
    
    day_of_week = datetime.now().weekday()
    if day_of_week < 5:
        base += random.randint(2, 5)
    else:
        base -= random.randint(1, 3)
    
    variation = random.randint(-3, 3)
    vessel_count = max(5, base + variation)
    
    wait_time = 2.0 + (vessel_count - 10) * 0.3
    wait_time = max(1.0, wait_time)
    
    return {
        'port': port_name,
        'vessel_count': vessel_count,
        'wait_time_hours': round(wait_time, 1)
    }

def collect_daily_data():
    """Main function to collect all data"""
    print("="*60)
    print(f"DAILY DATA COLLECTION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    all_data = []
    
    for port_name, port_info in PORTS.items():
        print(f"\n📍 {port_name}...")
        
        weather = get_weather_data(port_name, port_info['lat'], port_info['lon'])
        time.sleep(1)
        
        news = get_news_sentiment(port_name)
        time.sleep(2)
        
        vessels = estimate_vessel_congestion(port_name)
        
        weather_risk = calculate_weather_risk(weather) if weather else 20
        
        record = {
            'timestamp': datetime.now(),
            'port': port_name,
            'country': port_info['country'],
            'vessel_count': vessels['vessel_count'],
            'wait_time_hours': vessels['wait_time_hours'],
            'temperature': weather['temperature'] if weather else None,
            'wind_speed': weather['wind_speed'] if weather else None,
            'visibility': weather['visibility'] if weather else None,
            'weather_condition': weather['weather'] if weather else None,
            'weather_risk': weather_risk,
            'article_count': news['article_count'],
            'news_sentiment': news['sentiment_score'],
            'risk_score': round(
                (vessels['wait_time_hours'] / 10 * 40) +
                (news['sentiment_score'] * 0.35) +
                (weather_risk * 0.25),
                2
            )
        }
        
        all_data.append(record)
        
        print(f"  ✓ Vessels: {record['vessel_count']}")
        print(f"  ✓ Wait: {record['wait_time_hours']}h")
        print(f"  ✓ Weather Risk: {record['weather_risk']}%")
        print(f"  ✓ News Sentiment: {record['news_sentiment']}%")
        print(f"  ✓ RISK SCORE: {record['risk_score']}%")
    
    df = pd.DataFrame(all_data)
    
    today = datetime.now().strftime('%Y%m%d')
    filepath = f'data/daily_collections/data_{today}.csv'
    
    df.to_csv(filepath, index=False)
    
    print(f"\n{'='*60}")
    print(f"✓ Data saved to: {filepath}")
    print(f"✓ Total records: {len(df)}")
    print(f"{'='*60}\n")
    
    master_file = 'data/all_data.csv'
    if os.path.exists(master_file):
        df.to_csv(master_file, mode='a', header=False, index=False)
        print(f"✓ Appended to master file: {master_file}")
    else:
        df.to_csv(master_file, index=False)
        print(f"✓ Created master file: {master_file}")
    
    master_df = pd.read_csv(master_file)
    days_collected = len(master_df) // len(PORTS)
    print(f"\n📊 COLLECTION PROGRESS: {days_collected}/30 days")
    
    if days_collected >= 30:
        print("\n🎉 YOU HAVE ENOUGH DATA TO TRAIN THE MODEL!")
        print("Run: python train_model.py")

if __name__ == "__main__":
    collect_daily_data()