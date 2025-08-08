# -*- coding: utf-8 -*-

import os
import re
import chardet

class NovelHandler:
    """
    负责处理小说文件，核心功能是解码并返回完整的字符串内容。
    """
    def __init__(self, books_dir_name="books"):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.books_dir = os.path.join(project_root, books_dir_name)
        os.makedirs(self.books_dir, exist_ok=True)

    def get_all_books_names(self):
        try:
            files = os.listdir(self.books_dir)
            return [f for f in files if f.endswith('.txt')]
        except FileNotFoundError:
            return []

    def _detect_encoding(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(4096) # 读取前4KB来检测
            result = chardet.detect(raw_data)
            encoding = result.get('encoding', 'utf-8')
            if encoding and encoding.lower() in ['gb2312', 'gb18030']:
                return 'gbk'
            return encoding if encoding else 'utf-8'
        except (FileNotFoundError, IndexError):
            return 'utf-8'

    def load_book_as_string(self, book_filename):
        """
        检测文件编码，并将整个文件一次性解码成一个字符串。
        返回 (内容字符串, 错误信息) 的元组。
        """
        book_path = os.path.join(self.books_dir, book_filename)
        if not os.path.exists(book_path):
            return None, f"错误：找不到文件 {book_filename}"

        encoding = self._detect_encoding(book_path)
        
        try:
            with open(book_path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()
            # 清理文本，将所有类型的空白符（换行、空格、制表符等）替换掉
            processed_content = re.sub(r'\s+', '', content)
            return processed_content, None
        except Exception as e:
            return None, f"打开或读取文件时出错: {e}"
