import json
import os
import sys

class ConfigHandler:
    """
    处理应用程序的配置文件（config.json）的加载和保存。
    """
    def __init__(self, config_dir="resources", config_filename="config.json"):
        """
        初始化配置处理器。
        开发环境使用项目根目录下的resources/config.json；
        打包后的应用使用当前用户的本地应用数据目录。
        """
        if getattr(sys, 'frozen', False):
            local_app_data = os.getenv("LOCALAPPDATA")
            if local_app_data:
                config_root = os.path.join(local_app_data, "ReadInTheOffice")
            else:
                config_root = os.path.join(os.path.expanduser("~"), ".ReadInTheOffice")
            self.config_path = os.path.join(config_root, config_filename)
        else:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            self.config_path = os.path.join(project_root, config_dir, config_filename)

        # 确保配置目录存在
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        self.temp_config_path = f"{self.config_path}.tmp"
        self._remove_stale_temp_file()

    def _remove_stale_temp_file(self):
        """移除上次异常中断时未替换成功的临时配置文件。"""
        try:
            os.remove(self.temp_config_path)
        except FileNotFoundError:
            pass

    def get_default_settings(self):
        """
        返回一个包含所有默认设置的字典。
        """
        return {
            "font_size": 14,
            "font_color": "#FFFFFF",
            "background_color": "#000000",
            "opacity": 0.7,
            "lines_per_page": 10,
            "chars_per_line": 40,
            "minimize_hotkey": "<ctrl>+m",
            "close_hotkey": "<alt>+q",
            "paging_hotkey": "← 和 →",
            "progress": {} # 用于存储每本书的阅读进度
        }

    def load_settings(self):
        """
        从config.json文件加载设置。
        如果文件不存在或无效，则返回并保存一套默认设置。
        """
        if not os.path.exists(self.config_path):
            default_settings = self.get_default_settings()
            self.save_settings(default_settings)
            return default_settings
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # 确保所有键都存在，如果缺少则从默认值中补充
                default_settings = self.get_default_settings()
                is_updated = False
                for key, value in default_settings.items():
                    if key not in settings:
                        settings[key] = value
                        is_updated = True
                if is_updated:
                    self.save_settings(settings)
                return settings
        except (json.JSONDecodeError, TypeError):
            # 如果文件损坏，则用默认设置覆盖它
            default_settings = self.get_default_settings()
            self.save_settings(default_settings)
            return default_settings

    def save_settings(self, settings):
        """
        将给定设置保存到config.json文件。
        """
        try:
            with open(self.temp_config_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
                f.flush()
                os.fsync(f.fileno())
            os.replace(self.temp_config_path, self.config_path)
        except Exception:
            self._remove_stale_temp_file()
            raise
