"""
File handling utilities for JSON operations.
"""

import json
from pathlib import Path
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)


class FileHandler:
    """ファイルの読み書き処理を管理するクラス"""
    
    @staticmethod
    def read_json(file_path: Path) -> Optional[dict]:
        """
        JSONファイルを読み込む
        
        Args:
            file_path: ファイルパス
            
        Returns:
            読み込んだデータ（辞書形式）。失敗時はNone
        """
        try:
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Successfully read file: {file_path}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    @staticmethod
    def write_json(file_path: Path, data: Any, ensure_dir: bool = True) -> bool:
        """
        JSONファイルに書き込む
        
        Args:
            file_path: ファイルパス
            data: 書き込むデータ
            ensure_dir: ディレクトリが存在しない場合に作成するか
            
        Returns:
            成功時True、失敗時False
        """
        try:
            if ensure_dir:
                file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Successfully wrote file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return False
    
    @staticmethod
    def file_exists(file_path: Path) -> bool:
        """
        ファイルの存在を確認する
        
        Args:
            file_path: ファイルパス
            
        Returns:
            存在する場合True
        """
        return file_path.exists() and file_path.is_file()
    
    @staticmethod
    def ensure_directory(directory: Path) -> bool:
        """
        ディレクトリの存在を確認し、なければ作成する
        
        Args:
            directory: ディレクトリパス
            
        Returns:
            成功時True、失敗時False
        """
        try:
            directory.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Error creating directory {directory}: {e}")
            return False
    
    @staticmethod
    def list_json_files(directory: Path) -> list:
        """
        ディレクトリ内のJSONファイル一覧を取得する
        
        Args:
            directory: ディレクトリパス
            
        Returns:
            JSONファイルのパスリスト
        """
        if not directory.exists():
            return []
        
        return list(directory.glob("*.json"))

