# ==================== pandas fallback ====================
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    # جایگزین ساده برای مواقع ضروری
    class SimpleDataFrame:
        def __init__(self, data=None):
            self.data = data or []
        def to_dict(self):
            return {}
    pd = SimpleDataFrame
# ====================================================

# core/numerology_engine.py
"""
موتور عددشناسی نهایی
ترکیبی از: Pythagorean, Chaldean, Cabbalistic, Vedic, Chinese numerology
با قابلیت یادگیری از کتاب‌ها و الگوهای جدید
"""

import re
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional, Any, Union
import numpy as np
import math
import hashlib
import json
import pickle
from collections import Counter
import logging
from database.models import NumberMeaning, Teaching, Book, get_db

logger = logging.getLogger(__name__)

class NumerologyEngine:
    """
    هسته اصلی عددشناسی با ۵ سیستم مختلف و هوش ترکیبی
    """
    
    # ==================== سیستم فیثاغورثی ====================
    PYTHAGOREAN_MAP = {
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
        'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
        'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
    }
    
    # ==================== سیستم کلدانی ====================
    CHALDEAN_MAP = {
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
        'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
        'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
    }
    
    # ==================== سیستم کابالیستی (حروف عبری) ====================
    HEBREW_MAP = {
        'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
        'י': 10, 'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90,
        'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400,
        # حروف نهایی
        'ך': 500, 'ם': 600, 'ן': 700, 'ף': 800, 'ץ': 900
    }
    
    # ==================== سیستم ودایی (سانسکریت) ====================
    SANSKRIT_MAP = {
        'अ': 1, 'आ': 2, 'इ': 3, 'ई': 4, 'उ': 5, 'ऊ': 6, 'ऋ': 7, 'ॠ': 8, 'ऌ': 9,
        'ए': 1, 'ऐ': 2, 'ओ': 3, 'औ': 4, 'क': 1, 'ख': 2, 'ग': 3, 'घ': 4, 'ङ': 5,
        'च': 6, 'छ': 7, 'ज': 8, 'झ': 9, 'ञ': 1, 'ट': 2, 'ठ': 3, 'ड': 4, 'ढ': 5,
        'ण': 6, 'त': 7, 'थ': 8, 'द': 9, 'ध': 1, 'न': 2, 'प': 3, 'फ': 4, 'ब': 5,
        'भ': 6, 'म': 7, 'य': 8, 'र': 9, 'ल': 1, 'व': 2, 'श': 3, 'ष': 4, 'स': 5,
        'ह': 6
    }
    
    # ==================== اعداد خاص ====================
    MASTER_NUMBERS = [11, 22, 33, 44, 55, 66, 77, 88, 99]
    KARMIC_NUMBERS = [13, 14, 16, 19, 26]
    ANGEL_NUMBERS = [111, 222, 333, 444, 555, 666, 777, 888, 999, 1111]
    POWER_NUMBERS = [3, 7, 9, 11, 22, 33]
    SACRED_NUMBERS = [3, 7, 12, 40, 108]
    
    # ==================== تطابق‌های کیهانی ====================
    PLANETARY_RULERS = {
        1: 'Sun', 2: 'Moon', 3: 'Jupiter', 4: 'Uranus', 5: 'Mercury',
        6: 'Venus', 7: 'Neptune', 8: 'Saturn', 9: 'Mars', 11: 'Pluto',
        22: 'Proserpina', 33: 'Vulcan', 44: 'Chiron', 55: 'Ceres',
        66: 'Vesta', 77: 'Pallas', 88: 'Juno', 99: 'Eris'
    }
    
    ELEMENTAL_RULERS = {
        1: 'Fire', 2: 'Water', 3: 'Air', 4: 'Earth', 5: 'Air',
        6: 'Earth', 7: 'Water', 8: 'Earth', 9: 'Fire', 11: 'Spirit',
        22: 'Spirit', 33: 'Spirit', 44: 'Ether', 55: 'Light',
        66: 'Sound', 77: 'Consciousness'
    }
    
    ZODIAC_RULERS = {
        1: 'Aries', 2: 'Taurus', 3: 'Gemini', 4: 'Cancer', 5: 'Leo',
        6: 'Virgo', 7: 'Libra', 8: 'Scorpio', 9: 'Sagittarius',
        11: 'Capricorn', 22: 'Aquarius', 33: 'Pisces'
    }
    
    TAROT_CARDS = {
        1: 'The Magician', 2: 'The High Priestess', 3: 'The Empress',
        4: 'The Emperor', 5: 'The Hierophant', 6: 'The Lovers',
        7: 'The Chariot', 8: 'Strength', 9: 'The Hermit',
        11: 'Justice', 22: 'The Fool', 33: 'The World'
    }
    
    def __init__(self, db_session=None):
        self.db = db_session
        self.meanings_cache = {}
        self.teachings_cache = {}
        self.load_meanings()
        self.load_teachings()
        
    def load_meanings(self):
        """بارگذاری معانی اعداد از دیتابیس"""
        if self.db:
            meanings = self.db.query(NumberMeaning).all()
            for m in meanings:
                self.meanings_cache[m.number] = m
    
    def load_teachings(self):
        """بارگذاری آموزه‌های کتاب‌ها"""
        if self.db:
            teachings = self.db.query(Teaching).all()
            for t in teachings:
                if t.number_value not in self.teachings_cache:
                    self.teachings_cache[t.number_value] = []
                self.teachings_cache[t.number_value].append(t)
    
    # ==================== توابع پایه ====================
    
    def reduce_number(self, num: int, keep_master: bool = True, keep_angel: bool = True) -> int:
        """
        کاهش عدد به رقم اصلی با حفظ اعداد خاص
        
        Args:
            num: عدد ورودی
            keep_master: حفظ اعداد استاد
            keep_angel: حفظ اعداد فرشته
        
        Returns:
            عدد کاهش یافته
        """
        if num == 0:
            return 0
        
        # بررسی اعداد خاص
        if keep_master and num in self.MASTER_NUMBERS:
            return num
        
        if keep_angel and num in self.ANGEL_NUMBERS:
            return num
        
        # کاهش تا رسیدن به یک رقم
        while num > 9 and num not in self.MASTER_NUMBERS and num not in self.ANGEL_NUMBERS:
            num = sum(int(d) for d in str(num))
        
        return num
    
    def calculate_digital_root(self, num: int) -> int:
        """محاسبه ریشه دیجیتال (جمع مکرر تا یک رقم)"""
        while num > 9:
            num = sum(int(d) for d in str(num))
        return num
    
    def calculate_frequency(self, num: int) -> float:
        """محاسبه فرکانس ارتعاشی عدد"""
        # فرمول: فرکانس = (عدد * 7.83) / 9
        # 7.83 هرتز فرکانس زمین (Schumann resonance)
        return (num * 7.83) / 9
    
    # ==================== محاسبات تاریخ ====================
    
    def calculate_life_path(self, birth_date: Union[str, date]) -> Dict[str, Any]:
        """
        محاسبه عدد مسیر زندگی با ۳ روش مختلف
        
        Args:
            birth_date: تاریخ تولد (YYYY-MM-DD یا date object)
        
        Returns:
            دیکشنری کامل شامل اعداد و تفسیرها
        """
        # تبدیل تاریخ
        if isinstance(birth_date, str):
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        
        year = birth_date.year
        month = birth_date.month
        day = birth_date.day
        
        # روش ۱: کاهش مجزا
        year_sum = self.reduce_number(sum(int(d) for d in str(year)), keep_master=False)
        month_sum = self.reduce_number(month, keep_master=False)
        day_sum = self.reduce_number(day, keep_master=False)
        
        total1 = year_sum + month_sum + day_sum
        life_path1 = self.reduce_number(total1)
        
        # روش ۲: کاهش کلی
        total_digits = sum(int(d) for d in f"{year}{month:02d}{day:02d}")
        life_path2 = self.reduce_number(total_digits)
        
        # روش ۳: روش پیشرفته (ترکیب هر سه)
        life_path3 = self.reduce_number(life_path1 + life_path2)
        
        # انتخاب بهترین روش (رای‌گیری)
        candidates = [life_path1, life_path2, life_path3]
        counter = Counter(candidates)
        final_number = counter.most_common(1)[0][0]
        
        # محاسبه اعداد ثانویه
        birthday_number = self.reduce_number(day)
        attitudinal_number = self.reduce_number(day + month)
        maturity_number = self.reduce_number(life_path1 + self.calculate_name_number("")['expression'])
        
        # محاسبه چرخه‌های زندگی
        cycles = self.calculate_life_cycles(birth_date)
        
        # تفسیر
        interpretation = self.get_complete_interpretation(final_number)
        
        result = {
            'primary_number': final_number,
            'alternative_numbers': {
                'method1': life_path1,
                'method2': life_path2,
                'method3': life_path3
            },
            'secondary_numbers': {
                'birthday': birthday_number,
                'attitudinal': attitudinal_number,
                'maturity': maturity_number
            },
            'life_cycles': cycles,
            'is_master': final_number in self.MASTER_NUMBERS,
            'is_karmic': final_number in self.KARMIC_NUMBERS,
            'is_angel': final_number in self.ANGEL_NUMBERS,
            'planetary_ruler': self.PLANETARY_RULERS.get(final_number, 'Unknown'),
            'element': self.ELEMENTAL_RULERS.get(self.reduce_number(final_number), 'Unknown'),
            'zodiac': self.ZODIAC_RULERS.get(final_number, 'Unknown'),
            'tarot': self.TAROT_CARDS.get(final_number, 'Unknown'),
            'frequency': self.calculate_frequency(final_number),
            'interpretation': interpretation,
            'components': {
                'year': year_sum,
                'month': month_sum,
                'day': day_sum,
                'year_raw': year,
                'month_raw': month,
                'day_raw': day
            }
        }
        
        return result
    
    def calculate_life_cycles(self, birth_date: date) -> Dict[str, Any]:
        """محاسبه چرخه‌های زندگی"""
        year = birth_date.year
        month = birth_date.month
        day = birth_date.day
        
        # چرخه اول (تولد تا ۲۸ سالگی)
        cycle1 = self.reduce_number(month)
        
        # چرخه دوم (۲۸ تا ۵۶ سالگی)
        cycle2 = self.reduce_number(day)
        
        # چرخه سوم (۵۶ سالگی به بعد)
        cycle3 = self.reduce_number(year)
        
        # اوج‌ها (پیک‌ها)
        peak1 = self.reduce_number(cycle1 + cycle2)
        peak2 = self.reduce_number(cycle2 + cycle3)
        peak3 = self.reduce_number(peak1 + peak2)
        
        return {
            'cycles': {
                'first': {'number': cycle1, 'years': '0-28', 'interpretation': self.get_quick_interpretation(cycle1)},
                'second': {'number': cycle2, 'years': '28-56', 'interpretation': self.get_quick_interpretation(cycle2)},
                'third': {'number': cycle3, 'years': '56+', 'interpretation': self.get_quick_interpretation(cycle3)}
            },
            'peaks': {
                'first': {'number': peak1, 'age': '0-28', 'interpretation': self.get_quick_interpretation(peak1)},
                'second': {'number': peak2, 'age': '28-56', 'interpretation': self.get_quick_interpretation(peak2)},
                'third': {'number': peak3, 'age': '56+', 'interpretation': self.get_quick_interpretation(peak3)}
            }
        }
    
    # ==================== محاسبات نام ====================
    
    def calculate_name_number(self, name: str, system: str = 'all') -> Dict[str, Any]:
        """
        محاسبه عدد نام با ۵ سیستم مختلف
        
        Args:
            name: نام کامل
            system: 'pythagorean', 'chaldean', 'hebrew', 'sanskrit', 'all'
        
        Returns:
            دیکشنری کامل شامل اعداد از همه سیستم‌ها
        """
        if not name:
            return {'expression': 0, 'soul_urge': 0, 'personality': 0}
        
        # پاکسازی نام
        clean_name = re.sub(r'[^A-Za-z\u0590-\u05FF\u0900-\u097F\s]', '', name.upper())
        
        results = {}
        
        # سیستم فیثاغورثی
        if system in ['all', 'pythagorean']:
            results['pythagorean'] = self._calculate_with_map(clean_name, self.PYTHAGOREAN_MAP)
        
        # سیستم کلدانی
        if system in ['all', 'chaldean']:
            results['chaldean'] = self._calculate_with_map(clean_name, self.CHALDEAN_MAP)
        
        # سیستم عبری (اگر حروف عبری باشه)
        if system in ['all', 'hebrew'] and any('\u0590' <= c <= '\u05FF' for c in name):
            results['hebrew'] = self._calculate_with_map(clean_name, self.HEBREW_MAP)
        
        # سیستم سانسکریت (اگر حروف دوواناگری باشه)
        if system in ['all', 'sanskrit'] and any('\u0900' <= c <= '\u097F' for c in name):
            results['sanskrit'] = self._calculate_with_map(clean_name, self.SANSKRIT_MAP)
        
        # ترکیب نتایج (برای حالت all)
        if system == 'all':
            combined = self._combine_name_results(results)
        else:
            combined = results.get(system, self._calculate_with_map(clean_name, self.PYTHAGOREAN_MAP))
        
        # اضافه کردن اطلاعات تکمیلی
        if isinstance(combined, dict):
            combined['is_master'] = combined.get('expression', 0) in self.MASTER_NUMBERS
            combined['is_karmic'] = combined.get('expression', 0) in self.KARMIC_NUMBERS
            combined['planetary_ruler'] = self.PLANETARY_RULERS.get(combined.get('expression', 0), 'Unknown')
            combined['element'] = self.ELEMENTAL_RULERS.get(self.reduce_number(combined.get('expression', 0)), 'Unknown')
            combined['frequency'] = self.calculate_frequency(combined.get('expression', 0))
            combined['interpretation'] = self.get_complete_interpretation(combined.get('expression', 0))
        
        return combined
    
    def _calculate_with_map(self, name: str, char_map: Dict) -> Dict[str, Any]:
        """محاسبه با یک نگاشت مشخص"""
        words = name.split()
        
        word_results = []
        total_sum = 0
        vowel_sum = 0
        consonant_sum = 0
        
        vowels = 'AEIOU'
        
        for word in words:
            word_sum = 0
            word_vowels = 0
            word_consonants = 0
            
            for char in word:
                if char in char_map:
                    value = char_map[char]
                    word_sum += value
                    
                    if char in vowels:
                        vowel_sum += value
                        word_vowels += value
                    else:
                        consonant_sum += value
                        word_consonants += value
            
            word_reduced = self.reduce_number(word_sum)
            word_results.append({
                'word': word,
                'sum': word_sum,
                'reduced': word_reduced,
                'vowels': word_vowels,
                'consonants': word_consonants
            })
            
            total_sum += word_sum
        
        # اعداد نهایی
        expression = self.reduce_number(total_sum)
        soul_urge = self.reduce_number(vowel_sum)
        personality = self.reduce_number(consonant_sum)
        
        # عدد بلوغ (Maturity)
        maturity = self.reduce_number(expression + soul_urge)
        
        # عدد چالش (Challenge)
        challenge = abs(self.reduce_number(vowel_sum) - self.reduce_number(consonant_sum))
        
        return {
            'expression': expression,
            'soul_urge': soul_urge,
            'personality': personality,
            'maturity': maturity,
            'challenge': challenge,
            'words': word_results,
            'total_sum': total_sum,
            'vowel_sum': vowel_sum,
            'consonant_sum': consonant_sum
        }
    
    def _combine_name_results(self, results: Dict) -> Dict[str, Any]:
        """ترکیب نتایج از سیستم‌های مختلف"""
        combined = {
            'expression': 0,
            'soul_urge': 0,
            'personality': 0,
            'systems_used': list(results.keys())
        }
        
        if not results:
            return combined
        
        # میانگین‌گیری وزنی
        weights = {
            'pythagorean': 0.4,
            'chaldean': 0.3,
            'hebrew': 0.2,
            'sanskrit': 0.1
        }
        
        weighted_expr = 0
        weighted_soul = 0
        weighted_pers = 0
        total_weight = 0
        
        for system, data in results.items():
            weight = weights.get(system, 0.25)
            weighted_expr += data['expression'] * weight
            weighted_soul += data['soul_urge'] * weight
            weighted_pers += data['personality'] * weight
            total_weight += weight
        
        if total_weight > 0:
            combined['expression'] = self.reduce_number(round(weighted_expr / total_weight))
            combined['soul_urge'] = self.reduce_number(round(weighted_soul / total_weight))
            combined['personality'] = self.reduce_number(round(weighted_pers / total_weight))
        
        return combined
    
    # ==================== محاسبات پیشرفته ====================
    
    def calculate_personal_day(self, birth_date: str, target_date: str = None) -> Dict[str, Any]:
        """
        محاسبه عدد روز شخصی
        
        Args:
            birth_date: تاریخ تولد
            target_date: تاریخ هدف (امروز اگر None)
        
        Returns:
            عدد روز شخصی و تفسیر
        """
        if target_date is None:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        life_path = self.calculate_life_path(birth_date)
        universal_day = self.calculate_life_path(target_date)
        
        personal = life_path['primary_number'] + universal_day['primary_number']
        personal_day = self.reduce_number(personal)
        
        # محاسبه اعداد تکمیلی
        personal_month = self.calculate_personal_month(birth_date, target_date)
        personal_year = self.calculate_personal_year(birth_date, target_date)
        
        return {
            'personal_day': personal_day,
            'personal_month': personal_month,
            'personal_year': personal_year,
            'life_path': life_path['primary_number'],
            'universal_day': universal_day['primary_number'],
            'date': target_date,
            'interpretation': self.get_complete_interpretation(personal_day),
            'is_master': personal_day in self.MASTER_NUMBERS,
            'lucky_numbers': self.get_lucky_numbers(personal_day),
            'unlucky_numbers': self.get_unlucky_numbers(personal_day),
            'color': self.get_color(personal_day),
            'crystal': self.get_crystal(personal_day)
        }
    
    def calculate_personal_month(self, birth_date: str, target_date: str = None) -> int:
        """محاسبه عدد ماه شخصی"""
        if target_date is None:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        life_path = self.calculate_life_path(birth_date)
        target = datetime.strptime(target_date, '%Y-%m-%d')
        month_sum = life_path['primary_number'] + target.month + target.year
        return self.reduce_number(month_sum)
    
    def calculate_personal_year(self, birth_date: str, target_date: str = None) -> int:
        """محاسبه عدد سال شخصی"""
        if target_date is None:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        life_path = self.calculate_life_path(birth_date)
        target = datetime.strptime(target_date, '%Y-%m-%d')
        year_sum = life_path['primary_number'] + target.year
        return self.reduce_number(year_sum)
    
    def calculate_challenge_numbers(self, birth_date: str) -> Dict[str, int]:
        """محاسبه اعداد چالش"""
        bd = datetime.strptime(birth_date, '%Y-%m-%d').date()
        
        month = bd.month
        day = bd.day
        year = bd.year
        year_sum = sum(int(d) for d in str(year))
        
        # چالش اول: تفاوت ماه و روز
        challenge1 = abs(self.reduce_number(month) - self.reduce_number(day))
        
        # چالش دوم: تفاوت روز و سال
        challenge2 = abs(self.reduce_number(day) - self.reduce_number(year_sum))
        
        # چالش سوم: تفاوت چالش اول و دوم
        challenge3 = abs(challenge1 - challenge2)
        
        # چالش چهارم: تفاوت ماه و سال
        challenge4 = abs(self.reduce_number(month) - self.reduce_number(year_sum))
        
        return {
            'first': challenge1,
            'second': challenge2,
            'third': challenge3,
            'fourth': challenge4
        }
    
    def calculate_pinnacle_numbers(self, birth_date: str) -> Dict[str, Any]:
        """محاسبه اعداد قله"""
        bd = datetime.strptime(birth_date, '%Y-%m-%d').date()
        
        month = self.reduce_number(bd.month)
        day = self.reduce_number(bd.day)
        year = self.reduce_number(sum(int(d) for d in str(bd.year)))
        
        # قله اول: ماه + روز
        pinnacle1 = self.reduce_number(month + day)
        
        # قله دوم: روز + سال
        pinnacle2 = self.reduce_number(day + year)
        
        # قله سوم: قله اول + قله دوم
        pinnacle3 = self.reduce_number(pinnacle1 + pinnacle2)
        
        # قله چهارم: ماه + سال
        pinnacle4 = self.reduce_number(month + year)
        
        # محاسبه سنین
        age_first = 36 - pinnacle1
        age_second = age_first + 9
        age_third = age_second + 9
        age_fourth = age_third + 9
        
        return {
            'pinnacles': [
                {'number': pinnacle1, 'ages': f'0-{age_first}', 'interpretation': self.get_quick_interpretation(pinnacle1)},
                {'number': pinnacle2, 'ages': f'{age_first}-{age_second}', 'interpretation': self.get_quick_interpretation(pinnacle2)},
                {'number': pinnacle3, 'ages': f'{age_second}-{age_third}', 'interpretation': self.get_quick_interpretation(pinnacle3)},
                {'number': pinnacle4, 'ages': f'{age_third}+', 'interpretation': self.get_quick_interpretation(pinnacle4)}
            ]
        }
    
    # ==================== جماتریا و کلمات ====================
    
    def calculate_gematria(self, word: str, system: str = 'standard') -> Dict[str, Any]:
        """
        محاسبه جماتریا (ارزش عددی کلمات)
        
        Args:
            word: کلمه یا عبارت
            system: 'standard', 'ordinal', 'reduced', 'jewish', 'all'
        
        Returns:
            دیکشنری کامل ارزش‌ها
        """
        word = word.upper()
        results = {}
        
        # سیستم استاندارد (A=1, B=2, ... Z=26)
        if system in ['all', 'standard']:
            std_map = {chr(65+i): i+1 for i in range(26)}
            results['standard'] = self._calculate_gematria_with_map(word, std_map)
        
        # سیستم ترتیبی (A=1, B=2, ... Z=26)
        if system in ['all', 'ordinal']:
            ord_map = {chr(65+i): i+1 for i in range(26)}
            results['ordinal'] = self._calculate_gematria_with_map(word, ord_map)
        
        # سیستم کاهش یافته (A=1, B=2, ... Z=8)
        if system in ['all', 'reduced']:
            red_map = self.PYTHAGOREAN_MAP
            results['reduced'] = self._calculate_gematria_with_map(word, red_map)
        
        # سیستم عبری (Jewish Gematria)
        if system in ['all', 'jewish']:
            jewish_map = {
                'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
                'J': 600, 'K': 10, 'L': 20, 'M': 30, 'N': 40, 'O': 50, 'P': 60, 'Q': 70,
                'R': 80, 'S': 90, 'T': 100, 'U': 200, 'V': 700, 'W': 900, 'X': 300, 'Y': 400, 'Z': 500
            }
            results['jewish'] = self._calculate_gematria_with_map(word, jewish_map)
        
        # ترکیب نتایج
        combined = {}
        if system == 'all':
            for sys_name, data in results.items():
                combined[sys_name] = data['total']
            combined['primary'] = results.get('reduced', results.get('standard', {}))['total']
        else:
            combined = results.get(system, {})
        
        # اضافه کردن تفسیر
        if isinstance(combined, dict) and 'total' in combined:
            reduced = self.reduce_number(combined['total'])
            combined['reduced'] = reduced
            combined['is_master'] = reduced in self.MASTER_NUMBERS
            combined['interpretation'] = self.get_quick_interpretation(reduced)
        
        return combined
    
    def _calculate_gematria_with_map(self, word: str, char_map: Dict) -> Dict[str, Any]:
        """محاسبه جماتریا با نگاشت مشخص"""
        total = 0
        details = []
        
        for char in word:
            if char in char_map:
                value = char_map[char]
                total += value
                details.append({'char': char, 'value': value})
        
        return {
            'total': total,
            'details': details,
            'reduced': self.reduce_number(total, keep_master=False)
        }
    
    # ==================== اعداد خاص و ترکیبی ====================
    
    def analyze_number_compatibility(self, num1: int, num2: int) -> Dict[str, Any]:
        """
        تحلیل سازگاری دو عدد
        
        Returns:
            امتیاز سازگاری و توصیه‌ها
        """
        n1 = self.reduce_number(num1)
        n2 = self.reduce_number(num2)
        
        # محاسبه امتیاز پایه
        if n1 == n2:
            base_score = 100
        elif n1 + n2 == 10:
            base_score = 95  # اعداد مکمل
        elif abs(n1 - n2) == 1:
            base_score = 85  # اعداد همسایه
        elif abs(n1 - n2) == 2:
            base_score = 75
        elif abs(n1 - n2) == 3:
            base_score = 65
        else:
            base_score = 50
        
        # تطابق عنصری
        element1 = self.ELEMENTAL_RULERS.get(n1, 'Unknown')
        element2 = self.ELEMENTAL_RULERS.get(n2, 'Unknown')
        
        element_compatibility = {
            ('Fire', 'Fire'): 90,
            ('Fire', 'Air'): 85,
            ('Fire', 'Water'): 60,
            ('Fire', 'Earth'): 70,
            ('Water', 'Water'): 95,
            ('Water', 'Earth'): 85,
            ('Water', 'Air'): 65,
            ('Air', 'Air'): 90,
            ('Air', 'Earth'): 75,
            ('Earth', 'Earth'): 95,
        }
        
        element_score = element_compatibility.get((element1, element2), 50)
        
        # امتیاز نهایی
        final_score = (base_score * 0.6 + element_score * 0.4)
        
        # سطح سازگاری
        if final_score >= 90:
            level = "🌟 Cosmic Match"
            description = "Perfect harmony! This is a soulmate connection."
        elif final_score >= 80:
            level = "✨ Excellent Compatibility"
            description = "Strong connection with great potential."
        elif final_score >= 70:
            level = "💫 Good Compatibility"
            description = "Good match with some challenges to overcome."
        elif final_score >= 60:
            level = "⭐ Average Compatibility"
            description = "Can work well with understanding and compromise."
        else:
            level = "⚡ Challenging"
            description = "Requires effort and growth to harmonize."
        
        return {
            'number1': n1,
            'number2': n2,
            'compatibility_score': round(final_score, 1),
            'level': level,
            'description': description,
            'element1': element1,
            'element2': element2,
            'element_score': element_score,
            'advice': self._get_compatibility_advice(n1, n2)
        }
    
    def _get_compatibility_advice(self, n1: int, n2: int) -> str:
        """تولید توصیه سازگاری"""
        advice_map = {
            (1, 1): "Two leaders need to learn to share power.",
            (1, 2): "Balance independence with partnership.",
            (1, 3): "Combine creativity with leadership.",
            (2, 2): "Deep emotional connection, avoid codependency.",
            (2, 6): "Perfect for family and home life.",
            (3, 5): "Exciting and adventurous together.",
            (4, 8): "Power couple for business and success.",
            (6, 9): "Beautiful humanitarian partnership.",
            (7, 7): "Deep spiritual connection.",
            (8, 8): "Ambitious power couple, watch for ego.",
        }
        
        return advice_map.get((n1, n2), "Focus on communication and mutual respect.")
    
    def find_magic_square(self, number: int) -> List[List[int]]:
        """یافتن مربع جادویی برای عدد"""
        squares = {
            3: [[4, 9, 2], [3, 5, 7], [8, 1, 6]],  # Saturn
            4: [[4, 14, 15, 1], [9, 7, 6, 12], [5, 11, 10, 8], [16, 2, 3, 13]],  # Jupiter
            5: [[11, 24, 7, 20, 3], [4, 12, 25, 8, 16], [17, 5, 13, 21, 9], 
                [10, 18, 1, 14, 22], [23, 6, 19, 2, 15]],  # Mars
            6: [[6, 32, 3, 34, 35, 1], [7, 11, 27, 28, 8, 30], [19, 14, 16, 15, 23, 24],
                [18, 20, 22, 21, 17, 13], [25, 29, 10, 9, 26, 12], [36, 5, 33, 4, 2, 31]]  # Sun
        }
        
        # پیدا کردن نزدیک‌ترین مربع
        n = int(math.sqrt(number)) if number > 0 else 3
        if n in squares:
            return squares[n]
        
        # مربع پیش‌فرض
        return squares.get(3, [])
    
    def get_lucky_numbers(self, base_number: int, count: int = 5) -> List[int]:
        """تولید اعداد شانس بر اساس عدد پایه"""
        lucky = []
        n = self.reduce_number(base_number)
        
        # اعداد مرتبط
        related = {
            1: [1, 10, 19, 28, 37, 46, 55],
            2: [2, 11, 20, 29, 38, 47, 56],
            3: [3, 12, 21, 30, 39, 48, 57],
            4: [4, 13, 22, 31, 40, 49, 58],
            5: [5, 14, 23, 32, 41, 50, 59],
            6: [6, 15, 24, 33, 42, 51, 60],
            7: [7, 16, 25, 34, 43, 52, 61],
            8: [8, 17, 26, 35, 44, 53, 62],
            9: [9, 18, 27, 36, 45, 54, 63]
        }
        
        lucky = related.get(n, [n])[:count]
        return lucky
    
    def get_unlucky_numbers(self, base_number: int, count: int = 3) -> List[int]:
        """اعداد نامبارک"""
        n = self.reduce_number(base_number)
        opposite = 10 - n
        return [opposite, opposite + 9, opposite + 18][:count]
    
    def get_color(self, number: int) -> str:
        """رنگ مرتبط با عدد"""
        colors = {
            1: "Red, Gold",
            2: "White, Silver",
            3: "Yellow, Purple",
            4: "Blue, Green",
            5: "Light Blue, Gray",
            6: "Green, Pink",
            7: "Sea Green, Violet",
            8: "Black, Dark Blue",
            9: "Red, Crimson",
            11: "Pearl, White",
            22: "Indigo",
            33: "Gold"
        }
        return colors.get(self.reduce_number(number), "Rainbow")
    
    def get_crystal(self, number: int) -> str:
        """سنگ مرتبط با عدد"""
        crystals = {
            1: "Ruby, Diamond",
            2: "Pearl, Moonstone",
            3: "Amethyst, Citrine",
            4: "Sapphire, Emerald",
            5: "Topaz, Aquamarine",
            6: "Rose Quartz, Jade",
            7: "Amethyst, Lapis Lazuli",
            8: "Onyx, Black Tourmaline",
            9: "Garnet, Red Jasper",
            11: "Clear Quartz",
            22: "Labradorite",
            33: "Herkimer Diamond"
        }
        return crystals.get(self.reduce_number(number), "Crystal")
    
    def get_angel_message(self, number: int) -> str:
        """پیام فرشته برای اعداد"""
        messages = {
            111: "Your thoughts are manifesting rapidly. Focus on what you want.",
            222: "Trust that everything is working out for your highest good.",
            333: "The ascended masters are with you, guiding and protecting.",
            444: "The angels are surrounding you with love and support.",
            555: "Major positive changes are coming. Embrace them.",
            666: "Balance your thoughts between material and spiritual.",
            777: "You're on the right path. Congratulations!",
            888: "Abundance is flowing into your life.",
            999: "A phase is ending. New beginnings await.",
            1111: "You're aligned with the universe. Manifestation power is high."
        }
        return messages.get(number, "The angels are watching over you.")
    
    # ==================== تفسیرها ====================
    
    def get_complete_interpretation(self, number: int) -> Dict[str, Any]:
        """تفسیر کامل یک عدد"""
        n = self.reduce_number(number)
        
        # از دیتابیس
        if n in self.meanings_cache:
            m = self.meanings_cache[n]
            return {
                'pythagorean': m.pythagorean,
                'chaldean': m.chaldean,
                'cabbalistic': m.cabbalistic,
                'positive': m.positive_traits,
                'negative': m.negative_traits,
                'career': m.career,
                'love': m.love,
                'health': m.health,
                'spirituality': m.spirituality,
                'money': m.money,
                'planet': m.planet,
                'element': m.element,
                'color': m.color,
                'crystal': m.crystal,
                'tarot': m.tarot_card,
                'angel': m.angel
            }
        
        # تفسیر پیش‌فرض
        basic = {
            1: "Leadership, independence, originality. You're a pioneer.",
            2: "Cooperation, diplomacy, sensitivity. You're a peacemaker.",
            3: "Creativity, expression, optimism. You're an artist.",
            4: "Stability, discipline, practicality. You're a builder.",
            5: "Freedom, adventure, versatility. You're an explorer.",
            6: "Responsibility, love, harmony. You're a nurturer.",
            7: "Wisdom, analysis, spirituality. You're a seeker.",
            8: "Power, success, abundance. You're an achiever.",
            9: "Humanitarianism, completion, art. You're a healer.",
            11: "Master number of spiritual insight. You're an illuminator.",
            22: "Master builder. You can manifest dreams into reality.",
            33: "Master teacher of unconditional love.",
        }
        
        return {
            'pythagorean': basic.get(n, "Unknown"),
            'positive': "See your potential",
            'negative': "Work on your challenges",
            'planet': self.PLANETARY_RULERS.get(n, "Unknown"),
            'element': self.ELEMENTAL_RULERS.get(n, "Unknown")
        }
    
    def get_quick_interpretation(self, number: int) -> str:
        """تفسیر سریع"""
        quick = {
            1: "Leader. Independent. Creative.",
            2: "Diplomat. Peaceful. Sensitive.",
            3: "Artist. Expressive. Optimistic.",
            4: "Builder. Practical. Reliable.",
            5: "Explorer. Free. Adaptable.",
            6: "Nurturer. Responsible. Loving.",
            7: "Seeker. Wise. Analytical.",
            8: "Achiever. Powerful. Abundant.",
            9: "Healer. Humanitarian. Artistic.",
            11: "Illuminator. Intuitive. Inspired.",
            22: "Master Builder. Visionary.",
            33: "Master Teacher. Compassionate."
        }
        return quick.get(self.reduce_number(number), "Mystical number")
    
    # ==================== متدهای کاربردی ====================
    
    def hash_to_number(self, text: str) -> int:
        """تبدیل هر متنی به عدد (برای آدرس‌های توکن)"""
        hash_obj = hashlib.sha256(text.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        return self.reduce_number(hash_int)
    
    def analyze_token_address(self, address: str) -> Dict[str, Any]:
        """تحلیل عددشناسی آدرس توکن"""
        # استخراج اعداد از آدرس
        numbers = [int(c, 16) if c.isdigit() else ord(c) % 10 for c in address if c.isalnum()]
        
        if not numbers:
            return {}
        
        total = sum(numbers)
        reduced = self.reduce_number(total)
        
        # الگوهای خاص
        patterns = []
        if any(n == reduced for n in numbers):
            patterns.append("Self-referential pattern detected")
        
        # بررسی تکرار
        from collections import Counter
        counter = Counter(numbers)
        most_common = counter.most_common(1)[0] if counter else (0, 0)
        
        return {
            'total_sum': total,
            'reduced_number': reduced,
            'most_common_digit': most_common[0],
            'repetition_count': most_common[1],
            'has_master': any(n in self.MASTER_NUMBERS for n in numbers),
            'numerological_score': self.calculate_numerological_score(address),
            'interpretation': self.get_quick_interpretation(reduced),
            'lucky': reduced in [1, 3, 7, 8, 9],
            'patterns': patterns
        }
    
    def calculate_numerological_score(self, text: str) -> float:
        """امتیاز عددشناسی برای یک متن (0-100)"""
        numbers = [int(c, 16) if c.isdigit() else ord(c) % 10 for c in text if c.isalnum()]
        
        if not numbers:
            return 50
        
        # معیارهای مختلف
        avg = sum(numbers) / len(numbers)
        variance = sum((x - avg) ** 2 for x in numbers) / len(numbers)
        
        # امتیاز بر اساس توزیع
        if variance < 5:
            score = 90  # متوازن
        elif variance < 10:
            score = 70
        else:
            score = 50
        
        # بررسی وجود اعداد خاص
        if any(n in self.MASTER_NUMBERS for n in numbers):
            score += 10
        
        if any(n in self.ANGEL_NUMBERS for n in numbers):
            score += 5
        
        return min(score, 100)
    
    def get_trending_numbers(self, days: int = 7) -> List[int]:
        """اعداد پرطرفدار روز"""
        # اینجا می‌تونه از دیتابیس یا API استفاده کنه
        # فعلاً نمونه
        return [1, 7, 11, 22, 33, 44]
    
    def get_number_of_the_day(self) -> Dict[str, Any]:
        """عدد روز"""
        today = datetime.now()
        day_num = self.reduce_number(today.day)
        month_num = self.reduce_number(today.month)
        year_num = self.reduce_number(today.year)
        
        total = self.reduce_number(day_num + month_num + year_num)
        
        return {
            'date': today.strftime('%Y-%m-%d'),
            'day_number': day_num,
            'month_number': month_num,
            'year_number': year_num,
            'universal_number': total,
            'energy': self.get_quick_interpretation(total),
            'lucky_numbers': self.get_lucky_numbers(total, 3),
            'color': self.get_color(total),
            'crystal': self.get_crystal(total)
        }
