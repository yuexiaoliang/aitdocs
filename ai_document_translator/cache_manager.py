import os
import hashlib
from typing import Optional


class CacheManager:
    """缓存管理器，用于管理翻译结果的缓存"""

    def __init__(self, cache_directory: str):
        """
        初始化缓存管理器

        Args:
            cache_directory: 缓存目录路径
        """
        self.cache_directory = cache_directory
        if not os.path.exists(self.cache_directory):
            os.makedirs(self.cache_directory)

    def _get_cache_file_path(self, content: str) -> str:
        """
        根据内容生成缓存文件路径

        Args:
            content: 文件内容

        Returns:
            缓存文件路径
        """
        # 使用内容的MD5值作为文件名
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        return os.path.join(self.cache_directory, content_hash)

    def get_from_cache(self, content: str) -> Optional[str]:
        """
        从缓存中获取翻译结果

        Args:
            content: 原始内容

        Returns:
            翻译后的内容，如果缓存中不存在则返回None
        """
        cache_file_path = self._get_cache_file_path(content)
        if os.path.exists(cache_file_path):
            try:
                with open(cache_file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"读取缓存文件失败: {e}")
        return None

    def save_to_cache(self, original_content: str, translated_content: str) -> None:
        """
        将翻译结果保存到缓存

        Args:
            original_content: 原始内容
            translated_content: 翻译后的内容
        """
        try:
            cache_file_path = self._get_cache_file_path(original_content)
            with open(cache_file_path, 'w', encoding='utf-8') as f:
                f.write(translated_content)
        except Exception as e:
            print(f"保存缓存文件失败: {e}")