"""
Date and time utility functions.
"""

from datetime import datetime, date
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DateUtils:
    """日付・時刻処理のユーティリティクラス"""
    
    @staticmethod
    def get_current_datetime_iso() -> str:
        """
        現在の日時をISO 8601形式で取得
        
        Returns:
            ISO 8601形式の日時文字列
        """
        return datetime.now().isoformat()
    
    @staticmethod
    def get_current_date_str() -> str:
        """
        現在の日付をYYYY-MM-DD形式で取得
        
        Returns:
            YYYY-MM-DD形式の日付文字列
        """
        return date.today().strftime("%Y-%m-%d")
    
    @staticmethod
    def parse_iso_datetime(iso_string: str) -> Optional[datetime]:
        """
        ISO 8601形式の文字列をdatetimeオブジェクトに変換
        
        Args:
            iso_string: ISO 8601形式の日時文字列
            
        Returns:
            datetimeオブジェクト。失敗時はNone
        """
        try:
            return datetime.fromisoformat(iso_string)
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing ISO datetime: {iso_string}, {e}")
            return None
    
    @staticmethod
    def format_datetime_display(iso_string: str) -> str:
        """
        ISO 8601形式の日時を表示用にフォーマット
        
        Args:
            iso_string: ISO 8601形式の日時文字列
            
        Returns:
            表示用フォーマット（例: 2025年10月25日 14:30）
        """
        try:
            dt = datetime.fromisoformat(iso_string)
            return dt.strftime("%Y年%m月%d日 %H:%M")
        except (ValueError, TypeError) as e:
            logger.error(f"Error formatting datetime: {iso_string}, {e}")
            return iso_string
    
    @staticmethod
    def format_date_display(date_string: str) -> str:
        """
        YYYY-MM-DD形式の日付を表示用にフォーマット
        
        Args:
            date_string: YYYY-MM-DD形式の日付文字列
            
        Returns:
            表示用フォーマット（例: 2025年10月25日）
        """
        try:
            dt = datetime.strptime(date_string, "%Y-%m-%d")
            return dt.strftime("%Y年%m月%d日")
        except (ValueError, TypeError) as e:
            logger.error(f"Error formatting date: {date_string}, {e}")
            return date_string
    
    @staticmethod
    def calculate_days_ago(iso_string: str) -> Optional[int]:
        """
        指定日時から現在までの経過日数を計算
        
        Args:
            iso_string: ISO 8601形式の日時文字列
            
        Returns:
            経過日数。失敗時はNone
        """
        try:
            dt = datetime.fromisoformat(iso_string)
            now = datetime.now()
            delta = now - dt
            return delta.days
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating days ago: {iso_string}, {e}")
            return None
    
    @staticmethod
    def is_same_day(date_str1: str, date_str2: str) -> bool:
        """
        2つの日付文字列が同じ日かどうかを判定
        
        Args:
            date_str1: YYYY-MM-DD形式の日付文字列
            date_str2: YYYY-MM-DD形式の日付文字列
            
        Returns:
            同じ日の場合True
        """
        return date_str1 == date_str2
    
    @staticmethod
    def get_week_range(target_date: Optional[str] = None) -> tuple:
        """
        指定日（デフォルトは今日）を含む週の開始日と終了日を取得
        
        Args:
            target_date: YYYY-MM-DD形式の日付文字列（Noneの場合は今日）
            
        Returns:
            (開始日, 終了日)のタプル（YYYY-MM-DD形式）
        """
        try:
            if target_date:
                dt = datetime.strptime(target_date, "%Y-%m-%d")
            else:
                dt = datetime.now()
            
            # 月曜日を週の始まりとする
            start = dt - datetime.timedelta(days=dt.weekday())
            end = start + datetime.timedelta(days=6)
            
            return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error getting week range: {target_date}, {e}")
            return (None, None)

