# event_analyzer/event_predictor.py
"""
پیش‌بینی‌کننده نهایی رویدادهای جهانی
پشتیبانی از:
- انتخابات و سیاست
- اقتصاد و بازارها
- آب و هوا و بلایای طبیعی
- جوایز (اسکار، نوبل، گرمی)
- فناوری و نوآوری
- فرهنگ و سرگرمی
- هر رویداد دلخواه کاربر
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import numpy as np
from collections import defaultdict
import logging
import re
import random

# Machine Learning
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import joblib

# Time Series
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet

# Local
from core.numerology_engine import NumerologyEngine
from ai.genius_ai import GeniusAI
from config import *

logger = logging.getLogger(__name__)

class EventPredictor:
    """
    پیش‌بینی‌کننده هر نوع رویدادی در جهان
    با استفاده از ترکیب عددشناسی، AI، و داده‌های تاریخی
    """
    
    # ==================== دسته‌بندی رویدادها ====================
    
    EVENT_CATEGORIES = {
        'politics': {
            'name': '🗳️ Politics & Elections',
            'subcategories': ['presidential_election', 'parliamentary_election', 'referendum', 'leadership_change', 'policy_decision'],
            'apis': ['newsapi', 'google_news'],
            'numerology_impact': 0.3,
            'historical_impact': 0.4,
            'current_impact': 0.3
        },
        'economics': {
            'name': '📊 Economics & Markets',
            'subcategories': ['market_crash', 'recession', 'inflation', 'interest_rate', 'oil_price', 'gold_price'],
            'apis': ['yahoo_finance', 'coingecko', 'world_bank'],
            'numerology_impact': 0.2,
            'historical_impact': 0.5,
            'current_impact': 0.3
        },
        'weather': {
            'name': '🌤️ Weather & Natural Disasters',
            'subcategories': ['earthquake', 'hurricane', 'flood', 'drought', 'heatwave', 'solar_storm'],
            'apis': ['noaa', 'openweathermap', 'usgs'],
            'numerology_impact': 0.15,
            'historical_impact': 0.35,
            'current_impact': 0.5
        },
        'entertainment': {
            'name': '🎬 Entertainment & Awards',
            'subcategories': ['oscars', 'grammys', 'emmys', 'golden_globes', 'nobel_prize', 'pulitzer'],
            'apis': ['imdb', 'spotify', 'newsapi'],
            'numerology_impact': 0.4,
            'historical_impact': 0.3,
            'current_impact': 0.3
        },
        'technology': {
            'name': '💻 Technology & Innovation',
            'subcategories': ['product_launch', 'ai_breakthrough', 'space_mission', 'cyber_attack', 'patent'],
            'apis': ['techcrunch', 'wired', 'newsapi'],
            'numerology_impact': 0.25,
            'historical_impact': 0.3,
            'current_impact': 0.45
        },
        'sports': {
            'name': '🏆 Sports Events',
            'subcategories': ['world_cup', 'super_bowl', 'olympics', 'champions_league_final'],
            'apis': ['sportsdb', 'espn'],
            'numerology_impact': 0.35,
            'historical_impact': 0.4,
            'current_impact': 0.25
        },
        'health': {
            'name': '🏥 Health & Medicine',
            'subcategories': ['pandemic', 'vaccine', 'medical_breakthrough', 'health_crisis'],
            'apis': ['who', 'cdc', 'newsapi'],
            'numerology_impact': 0.2,
            'historical_impact': 0.4,
            'current_impact': 0.4
        },
        'social': {
            'name': '👥 Social & Cultural',
            'subcategories': ['protest', 'movement', 'trend', 'viral_event'],
            'apis': ['twitter', 'reddit', 'newsapi'],
            'numerology_impact': 0.3,
            'historical_impact': 0.2,
            'current_impact': 0.5
        },
        'custom': {
            'name': '✨ Custom Event',
            'subcategories': ['user_defined'],
            'apis': [],
            'numerology_impact': 0.5,
            'historical_impact': 0.2,
            'current_impact': 0.3
        }
    }
    
    # ==================== APIهای عمومی ====================
    
    NEWS_API = "https://newsapi.org/v2"
    WEATHER_API = "https://api.openweathermap.org/data/2.5"
    NASA_API = "https://api.nasa.gov"
    USGS_API = "https://earthquake.usgs.gov/fdsnws/event/1"
    
    def __init__(self, db_session=None, numerology=None, ai=None):
        self.db = db_session
        self.numerology = numerology or NumerologyEngine(db_session)
        self.ai = ai or GeniusAI(db_session, self.numerology)
        
        # مدل‌ها
        self.models = {}
        self.scalers = {}
        
        # کش
        self.cache = {}
        self.cache_timeout = 3600  # 1 ساعت
        
        # داده‌های تاریخی
        self.historical_events = self.load_historical_events()
        
        logger.info("🌍 EventPredictor initialized with 8 categories and 20+ subcategories")
    
    def load_historical_events(self):
        """بارگذاری رویدادهای تاریخی مهم"""
        
        events = {
            'elections': [
                {'year': 2020, 'country': 'USA', 'event': 'presidential_election', 'winner': 'Biden', 'loser': 'Trump'},
                {'year': 2016, 'country': 'USA', 'event': 'presidential_election', 'winner': 'Trump', 'loser': 'Clinton'},
                {'year': 2019, 'country': 'UK', 'event': 'general_election', 'winner': 'Johnson', 'loser': 'Corbyn'}
            ],
            'economic_crises': [
                {'year': 2008, 'event': 'financial_crisis', 'cause': 'housing_bubble', 'severity': 9},
                {'year': 2020, 'event': 'covid_crash', 'cause': 'pandemic', 'severity': 8},
                {'year': 1997, 'event': 'asian_financial_crisis', 'cause': 'currency_crisis', 'severity': 7}
            ],
            'natural_disasters': [
                {'year': 2004, 'event': 'indian_ocean_tsunami', 'magnitude': 9.1, 'deaths': 230000},
                {'year': 2010, 'event': 'haiti_earthquake', 'magnitude': 7.0, 'deaths': 160000},
                {'year': 2011, 'event': 'japan_earthquake', 'magnitude': 9.0, 'deaths': 15800}
            ],
            'awards': [
                {'year': 2023, 'event': 'oscars', 'best_picture': 'Everything Everywhere All At Once'},
                {'year': 2023, 'event': 'nobel_peace', 'winner': 'Narges Mohammadi'},
                {'year': 2023, 'event': 'grammys', 'album_of_year': 'Harry\'s House'}
            ],
            'tech_breakthroughs': [
                {'year': 2022, 'event': 'chatgpt_launch', 'impact': 10},
                {'year': 2019, 'event': 'covid_vaccine', 'impact': 10},
                {'year': 2015, 'event': 'crispr_breakthrough', 'impact': 9}
            ]
        }
        
        return events
    
    # ==================== تشخیص رویداد ====================
    
    def detect_event(self, query: str) -> Tuple[str, str, Dict]:
        """
        تشخیص خودکار نوع رویداد از متن کاربر
        
        Args:
            query: متن کاربر (مثال: "Who will win the 2024 US election?")
        
        Returns:
            (category, subcategory, extracted_info)
        """
        
        query_lower = query.lower()
        result = {
            'category': 'custom',
            'subcategory': 'user_defined',
            'year': None,
            'location': None,
            'entities': []
        }
        
        # تشخیص سال
        year_pattern = r'\b(20\d{2})\b'
        year_match = re.search(year_pattern, query)
        if year_match:
            result['year'] = int(year_match.group(1))
        
        # تشخیص دسته‌بندی
        category_keywords = {
            'politics': ['election', 'president', 'vote', 'campaign', 'parliament', 'referendum', 'prime minister'],
            'economics': ['market', 'economy', 'stock', 'crash', 'recession', 'inflation', 'interest rate', 'oil price'],
            'weather': ['weather', 'earthquake', 'hurricane', 'storm', 'flood', 'drought', 'tornado', 'tsunami'],
            'entertainment': ['oscar', 'grammy', 'emmy', 'nobel', 'award', 'movie', 'film', 'actor', 'singer'],
            'technology': ['tech', 'ai', 'artificial intelligence', 'space', 'nasa', 'rocket', 'launch', 'cyber'],
            'sports': ['world cup', 'super bowl', 'olympics', 'champions league', 'final', 'match', 'game'],
            'health': ['pandemic', 'vaccine', 'virus', 'covid', 'health', 'medicine', 'disease'],
            'social': ['protest', 'movement', 'trend', 'viral', 'social media']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                result['category'] = category
                
                # تشخیص زیردسته
                for sub in self.EVENT_CATEGORIES[category]['subcategories']:
                    if sub.replace('_', ' ') in query_lower:
                        result['subcategory'] = sub
                        break
                
                break
        
        # تشخیص مکان
        countries = ['usa', 'us', 'america', 'uk', 'britain', 'france', 'germany', 'china', 'japan', 'russia']
        for country in countries:
            if country in query_lower:
                result['location'] = country.upper()
                break
        
        return result['category'], result['subcategory'], result
    
    # ==================== پیش‌بینی رویداد ====================
    
    async def predict_event(self, query: str) -> Dict[str, Any]:
        """
        پیش‌بینی هر نوع رویدادی
        
        Args:
            query: سوال کاربر (مثال: "Who will win the 2024 US election?")
        
        Returns:
            پیش‌بینی کامل
        """
        
        # تشخیص رویداد
        category, subcategory, info = self.detect_event(query)
        
        logger.info(f"🌍 Predicting event: {query} [{category} - {subcategory}]")
        
        # ==================== تحلیل عددشناسی ====================
        
        numerology_result = self._analyze_event_numerology(query, info)
        
        # ==================== تحلیل داده‌های تاریخی ====================
        
        historical_analysis = self._analyze_historical_patterns(category, subcategory, info)
        
        # ==================== تحلیل اخبار جاری ====================
        
        news_analysis = await self._analyze_current_news(query, category, info)
        
        # ==================== پیش‌بینی با AI ====================
        
        ai_input = {
            'query': query,
            'category': category,
            'subcategory': subcategory,
            'year': info.get('year'),
            'location': info.get('location'),
            'numerology': numerology_result,
            'historical': historical_analysis,
            'news': news_analysis
        }
        
        ai_prediction = await self.ai.predict(ai_input, 'event')
        
        # ==================== ترکیب نتایج ====================
        
        event_info = self.EVENT_CATEGORIES.get(category, self.EVENT_CATEGORIES['custom'])
        
        # وزن‌دهی
        num_weight = event_info['numerology_impact']
        hist_weight = event_info['historical_impact']
        current_weight = event_info['current_impact']
        ai_weight = 0.2
        
        # تنظیم مجدد
        total = num_weight + hist_weight + current_weight + ai_weight
        num_weight /= total
        hist_weight /= total
        current_weight /= total
        ai_weight /= total
        
        # امتیاز نهایی
        final_score = (
            numerology_result.get('score', 0.5) * num_weight +
            historical_analysis.get('score', 0.5) * hist_weight +
            news_analysis.get('sentiment', 0.5) * current_weight +
            ai_prediction.get('value', 0.5) * ai_weight
        )
        
        # سطح اطمینان
        confidence = (
            numerology_result.get('confidence', 0.5) * 0.2 +
            historical_analysis.get('confidence', 0.5) * 0.3 +
            news_analysis.get('confidence', 0.5) * 0.3 +
            ai_prediction.get('confidence', 0.5) * 0.2
        )
        
        # تفسیر نهایی
        interpretation = self._generate_event_interpretation(
            category, subcategory, final_score, confidence, info
        )
        
        result = {
            'query': query,
            'category': event_info['name'],
            'subcategory': subcategory.replace('_', ' ').title(),
            'prediction': interpretation['summary'],
            'probability': round(final_score * 100, 1),
            'confidence': round(confidence * 100, 1),
            'confidence_level': self._get_confidence_level(confidence),
            
            'details': {
                'numerology': numerology_result,
                'historical_patterns': historical_analysis,
                'current_news': news_analysis,
                'ai_analysis': {
                    'value': ai_prediction.get('value'),
                    'interpretation': ai_prediction.get('interpretation', '')
                }
            },
            
            'factors': interpretation['factors'],
            'timeline': self._estimate_timeline(info),
            'recommendation': interpretation['recommendation'],
            
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return result
    
    def _analyze_event_numerology(self, query: str, info: Dict) -> Dict[str, Any]:
        """تحلیل عددشناسی رویداد"""
        
        result = {
            'score': 0.5,
            'confidence': 0.5,
            'lucky_numbers': [],
            'unlucky_numbers': [],
            'factors': []
        }
        
        try:
            # عدد تاریخ
            if info.get('year'):
                year_num = self.numerology.reduce_number(info['year'])
                result['year_number'] = year_num
                
                # بررسی سال‌های خوش‌یمن
                lucky_years = [1, 3, 6, 8, 9, 11, 22, 33]
                if year_num in lucky_years:
                    result['factors'].append(f"✨ Year {info['year']} is numerologically favorable")
                    result['score'] += 0.1
            
            # عدد سوال
            query_num = self.numerology.hash_to_number(query)
            result['query_number'] = query_num
            
            # عدد امروز
            today = self.numerology.get_number_of_the_day()
            result['today_number'] = today['universal_number']
            
            # تطابق
            if query_num == today['universal_number']:
                result['factors'].append("⚡ Strong cosmic alignment today")
                result['score'] += 0.15
                result['confidence'] += 0.1
            
            # اعداد شانس
            result['lucky_numbers'] = self.numerology.get_lucky_numbers(query_num, 3)
            result['unlucky_numbers'] = self.numerology.get_unlucky_numbers(query_num, 2)
            
            # نرمال‌سازی
            result['score'] = min(max(result['score'], 0), 1)
            result['confidence'] = min(max(result['confidence'], 0), 1)
            
        except Exception as e:
            logger.error(f"Numerology analysis error: {e}")
        
        return result
    
    def _analyze_historical_patterns(self, category: str, subcategory: str, info: Dict) -> Dict[str, Any]:
        """تحلیل الگوهای تاریخی"""
        
        result = {
            'score': 0.5,
            'confidence': 0.5,
            'patterns': [],
            'similar_events': [],
            'cycle_position': None
        }
        
        try:
            # پیدا کردن رویدادهای مشابه
            if category in self.historical_events:
                events = self.historical_events[category]
                
                # فیلتر بر اساس زیردسته
                if subcategory != 'user_defined':
                    filtered = [e for e in events if e.get('event') == subcategory]
                else:
                    filtered = events
                
                if filtered:
                    # آنالیز الگوها
                    outcomes = []
                    for event in filtered[-10:]:  # 10 رویداد آخر
                        if 'winner' in event:
                            outcomes.append(event['winner'])
                        elif 'severity' in event:
                            outcomes.append(event['severity'])
                    
                    if outcomes:
                        # تشخیص الگو
                        from collections import Counter
                        counter = Counter(outcomes)
                        most_common = counter.most_common(1)
                        
                        if most_common:
                            result['patterns'].append(f"Historical pattern: {most_common[0][0]} appears {most_common[0][1]} times")
                            
                            # امتیاز بر اساس الگو
                            pattern_strength = most_common[0][1] / len(outcomes)
                            result['score'] = pattern_strength
                            result['confidence'] = pattern_strength * 0.7
                    
                    result['similar_events'] = filtered[-3:]  # 3 رویداد آخر
            
            # تشخیص چرخه‌ها
            if info.get('year'):
                # چرخه 4 ساله (انتخابات آمریکا)
                if category == 'politics' and 'election' in subcategory:
                    cycle_pos = (info['year'] - 2020) % 4
                    result['cycle_position'] = cycle_pos
                    
                    if cycle_pos == 0:
                        result['patterns'].append("🔄 This is an election year (4-year cycle)")
                        result['score'] += 0.1
                
                # چرخه 10 ساله (بحران‌های اقتصادی)
                elif category == 'economics':
                    cycle_pos = (info['year'] - 2008) % 10
                    if cycle_pos == 0:
                        result['patterns'].append("⚠️ This year aligns with major economic crisis cycles")
                        result['score'] += 0.15
            
            # نرمال‌سازی
            result['score'] = min(max(result['score'], 0), 1)
            result['confidence'] = min(max(result['confidence'], 0), 1)
            
        except Exception as e:
            logger.error(f"Historical analysis error: {e}")
        
        return result
    
    async def _analyze_current_news(self, query: str, category: str, info: Dict) -> Dict[str, Any]:
        """تحلیل اخبار جاری مرتبط با رویداد"""
        
        result = {
            'sentiment': 0.5,
            'confidence': 0.5,
            'mentions': 0,
            'trending': False,
            'key_phrases': [],
            'articles': []
        }
        
        try:
            # دریافت اخبار از NewsAPI
            async with aiohttp.ClientSession() as session:
                url = f"{self.NEWS_API}/everything"
                params = {
                    'q': query[:100],  # محدودیت طول
                    'apiKey': NEWS_API_KEY,
                    'language': 'en',
                    'sortBy': 'relevancy',
                    'pageSize': 10
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get('articles', [])
                        
                        result['mentions'] = len(articles)
                        
                        # تحلیل احساسات اخبار
                        sentiments = []
                        for article in articles[:5]:
                            title = article.get('title', '')
                            description = article.get('description', '') or ''
                            
                            # تحلیل با AI
                            sentiment = await self._analyze_text_sentiment(f"{title} {description}")
                            sentiments.append(sentiment)
                            
                            result['articles'].append({
                                'title': title[:100],
                                'source': article.get('source', {}).get('name', ''),
                                'url': article.get('url', '')
                            })
                        
                        if sentiments:
                            result['sentiment'] = np.mean(sentiments)
                            result['confidence'] = min(len(sentiments) / 10, 1)
                        
                        # تشخیص روند
                        result['trending'] = result['mentions'] > 5
                        
                        # استخراج کلمات کلیدی
                        all_text = ' '.join([a['title'] for a in result['articles']])
                        result['key_phrases'] = self._extract_key_phrases(all_text)[:5]
        
        except Exception as e:
            logger.error(f"News analysis error: {e}")
        
        return result
    
    async def _analyze_text_sentiment(self, text: str) -> float:
        """تحلیل احساسات متن"""
        # استفاده از AI برای تحلیل
        result = await self.ai.analyze_sentiment(text)
        return result.get('normalized', 0.5)
    
    def _extract_key_phrases(self, text: str, max_phrases: int = 5) -> List[str]:
        """استخراج عبارات کلیدی از متن"""
        # الگوریتم ساده - می‌تونه با RAKE یا KeyBERT بهتر بشه
        words = text.lower().split()
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        # حذف کلمات تکراری
        phrases = []
        for i in range(len(words)-1):
            if words[i] not in stopwords and words[i+1] not in stopwords:
                phrases.append(f"{words[i]} {words[i+1]}")
        
        from collections import Counter
        counter = Counter(phrases)
        return [p for p, _ in counter.most_common(max_phrases)]
    
    def _generate_event_interpretation(self, category: str, subcategory: str, 
                                      score: float, confidence: float, info: Dict) -> Dict[str, Any]:
        """تولید تفسیر نهایی رویداد"""
        
        # خلاصه پیش‌بینی
        if score >= 0.8:
            summary = f"🔮 Very high probability of this event occurring"
            if info.get('year'):
                summary += f" in {info['year']}"
        elif score >= 0.7:
            summary = f"✨ High probability"
        elif score >= 0.6:
            summary = f"📊 Moderate probability"
        elif score >= 0.5:
            summary = f"⚖️ Balanced - too close to call"
        elif score >= 0.4:
            summary = f"⚠️ Low probability"
        else:
            summary = f"❌ Very low probability"
        
        # عوامل موثر
        factors = []
        
        if info.get('year'):
            factors.append(f"📅 Year {info['year']} analysis")
        
        if info.get('location'):
            factors.append(f"📍 Location: {info['location']}")
        
        factors.append(f"🔢 Numerological alignment: {self._get_alignment_text(score)}")
        factors.append(f"📈 Historical patterns: {self._get_pattern_text(score)}")
        factors.append(f"📰 Current sentiment: {self._get_sentiment_text(score)}")
        
        # توصیه
        if confidence >= 0.7 and score >= 0.7:
            recommendation = "✅ High confidence - Consider acting on this prediction"
        elif confidence >= 0.5 and score >= 0.6:
            recommendation = "📊 Moderate confidence - Monitor closely"
        elif confidence >= 0.5 and score <= 0.4:
            recommendation = "🛑 Low probability - Consider alternatives"
        else:
            recommendation = "🤔 Uncertainty high - Wait for clearer signals"
        
        return {
            'summary': summary,
            'factors': factors,
            'recommendation': recommendation
        }
    
    def _get_alignment_text(self, score: float) -> str:
        if score >= 0.7:
            return "Strong alignment"
        elif score >= 0.5:
            return "Moderate alignment"
        else:
            return "Weak alignment"
    
    def _get_pattern_text(self, score: float) -> str:
        if score >= 0.7:
            return "Strong historical patterns"
        elif score >= 0.5:
            return "Some historical precedents"
        else:
            return "No clear patterns"
    
    def _get_sentiment_text(self, score: float) -> str:
        if score >= 0.7:
            return "Very positive"
        elif score >= 0.6:
            return "Positive"
        elif score >= 0.45:
            return "Neutral"
        elif score >= 0.3:
            return "Negative"
        else:
            return "Very negative"
    
    def _get_confidence_level(self, confidence: float) -> str:
        if confidence >= 0.9:
            return "🔮 Absolute Certainty"
        elif confidence >= 0.8:
            return "✨ Very High"
        elif confidence >= 0.7:
            return "⭐ High"
        elif confidence >= 0.6:
            return "📊 Moderate"
        elif confidence >= 0.5:
            return "📈 Slight Edge"
        else:
            return "⚠️ Low"
    
    def _estimate_timeline(self, info: Dict) -> Dict[str, Any]:
        """تخمین زمان وقوع رویداد"""
        
        if info.get('year'):
            # رویداد با سال مشخص
            year = info['year']
            now = datetime.now()
            
            if year > now.year:
                return {
                    'type': 'future',
                    'date': f"{year}",
                    'days_until': (datetime(year, 1, 1) - now).days,
                    'confidence': 'high'
                }
            elif year == now.year:
                return {
                    'type': 'current_year',
                    'date': 'This year',
                    'confidence': 'high'
                }
            else:
                return {
                    'type': 'past',
                    'date': f"{year}",
                    'confidence': 'historical'
                }
        else:
            # رویداد بدون سال مشخص
            today = self.numerology.get_number_of_the_day()
            
            if today['universal_number'] in [1, 3, 6, 8, 9]:
                return {
                    'type': 'imminent',
                    'estimate': 'Next 1-7 days',
                    'confidence': 'medium'
                }
            else:
                return {
                    'type': 'unknown',
                    'estimate': 'Timing uncertain - monitor daily',
                    'confidence': 'low'
                }
    
    # ==================== پیش‌بینی‌های خاص ====================
    
    async def predict_election(self, country: str, year: int, candidates: List[str] = None) -> Dict[str, Any]:
        """پیش‌بینی نتیجه انتخابات"""
        
        query = f"{country} election {year}"
        if candidates:
            query += f" between {' and '.join(candidates)}"
        
        return await self.predict_event(query)
    
    async def predict_earthquake(self, location: str, timeframe: str = '30d') -> Dict[str, Any]:
        """پیش‌بینی زلزله"""
        
        query = f"earthquake in {location} within {timeframe}"
        return await self.predict_event(query)
    
    async def predict_market_crash(self, market: str = 'US', timeframe: str = '1y') -> Dict[str, Any]:
        """پیش‌بینی سقوط بازار"""
        
        query = f"stock market crash in {market} within {timeframe}"
        return await self.predict_event(query)
    
    async def predict_oscars(self, category: str = 'Best Picture', year: int = None) -> Dict[str, Any]:
        """پیش‌بینی برنده اسکار"""
        
        if not year:
            year = datetime.now().year + 1
        
        query = f"oscars {year} winner for {category}"
        return await self.predict_event(query)
    
    async def predict_weather_disaster(self, disaster_type: str, location: str = None) -> Dict[str, Any]:
        """پیش‌بینی بلایای طبیعی"""
        
        query = f"{disaster_type} in {location if location else 'world'} next month"
        return await self.predict_event(query)
    
    # ==================== تحلیل روند ====================
    
    async def analyze_trend(self, topic: str, days: int = 30) -> Dict[str, Any]:
        """تحلیل روند یک موضوع در بازه زمانی"""
        
        # دریافت اخبار
        news = await self._analyze_current_news(topic, 'custom', {'year': datetime.now().year})
        
        # تحلیل عددشناسی
        topic_number = self.numerology.hash_to_number(topic)
        
        # پیش‌بینی آینده
        future_query = f"future of {topic} next {days} days"
        prediction = await self.predict_event(future_query)
        
        return {
            'topic': topic,
            'current_sentiment': news['sentiment'],
            'mentions': news['mentions'],
            'trending': news['trending'],
            'topic_number': topic_number,
            'numerology': self.numerology.get_quick_interpretation(topic_number),
            'prediction': prediction,
            'key_phrases': news['key_phrases']
        }
    
    # ==================== ابزارها ====================
    
    def get_category_emoji(self, category: str) -> str:
        """دریافت ایموجی دسته‌بندی"""
        emojis = {
            'politics': '🗳️',
            'economics': '📊',
            'weather': '🌤️',
            'entertainment': '🎬',
            'technology': '💻',
            'sports': '🏆',
            'health': '🏥',
            'social': '👥',
            'custom': '✨'
        }
        return emojis.get(category, '🌍')
    
    def get_stats(self) -> Dict[str, Any]:
        """گرفتن آمار"""
        return {
            'categories': len(self.EVENT_CATEGORIES),
            'historical_events': sum(len(v) for v in self.historical_events.values()),
            'cache_size': len(self.cache)
        }
