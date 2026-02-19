# sports_analyzer/sports_predictor.py
"""
پیش‌بینی‌کننده نهایی مسابقات ورزشی
پشتیبانی از: فوتبال، بسکتبال، تنیس، والیبال، هندبال، فوتبال آمریکایی، بیسبال، هاکی، بوکس، MMA
با استفاده از:
- عددشناسی نام تیم‌ها و بازیکنان
- آمار تاریخی
- فرم اخیر
- شرایط مسابقه
- هوش مصنوعی
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

# Machine Learning
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import joblib

# Local
from core.numerology_engine import NumerologyEngine
from ai.genius_ai import GeniusAI
from config import *

logger = logging.getLogger(__name__)

class SportsPredictor:
    """
    پیش‌بینی‌کننده مسابقات ورزشی با پشتیبانی از ۱۰+ رشته ورزشی
    """
    
    # ==================== لیست رشته‌های ورزشی ====================
    
    SPORTS = {
        'football': {
            'name': '⚽ Football',
            'leagues': ['UCL', 'Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1', 'World Cup', 'Euro'],
            'teams': True,
            'players': True,
            'numerology_impact': 0.3,
            'stats_impact': 0.7
        },
        'basketball': {
            'name': '🏀 Basketball',
            'leagues': ['NBA', 'EuroLeague', 'World Cup', 'Olympics'],
            'teams': True,
            'players': True,
            'numerology_impact': 0.25,
            'stats_impact': 0.75
        },
        'tennis': {
            'name': '🎾 Tennis',
            'leagues': ['Grand Slam', 'ATP', 'WTA', 'Davis Cup'],
            'teams': False,
            'players': True,
            'numerology_impact': 0.35,
            'stats_impact': 0.65
        },
        'volleyball': {
            'name': '🏐 Volleyball',
            'leagues': ['World Cup', 'Olympics', 'Champions League'],
            'teams': True,
            'players': True,
            'numerology_impact': 0.3,
            'stats_impact': 0.7
        },
        'handball': {
            'name': '🤾 Handball',
            'leagues': ['World Cup', 'Euro', 'Champions League'],
            'teams': True,
            'players': True,
            'numerology_impact': 0.3,
            'stats_impact': 0.7
        },
        'american_football': {
            'name': '🏈 American Football',
            'leagues': ['NFL', 'Super Bowl', 'College Football'],
            'teams': True,
            'players': True,
            'numerology_impact': 0.25,
            'stats_impact': 0.75
        },
        'baseball': {
            'name': '⚾ Baseball',
            'leagues': ['MLB', 'World Series', 'Japan League'],
            'teams': True,
            'players': True,
            'numerology_impact': 0.25,
            'stats_impact': 0.75
        },
        'hockey': {
            'name': '🏒 Hockey',
            'leagues': ['NHL', 'World Cup', 'Olympics'],
            'teams': True,
            'players': True,
            'numerology_impact': 0.3,
            'stats_impact': 0.7
        },
        'boxing': {
            'name': '🥊 Boxing',
            'leagues': ['Heavyweight', 'Lightweight', 'Olympics'],
            'teams': False,
            'players': True,
            'numerology_impact': 0.4,
            'stats_impact': 0.6
        },
        'mma': {
            'name': '🥋 MMA',
            'leagues': ['UFC', 'Bellator', 'ONE Championship'],
            'teams': False,
            'players': True,
            'numerology_impact': 0.4,
            'stats_impact': 0.6
        },
        'formula1': {
            'name': '🏎️ Formula 1',
            'leagues': ['F1', 'Grand Prix'],
            'teams': True,
            'players': True,
            'numerology_impact': 0.2,
            'stats_impact': 0.8
        },
        'cycling': {
            'name': '🚴 Cycling',
            'leagues': ['Tour de France', 'Giro', 'Vuelta'],
            'teams': True,
            'players': True,
            'numerology_impact': 0.25,
            'stats_impact': 0.75
        },
        'swimming': {
            'name': '🏊 Swimming',
            'leagues': ['Olympics', 'World Cup'],
            'teams': False,
            'players': True,
            'numerology_impact': 0.3,
            'stats_impact': 0.7
        },
        'athletics': {
            'name': '🏃 Athletics',
            'leagues': ['Olympics', 'World Cup'],
            'teams': False,
            'players': True,
            'numerology_impact': 0.3,
            'stats_impact': 0.7
        },
        'esports': {
            'name': '🎮 Esports',
            'leagues': ['LoL World Cup', 'Dota 2 International', 'CS:GO Major'],
            'teams': True,
            'players': True,
            'numerology_impact': 0.35,
            'stats_impact': 0.65
        }
    }
    
    # ==================== APIهای ورزشی ====================
    
    # Football API (رایگان)
    FOOTBALL_API = "https://www.thesportsdb.com/api/v1/json/3"
    
    # Basketball API
    BASKETBALL_API = "https://www.balldontlie.io/api/v1"
    
    # عمومی
    SPORTS_API = "https://www.thesportsdb.com/api/v1/json/3"
    
    def __init__(self, db_session=None, numerology=None, ai=None):
        self.db = db_session
        self.numerology = numerology or NumerologyEngine(db_session)
        self.ai = ai or GeniusAI(db_session, self.numerology)
        
        # مدل‌های ML
        self.models = {}
        self.scalers = {}
        
        # کش
        self.cache = {}
        self.cache_timeout = 3600  # 1 ساعت
        
        # آمار تیم‌ها و بازیکنان
        self.team_stats = {}
        self.player_stats = {}
        self.h2h_records = {}
        
        # بارگذاری مدل‌ها
        self.load_models()
        
        logger.info("⚽ SportsPredictor initialized with 15+ sports")
    
    def load_models(self):
        """بارگذاری مدل‌های آموزش دیده"""
        try:
            model_files = {
                'football': 'models/football_model.pkl',
                'basketball': 'models/basketball_model.pkl',
                'tennis': 'models/tennis_model.pkl'
            }
            
            for sport, path in model_files.items():
                try:
                    self.models[sport] = joblib.load(path)
                    logger.info(f"✅ Loaded model for {sport}")
                except:
                    self.models[sport] = self._create_default_model()
                    
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def _create_default_model(self):
        """ایجاد مدل پیش‌فرض"""
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
    
    # ==================== تشخیص ورزش ====================
    
    def detect_sport(self, query: str) -> Tuple[str, Dict]:
        """
        تشخیص خودکار رشته ورزشی از متن کاربر
        
        Args:
            query: متن کاربر (مثلاً "Man United vs Liverpool")
        
        Returns:
            (sport_type, extracted_info)
        """
        
        query_lower = query.lower()
        
        # تشخیص لیگ‌ها
        for sport, info in self.SPORTS.items():
            for league in info['leagues']:
                if league.lower() in query_lower:
                    return sport, {'league': league, 'sport': sport}
        
        # تشخیص بر اساس کلمات کلیدی
        keywords = {
            'football': ['football', 'soccer', 'premier league', 'ucl', 'champions league', 'world cup'],
            'basketball': ['basketball', 'nba', 'euroleague', 'lebron', 'jordan'],
            'tennis': ['tennis', 'grand slam', 'wimbledon', 'us open', 'federer', 'nadal', 'djokovic'],
            'boxing': ['boxing', 'heavyweight', 'tyson', 'ali', 'mayweather'],
            'mma': ['mma', 'ufc', 'mcgregor', 'khabib', 'jones'],
            'formula1': ['f1', 'formula 1', 'grand prix', 'hamilton', 'verstappen'],
            'baseball': ['baseball', 'mlb', 'world series'],
            'hockey': ['hockey', 'nhl', 'stanley cup'],
            'american_football': ['nfl', 'super bowl', 'football', 'patriots', 'chiefs'],
            'esports': ['esports', 'league of legends', 'dota', 'csgo', 'valorant']
        }
        
        for sport, words in keywords.items():
            if any(word in query_lower for word in words):
                return sport, {'detected_by': 'keywords'}
        
        # پیش‌فرض: فوتبال
        return 'football', {'detected_by': 'default'}
    
    # ==================== استخراج اطلاعات ====================
    
    def extract_match_info(self, query: str) -> Dict[str, Any]:
        """
        استخراج اطلاعات مسابقه از متن کاربر
        
        Args:
            query: متن کاربر (مثال: "Man United vs Liverpool tomorrow")
        
        Returns:
            اطلاعات استخراج شده
        """
        
        result = {
            'team1': None,
            'team2': None,
            'date': None,
            'time': None,
            'league': None,
            'sport': None
        }
        
        # تشخیص "vs" یا "against"
        vs_patterns = [r'(.+?)\s+(?:vs|VS|against|AGAINST|vs\.|VS\.)\s+(.+)']
        
        for pattern in vs_patterns:
            match = re.search(pattern, query)
            if match:
                result['team1'] = match.group(1).strip()
                result['team2'] = match.group(2).strip()
                
                # حذف کلمات اضافه از انتهای تیم دوم
                result['team2'] = re.sub(r'\s+(?:tomorrow|today|at|on|in|at\s+\d+:\d+).*$', '', result['team2'])
                break
        
        # تشخیص تاریخ
        date_keywords = {
            'today': datetime.now(),
            'tomorrow': datetime.now() + timedelta(days=1),
            'next week': datetime.now() + timedelta(days=7)
        }
        
        for keyword, date in date_keywords.items():
            if keyword in query.lower():
                result['date'] = date.strftime('%Y-%m-%d')
                break
        
        # تشخیص ساعت
        time_pattern = r'(\d{1,2}):(\d{2})\s*(?:am|pm)?'
        time_match = re.search(time_pattern, query)
        if time_match:
            result['time'] = f"{time_match.group(1)}:{time_match.group(2)}"
        
        # تشخیص ورزش
        sport, sport_info = self.detect_sport(query)
        result['sport'] = sport
        
        return result
    
    # ==================== دریافت داده‌های تیم ====================
    
    async def get_team_data(self, team_name: str, sport: str) -> Dict[str, Any]:
        """
        دریافت اطلاعات تیم از API
        """
        
        cache_key = f"team_{sport}_{team_name}"
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if time.time() - cached_time < self.cache_timeout:
                return cached_data
        
        result = {
            'name': team_name,
            'sport': sport,
            'form': [],
            'last_5': [],
            'home_advantage': 0.1,
            'injuries': [],
            'suspensions': [],
            'key_players': [],
            'ranking': None,
            'points': 0,
            'goals_for': 0,
            'goals_against': 0,
            'wins': 0,
            'draws': 0,
            'losses': 0
        }
        
        try:
            # جستجوی تیم در API
            async with aiohttp.ClientSession() as session:
                url = f"{self.SPORTS_API}/searchteams.php"
                params = {'t': team_name}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and 'teams' in data and data['teams']:
                            team = data['teams'][0]
                            
                            # استخراج اطلاعات
                            result['id'] = team.get('idTeam')
                            result['league'] = team.get('strLeague')
                            result['stadium'] = team.get('strStadium')
                            result['capacity'] = team.get('intStadiumCapacity')
                            result['formed_year'] = team.get('intFormedYear')
                            result['badge'] = team.get('strTeamBadge')
                            
                            # عددشناسی نام تیم
                            numerology = self.numerology.calculate_name_number(team_name)
                            result['numerology'] = numerology
                            result['team_number'] = numerology.get('expression', 5)
            
            # دریافت فرم اخیر
            await self._get_team_form(result, sport)
            
            # دریافت آمار مقابل حریف خاص (بعداً در H2H)
            
            self.cache[cache_key] = (time.time(), result)
            
        except Exception as e:
            logger.error(f"Error getting team data for {team_name}: {e}")
        
        return result
    
    async def _get_team_form(self, team_data: Dict, sport: str):
        """دریافت فرم اخیر تیم"""
        
        # TODO: دریافت از API واقعی
        # فعلاً داده‌های نمونه
        import random
        
        last_5 = []
        for i in range(5):
            result = random.choice(['W', 'W', 'D', 'L', 'L'])
            last_5.append(result)
            if result == 'W':
                team_data['wins'] += 1
            elif result == 'D':
                team_data['draws'] += 1
            else:
                team_data['losses'] += 1
            
            team_data['goals_for'] += random.randint(0, 3)
            team_data['goals_against'] += random.randint(0, 2)
        
        team_data['last_5'] = last_5
        team_data['form'] = last_5
        
        # محاسبه امتیاز فرم
        form_score = 0
        for result in last_5:
            if result == 'W':
                form_score += 3
            elif result == 'D':
                form_score += 1
        
        team_data['form_score'] = form_score
        
        # بازیکنان کلیدی
        team_data['key_players'] = self._get_key_players(team_data['name'], sport)
    
    def _get_key_players(self, team_name: str, sport: str) -> List[Dict]:
        """بازیکنان کلیدی تیم"""
        # TODO: دریافت از API
        return [
            {'name': 'Key Player 1', 'position': 'Forward', 'goals': 10},
            {'name': 'Key Player 2', 'position': 'Midfielder', 'assists': 5}
        ]
    
    # ==================== دریافت داده‌های بازیکن ====================
    
    async def get_player_data(self, player_name: str, sport: str) -> Dict[str, Any]:
        """دریافت اطلاعات بازیکن"""
        
        result = {
            'name': player_name,
            'sport': sport,
            'age': None,
            'nationality': None,
            'position': None,
            'team': None,
            'goals': 0,
            'assists': 0,
            'form': []
        }
        
        try:
            # جستجوی بازیکن در API
            async with aiohttp.ClientSession() as session:
                url = f"{self.SPORTS_API}/searchplayers.php"
                params = {'p': player_name}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and 'player' in data and data['player']:
                            player = data['player'][0]
                            
                            result['id'] = player.get('idPlayer')
                            result['team'] = player.get('strTeam')
                            result['nationality'] = player.get('strNationality')
                            result['position'] = player.get('strPosition')
                            result['age'] = player.get('dateBorn')
                            
                            # عددشناسی نام
                            numerology = self.numerology.calculate_name_number(player_name)
                            result['numerology'] = numerology
                            result['player_number'] = numerology.get('expression', 5)
                            
        except Exception as e:
            logger.error(f"Error getting player data: {e}")
        
        return result
    
    # ==================== پیش‌بینی مسابقه ====================
    
    async def predict_match(self, query: str) -> Dict[str, Any]:
        """
        پیش‌بینی نتیجه مسابقه
        
        Args:
            query: متن کاربر (مثال: "Man United vs Liverpool tomorrow")
        
        Returns:
            پیش‌بینی کامل
        """
        
        # استخراج اطلاعات
        match_info = self.extract_match_info(query)
        
        sport = match_info['sport']
        team1 = match_info['team1']
        team2 = match_info['team2']
        
        if not team1 or not team2:
            return {
                'error': 'Could not identify teams. Please use format: Team1 vs Team2',
                'example': 'Man United vs Liverpool'
            }
        
        logger.info(f"⚽ Predicting: {team1} vs {team2} ({sport})")
        
        # دریافت اطلاعات تیم‌ها
        team1_data = await self.get_team_data(team1, sport)
        team2_data = await self.get_team_data(team2, sport)
        
        # دریافت تاریخچه رویارویی
        h2h = await self.get_h2h(team1, team2, sport)
        
        # ==================== تحلیل عددشناسی ====================
        
        # عدد تیم‌ها
        num1 = team1_data.get('team_number', 5)
        num2 = team2_data.get('team_number', 5)
        
        # تطابق عددی
        compatibility = self.numerology.analyze_number_compatibility(num1, num2)
        
        # عدد روز مسابقه
        if match_info.get('date'):
            day_num = self.numerology.calculate_life_path(match_info['date'])
            day_number = day_num['primary_number']
        else:
            day_number = self.numerology.get_number_of_the_day()['universal_number']
        
        # تاثیر عددشناسی
        if num1 == day_number:
            num_advantage1 = 0.2
        elif abs(num1 - day_number) == 1:
            num_advantage1 = 0.1
        else:
            num_advantage1 = 0
        
        if num2 == day_number:
            num_advantage2 = 0.2
        elif abs(num2 - day_number) == 1:
            num_advantage2 = 0.1
        else:
            num_advantage2 = 0
        
        numerology_score1 = 0.5 + num_advantage1
        numerology_score2 = 0.5 + num_advantage2
        
        # ==================== تحلیل آماری ====================
        
        # فرم اخیر
        form_score1 = team1_data.get('form_score', 0) / 15  # نرمال‌سازی
        form_score2 = team2_data.get('form_score', 0) / 15
        
        # قدرت گلزنی
        attacking1 = team1_data.get('goals_for', 10) / max(team1_data.get('goals_for', 10) + team1_data.get('goals_against', 10), 1)
        attacking2 = team2_data.get('goals_for', 10) / max(team2_data.get('goals_for', 10) + team2_data.get('goals_against', 10), 1)
        
        # دفاع
        defending1 = 1 - (team1_data.get('goals_against', 5) / max(team1_data.get('goals_for', 10), 1))
        defending2 = 1 - (team2_data.get('goals_against', 5) / max(team2_data.get('goals_for', 10), 1))
        
        # تاریخچه رویارویی
        h2h_advantage = 0
        if h2h:
            total_matches = len(h2h.get('matches', []))
            if total_matches > 0:
                team1_wins = h2h.get('team1_wins', 0)
                h2h_advantage = (team1_wins / total_matches) - 0.5
        
        # امتیاز آماری نهایی
        stats_score1 = (form_score1 * 0.3 + attacking1 * 0.3 + defending1 * 0.2 + 0.5 + h2h_advantage * 0.2)
        stats_score2 = (form_score2 * 0.3 + attacking2 * 0.3 + defending2 * 0.2 + 0.5 - h2h_advantage * 0.2)
        
        # ==================== پیش‌بینی با AI ====================
        
        ai_input = {
            'sport': sport,
            'team1': team1,
            'team2': team2,
            'team1_number': num1,
            'team2_number': num2,
            'day_number': day_number,
            'form_score1': form_score1,
            'form_score2': form_score2,
            'attacking1': attacking1,
            'attacking2': attacking2,
            'defending1': defending1,
            'defending2': defending2,
            'h2h_advantage': h2h_advantage
        }
        
        ai_prediction = await self.ai.predict(ai_input, 'sports')
        ai_score = ai_prediction.get('value', 0.5)
        
        # ==================== ترکیب نتایج ====================
        
        # وزن‌دهی بر اساس sport
        sport_info = self.SPORTS.get(sport, self.SPORTS['football'])
        num_weight = sport_info['numerology_impact']
        stats_weight = sport_info['stats_impact']
        ai_weight = 0.2  # وزن AI
        
        # تنظیم مجدد وزن‌ها
        total_weight = num_weight + stats_weight + ai_weight
        num_weight = num_weight / total_weight
        stats_weight = stats_weight / total_weight
        ai_weight = ai_weight / total_weight
        
        team1_score = (numerology_score1 * num_weight + 
                      stats_score1 * stats_weight + 
                      ai_score * ai_weight)
        
        team2_score = (numerology_score2 * num_weight + 
                      stats_score2 * stats_weight + 
                      (1 - ai_score) * ai_weight)
        
        # نرمال‌سازی
        total = team1_score + team2_score
        team1_prob = team1_score / total
        team2_prob = team2_score / total
        draw_prob = 1 - (team1_prob + team2_prob)
        
        # اطمینان
        confidence = ai_prediction.get('confidence', 0.5) * 0.7 + abs(team1_prob - team2_prob) * 0.3
        
        # پیش‌بینی نتیجه
        if team1_prob > team2_prob + 0.1:
            winner = team1
            result_text = f"🏆 **{team1} wins**"
            if team1_prob > 0.6:
                result_text += " (High confidence)"
        elif team2_prob > team1_prob + 0.1:
            winner = team2
            result_text = f"🏆 **{team2} wins**"
            if team2_prob > 0.6:
                result_text += " (High confidence)"
        else:
            winner = "Draw"
            result_text = "🤝 **Draw**"
        
        # پیش‌بینی نتیجه دقیق
        score_prediction = self._predict_score(team1_data, team2_data, team1_prob, team2_prob)
        
        # ==================== نتیجه نهایی ====================
        
        result = {
            'match': f"{team1} vs {team2}",
            'sport': sport_info['name'],
            'date': match_info.get('date', 'Not specified'),
            'time': match_info.get('time', 'Not specified'),
            
            'prediction': {
                'winner': winner,
                'result': result_text,
                'score': score_prediction,
                'team1_prob': round(team1_prob * 100, 1),
                'team2_prob': round(team2_prob * 100, 1),
                'draw_prob': round(draw_prob * 100, 1),
                'confidence': round(confidence * 100, 1)
            },
            
            'numerology': {
                'team1_number': num1,
                'team2_number': num2,
                'day_number': day_number,
                'compatibility': compatibility,
                'team1_advantage': round(num_advantage1 * 100, 1),
                'team2_advantage': round(num_advantage2 * 100, 1)
            },
            
            'statistics': {
                'team1': {
                    'form': team1_data.get('last_5', []),
                    'form_score': round(form_score1 * 100, 1),
                    'attacking': round(attacking1 * 100, 1),
                    'defending': round(defending1 * 100, 1)
                },
                'team2': {
                    'form': team2_data.get('last_5', []),
                    'form_score': round(form_score2 * 100, 1),
                    'attacking': round(attacking2 * 100, 1),
                    'defending': round(defending2 * 100, 1)
                },
                'h2h': h2h
            },
            
            'ai_analysis': {
                'confidence': ai_prediction.get('confidence', 0.5),
                'interpretation': ai_prediction.get('interpretation', ''),
                'factors': ai_prediction.get('ensemble_details', {})
            },
            
            'recommendation': self._get_betting_recommendation(team1_prob, team2_prob, confidence),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return result
    
    async def get_h2h(self, team1: str, team2: str, sport: str) -> Dict[str, Any]:
        """دریافت تاریخچه رویارویی دو تیم"""
        
        cache_key = f"h2h_{sport}_{team1}_{team2}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = {
            'team1': team1,
            'team2': team2,
            'matches': [],
            'team1_wins': 0,
            'team2_wins': 0,
            'draws': 0,
            'team1_goals': 0,
            'team2_goals': 0
        }
        
        try:
            # TODO: دریافت از API واقعی
            # فعلاً داده‌های نمونه
            import random
            
            num_matches = random.randint(3, 10)
            for i in range(num_matches):
                if random.random() > 0.6:
                    winner = team1
                    result['team1_wins'] += 1
                elif random.random() > 0.3:
                    winner = team2
                    result['team2_wins'] += 1
                else:
                    winner = 'Draw'
                    result['draws'] += 1
                
                goals1 = random.randint(0, 4)
                goals2 = random.randint(0, 4)
                result['team1_goals'] += goals1
                result['team2_goals'] += goals2
                
                result['matches'].append({
                    'date': f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                    'score': f"{goals1}-{goals2}",
                    'winner': winner
                })
            
            self.cache[cache_key] = result
            
        except Exception as e:
            logger.error(f"Error getting H2H: {e}")
        
        return result
    
    def _predict_score(self, team1_data: Dict, team2_data: Dict, prob1: float, prob2: float) -> str:
        """پیش‌بینی نتیجه دقیق"""
        
        # میانگین گل‌های زده
        avg_goals1 = team1_data.get('goals_for', 10) / max(team1_data.get('wins', 1), 1)
        avg_goals2 = team2_data.get('goals_for', 10) / max(team2_data.get('wins', 1), 1)
        
        # تعدیل با احتمال
        expected1 = round(avg_goals1 * prob1)
        expected2 = round(avg_goals2 * prob2)
        
        # اطمینان از منطقی بودن
        expected1 = max(0, min(expected1, 5))
        expected2 = max(0, min(expected2, 5))
        
        return f"{expected1}-{expected2}"
    
    def _get_betting_recommendation(self, prob1: float, prob2: float, confidence: float) -> str:
        """توصیه شرط‌بندی"""
        
        if confidence < 0.4:
            return "⚠️ Low confidence - Not recommended for betting"
        
        if prob1 > 0.6:
            return f"🎯 Strong recommendation: Bet on Team 1 (Win probability: {prob1*100:.1f}%)"
        elif prob2 > 0.6:
            return f"🎯 Strong recommendation: Bet on Team 2 (Win probability: {prob2*100:.1f}%)"
        elif prob1 > 0.55:
            return f"📊 Moderate recommendation: Team 1 has slight edge ({prob1*100:.1f}%)"
        elif prob2 > 0.55:
            return f"📊 Moderate recommendation: Team 2 has slight edge ({prob2*100:.1f}%)"
        else:
            return "🤔 Too close to call - Consider betting on Draw or Over/Under markets"
    
    # ==================== پیش‌بینی تورنمنت ====================
    
    async def predict_tournament(self, tournament: str, sport: str = None) -> Dict[str, Any]:
        """پیش‌بینی قهرمان تورنمنت"""
        
        if not sport:
            sport, _ = self.detect_sport(tournament)
        
        # TODO: دریافت لیست تیم‌ها از API
        # تحلیل هر تیم و پیش‌بینی
        
        return {
            'tournament': tournament,
            'sport': sport,
            'predictions': [],
            'champion': None,
            'confidence': 0
        }
    
    # ==================== پیش‌بینی زنده ====================
    
    async def live_prediction(self, match_id: str) -> Dict[str, Any]:
        """پیش‌بینی لحظه‌ای در جریان بازی"""
        
        # TODO: دریافت اطلاعات زنده
        # تحلیل لحظه‌ای بر اساس جریان بازی
        
        return {
            'match_id': match_id,
            'current_score': '0-0',
            'minute': 0,
            'prediction': {},
            'live_analysis': {}
        }
    
    # ==================== ابزارها ====================
    
    def get_sport_emoji(self, sport: str) -> str:
        """دریافت ایموجی ورزش"""
        emojis = {
            'football': '⚽',
            'basketball': '🏀',
            'tennis': '🎾',
            'volleyball': '🏐',
            'handball': '🤾',
            'american_football': '🏈',
            'baseball': '⚾',
            'hockey': '🏒',
            'boxing': '🥊',
            'mma': '🥋',
            'formula1': '🏎️',
            'cycling': '🚴',
            'swimming': '🏊',
            'athletics': '🏃',
            'esports': '🎮'
        }
        return emojis.get(sport, '⚽')
    
    def get_league_info(self, league: str) -> Dict:
        """اطلاعات لیگ"""
        leagues = {
            'UCL': {'name': 'UEFA Champions League', 'teams': 32, 'country': 'Europe'},
            'Premier League': {'name': 'English Premier League', 'teams': 20, 'country': 'England'},
            'La Liga': {'name': 'Spanish La Liga', 'teams': 20, 'country': 'Spain'},
            'NBA': {'name': 'National Basketball Association', 'teams': 30, 'country': 'USA'},
            'World Cup': {'name': 'FIFA World Cup', 'teams': 32, 'country': 'International'}
        }
        return leagues.get(league, {})
