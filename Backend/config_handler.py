import json
import os

class ConfigHandler:
    """
    处理应用程序的配置文件（config.json）的加载和保存。
    """
    def __init__(self, config_dir="resources", config_filename="config.json"):
        """
        初始化配置处理器。
        会自动计算出项目根目录下的resources/config.json的绝对路径。
        """
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.config_path = os.path.join(project_root, config_dir, config_filename)
        # 确保配置目录存在
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

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
        将给定的设置字典保存到config.json文件。
        """
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
