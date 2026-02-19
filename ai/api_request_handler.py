# ai/api_request_handler.py
"""
مدیریت درخواست API از کاربر
- تشخیص نیاز به API
- درخواست API key از کاربر
- اعتبارسنجی API key
- ذخیره موقت برای آن درخواست
- پشتیبانی از APIهای مختلف
"""

import re
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class APIType(Enum):
    """انواع APIهای پشتیبانی شده"""
    COINGECKO = "coingecko"
    ETHERSCAN = "etherscan"
    BSCSCAN = "bscscan"
    NEWSAPI = "newsapi"
    TWITTER = "twitter"
    REDDIT = "reddit"
    WEATHER = "openweathermap"
    FOOTBALL = "football_data"
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    CUSTOM = "custom"

class APIRequestHandler:
    """
    مدیریت درخواست API key از کاربر
    """
    
    # تعریف APIهای مورد نیاز برای هر نوع درخواست
    API_REQUIREMENTS = {
        'crypto_address': {
            'description': '🔍 To analyze this token in depth, I need:',
            'apis': [
                {
                    'type': APIType.ETHERSCAN,
                    'name': 'Etherscan API Key',
                    'url': 'https://etherscan.io/register',
                    'description': 'For detailed token information and transactions',
                    'required_for': ['ethereum', 'bsc', 'polygon']
                },
                {
                    'type': APIType.COINGECKO,
                    'name': 'CoinGecko API Key',
                    'url': 'https://www.coingecko.com/en/api',
                    'description': 'For market data and price history',
                    'optional': True
                }
            ]
        },
        'sports_match': {
            'description': '⚽ For accurate sports predictions, I need:',
            'apis': [
                {
                    'type': APIType.FOOTBALL,
                    'name': 'Football-Data.org API Key',
                    'url': 'https://www.football-data.org/client/register',
                    'description': 'For live scores and team statistics',
                    'required_for': ['football']
                }
            ]
        },
        'event_prediction': {
            'description': '🌍 For precise event predictions, I need:',
            'apis': [
                {
                    'type': APIType.NEWSAPI,
                    'name': 'NewsAPI Key',
                    'url': 'https://newsapi.org/register',
                    'description': 'For real-time news analysis',
                    'optional': False
                }
            ]
        },
        'weather_prediction': {
            'description': '🌤️ For accurate weather predictions, I need:',
            'apis': [
                {
                    'type': APIType.WEATHER,
                    'name': 'OpenWeatherMap API Key',
                    'url': 'https://openweathermap.org/api',
                    'description': 'For current weather data',
                    'optional': False
                }
            ]
        }
    }
    
    def __init__(self):
        # کش موقت API keyهای دریافتی (فقط برای session فعلی)
        self.temp_api_keys = {}
        
        # تاریخچه درخواست‌ها
        self.request_history = []
    
    def detect_required_apis(self, query: str, query_type: str) -> List[Dict]:
        """
        تشخیص APIهای مورد نیاز برای یک query
        
        Args:
            query: متن سوال کاربر
            query_type: نوع درخواست (crypto_address, sports_match, etc)
        
        Returns:
            لیست APIهای مورد نیاز
        """
        
        if query_type in self.API_REQUIREMENTS:
            return self.API_REQUIREMENTS[query_type]['apis']
        
        # تشخیص خودکار بر اساس محتوای query
        required_apis = []
        
        # تشخیص نیاز به Crypto API
        if any(addr in query for addr in ['0x', 'token', 'coin', 'crypto']):
            required_apis.extend(self.API_REQUIREMENTS['crypto_address']['apis'])
        
        # تشخیص نیاز به Sports API
        sports_keywords = ['vs', 'match', 'game', 'football', 'soccer', 'basketball', 'tennis']
        if any(kw in query.lower() for kw in sports_keywords):
            required_apis.extend(self.API_REQUIREMENTS['sports_match']['apis'])
        
        # تشخیص نیاز به News API
        news_keywords = ['election', 'president', 'news', 'today', 'current', 'happening']
        if any(kw in query.lower() for kw in news_keywords):
            required_apis.extend(self.API_REQUIREMENTS['event_prediction']['apis'])
        
        return required_apis
    
    def create_api_request_message(self, query: str, required_apis: List[Dict]) -> str:
        """
        ایجاد پیام درخواست API از کاربر
        """
        
        if not required_apis:
            return ""
        
        message = "🔑 **API Key Required**\n\n"
        message += f"{self.API_REQUIREMENTS.get('description', 'To give you the most accurate prediction, I need:')}\n\n"
        
        for i, api in enumerate(required_apis, 1):
            message += f"{i}. **{api['name']}**\n"
            message += f"   📝 {api['description']}\n"
            message += f"   🔗 Get it here: {api['url']}\n"
            if api.get('optional'):
                message += "   ✨ (Optional - will improve accuracy)\n"
            else:
                message += "   ⚠️ (Required for this query)\n"
            message += "\n"
        
        message += "📤 **Send me the API key(s) in this format:**\n"
        message += "`API_NAME: YOUR_API_KEY`\n\n"
        message += "Example:\n"
        message += "`ETHERSCAN: ABC123XYZ456`\n"
        message += "`COINGECKO: DEF789UVW012`\n\n"
        message += "Or send them one by one."
        
        return message
    
    async def validate_api_key(self, api_type: APIType, api_key: str) -> Dict:
        """
        اعتبارسنجی API key
        
        Returns:
            {'valid': bool, 'message': str, 'details': dict}
        """
        
        try:
            if api_type == APIType.ETHERSCAN:
                return await self._validate_etherscan(api_key)
            elif api_type == APIType.BSCSCAN:
                return await self._validate_bscscan(api_key)
            elif api_type == APIType.COINGECKO:
                return await self._validate_coingecko(api_key)
            elif api_type == APIType.NEWSAPI:
                return await self._validate_newsapi(api_key)
            elif api_type == APIType.WEATHER:
                return await self._validate_weather(api_key)
            else:
                # برای APIهای دیگر، فقط فرمت رو بررسی می‌کنیم
                if len(api_key) > 10:
                    return {'valid': True, 'message': 'API key format accepted'}
                else:
                    return {'valid': False, 'message': 'API key too short'}
                    
        except Exception as e:
            logger.error(f"Error validating {api_type}: {e}")
            return {'valid': False, 'message': f'Validation error: {str(e)}'}
    
    async def _validate_etherscan(self, api_key: str) -> Dict:
        """اعتبارسنجی Etherscan API"""
        async with aiohttp.ClientSession() as session:
            url = f"https://api.etherscan.io/api"
            params = {
                'module': 'account',
                'action': 'balance',
                'address': '0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae',
                'tag': 'latest',
                'apikey': api_key
            }
            try:
                async with session.get(url, params=params, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') == '1':
                            return {'valid': True, 'message': '✅ Etherscan API key is valid'}
                        else:
                            return {'valid': False, 'message': f"❌ Invalid key: {data.get('message', 'Unknown error')}"}
                    else:
                        return {'valid': False, 'message': f"❌ HTTP {response.status}"}
            except Exception as e:
                return {'valid': False, 'message': f"❌ Connection error: {str(e)}"}
    
    async def _validate_coingecko(self, api_key: str) -> Dict:
        """اعتبارسنجی CoinGecko API"""
        async with aiohttp.ClientSession() as session:
            url = "https://api.coingecko.com/api/v3/ping"
            headers = {'x-cg-pro-api-key': api_key}
            try:
                async with session.get(url, headers=headers, timeout=5) as response:
                    if response.status == 200:
                        return {'valid': True, 'message': '✅ CoinGecko API key is valid'}
                    elif response.status == 401:
                        return {'valid': False, 'message': '❌ Invalid API key'}
                    else:
                        return {'valid': False, 'message': f"❌ HTTP {response.status}"}
            except Exception as e:
                return {'valid': False, 'message': f"❌ Connection error: {str(e)}"}
    
    async def _validate_newsapi(self, api_key: str) -> Dict:
        """اعتبارسنجی NewsAPI"""
        async with aiohttp.ClientSession() as session:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'country': 'us',
                'apiKey': api_key
            }
            try:
                async with session.get(url, params=params, timeout=5) as response:
                    if response.status == 200:
                        return {'valid': True, 'message': '✅ NewsAPI key is valid'}
                    elif response.status == 401:
                        return {'valid': False, 'message': '❌ Invalid API key'}
                    else:
                        return {'valid': False, 'message': f"❌ HTTP {response.status}"}
            except Exception as e:
                return {'valid': False, 'message': f"❌ Connection error: {str(e)}"}
    
    async def _validate_weather(self, api_key: str) -> Dict:
        """اعتبارسنجی OpenWeatherMap API"""
        async with aiohttp.ClientSession() as session:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': 'London',
                'appid': api_key
            }
            try:
                async with session.get(url, params=params, timeout=5) as response:
                    if response.status == 200:
                        return {'valid': True, 'message': '✅ Weather API key is valid'}
                    elif response.status == 401:
                        return {'valid': False, 'message': '❌ Invalid API key'}
                    else:
                        return {'valid': False, 'message': f"❌ HTTP {response.status}"}
            except Exception as e:
                return {'valid': False, 'message': f"❌ Connection error: {str(e)}"}
    
    async def _validate_bscscan(self, api_key: str) -> Dict:
        """اعتبارسنجی BSCscan API"""
        async with aiohttp.ClientSession() as session:
            url = "https://api.bscscan.com/api"
            params = {
                'module': 'account',
                'action': 'balance',
                'address': '0xb5d4f343412dc8efb6ff599d790074d0f1e8d430',
                'tag': 'latest',
                'apikey': api_key
            }
            try:
                async with session.get(url, params=params, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') == '1':
                            return {'valid': True, 'message': '✅ BSCscan API key is valid'}
                        else:
                            return {'valid': False, 'message': f"❌ Invalid key: {data.get('message', 'Unknown error')}"}
                    else:
                        return {'valid': False, 'message': f"❌ HTTP {response.status}"}
            except Exception as e:
                return {'valid': False, 'message': f"❌ Connection error: {str(e)}"}
    
    def parse_api_message(self, message: str) -> Dict[str, str]:
        """
        تجزیه پیام کاربر و استخراج API keyها
        
        Format: "API_NAME: API_KEY" or "API_NAME=API_KEY"
        """
        api_keys = {}
        
        # الگوهای مختلف
        patterns = [
            r'(?i)(etherscan|bscscan|coingecko|newsapi|weather|football)[\s:=]+([A-Za-z0-9\-_]{10,})',
            r'(?i)api[_\s]*(?:key)?[\s:=]+([A-Za-z0-9\-_]{10,})',
            r'(?i)([A-Za-z0-9\-_]{20,})'  # اگر فقط کلید رو فرستاد
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    api_name, api_key = match
                    api_keys[api_name.upper()] = api_key
                elif isinstance(match, str) and len(match) > 20:
                    # اگر فقط کلید بود، به عنوان آخرین API در نظر می‌گیریم
                    if 'last_api' in api_keys:
                        api_keys['CUSTOM'] = match
                    else:
                        api_keys['last_api'] = match
        
        return api_keys
    
    def store_temp_api_key(self, user_id: int, api_type: str, api_key: str):
        """ذخیره موقت API key برای کاربر (فقط برای session فعلی)"""
        
        if user_id not in self.temp_api_keys:
            self.temp_api_keys[user_id] = {}
        
        self.temp_api_keys[user_id][api_type] = {
            'key': api_key,
            'timestamp': datetime.now().isoformat(),
            'validated': False
        }
        
        logger.info(f"🔑 Temp API key stored for user {user_id}: {api_type}")
    
    def get_temp_api_key(self, user_id: int, api_type: str = None) -> Optional[str]:
        """دریافت API key موقت کاربر"""
        
        if user_id not in self.temp_api_keys:
            return None
        
        if api_type:
            return self.temp_api_keys[user_id].get(api_type, {}).get('key')
        else:
            # برگرداندن اولین API key
            for data in self.temp_api_keys[user_id].values():
                return data.get('key')
        
        return None
    
    def clear_temp_keys(self, user_id: int):
        """پاک کردن API keyهای موقت کاربر"""
        if user_id in self.temp_api_keys:
            del self.temp_api_keys[user_id]
            logger.info(f"🧹 Cleared temp API keys for user {user_id}")
    
    def log_request(self, user_id: int, query: str, apis_requested: List[str]):
        """ثبت درخواست API برای آمار"""
        
        self.request_history.append({
            'user_id': user_id,
            'query': query[:100],
            'apis': apis_requested,
            'timestamp': datetime.now().isoformat()
        })
        
        # نگه داشتن فقط 1000 رکورد آخر
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]
