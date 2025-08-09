import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

import qdarkstyle # 把它加回来
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout,
    QComboBox, QLabel, QSpinBox, QPushButton, QLineEdit,
    QColorDialog, QKeySequenceEdit
)
from PySide6.QtGui import QColor, QPalette, QKeySequence
from PySide6.QtCore import Qt

# --- 后端模块导入 ---
from Backend.novel_handler import NovelHandler
from Backend.config_handler import ConfigHandler
from UI.reader_view import ReaderView

class MainWindow(QMainWindow):
    """
    主设置窗口。
    用户在此配置所有参数，然后启动阅读窗口。
    """
    def __init__(self):
        super().__init__()

        # --- 初始化后端处理器 ---
        self.novel_handler = NovelHandler()
        self.config_handler = ConfigHandler()
        self.app_settings = self.config_handler.load_settings()

        # --- 窗口基本设置 ---
        self.setWindowTitle("有时间还是要多读书 - 丁真")
        self.setFixedSize(400, 550) # 增加了高度以容纳新控件

        # --- 中心控件和主布局 ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- 控制按钮 (移动到这里，确保提前初始化) ---
        self.start_button = QPushButton("启动阅读")
        self.start_button.setFixedHeight(40)
        self.start_button.clicked.connect(self.start_reading) # 连接到新的方法
        self.quit_button = QPushButton("退出程序")
        self.quit_button.setFixedHeight(40)
        self.quit_button.clicked.connect(QApplication.instance().quit)

        # --- 使用网格布局来对齐控件 ---
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15) # 设置控件间的间距

        # 1. 小说选择
        grid_layout.addWidget(QLabel("选择小说:"), 0, 0)
        self.book_selector = QComboBox()
        self.load_books_to_selector() # 调用方法加载书籍
        # 尝试从配置中恢复上次选择的小说
        last_selected_book = self.app_settings.get("last_selected_book")
        if last_selected_book and last_selected_book in [self.book_selector.itemText(i) for i in range(self.book_selector.count())]:
            self.book_selector.setCurrentText(last_selected_book)
        grid_layout.addWidget(self.book_selector, 0, 1, 1, 2) # 让下拉框占据两列

        # 2. 字体大小
        grid_layout.addWidget(QLabel("字体大小:"), 1, 0)
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 72)
        self.font_size_spinbox.setValue(self.app_settings.get("font_size", 14))
        grid_layout.addWidget(self.font_size_spinbox, 1, 1, 1, 2)

        # 3. 背景颜色
        grid_layout.addWidget(QLabel("背景颜色:"), 2, 0)
        self.bg_color_button = QPushButton("选择颜色")
        self.bg_color_button.clicked.connect(self.select_bg_color)
        self.bg_color_preview = QLabel()
        self.bg_color_preview.setAutoFillBackground(True)
        # 从配置中恢复背景色
        configured_bg_color = self.app_settings.get("background_color", "#000000")
        # 如果是rgba格式，只取rgb部分用于预览
        if configured_bg_color.startswith("rgba"):
            # 从rgba(r,g,b,a)中提取rgb
            parts = configured_bg_color.split('(')[1].split(')')[0].split(',')
            r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
            self.background_color = QColor(r, g, b)
        else:
            self.background_color = QColor(configured_bg_color)
        self._set_color_preview(self.bg_color_preview, self.background_color.name())
        grid_layout.addWidget(self.bg_color_button, 2, 1)
        grid_layout.addWidget(self.bg_color_preview, 2, 2)

        # 4. 字体颜色
        grid_layout.addWidget(QLabel("字体颜色:"), 3, 0)
        self.font_color_button = QPushButton("选择颜色")
        self.font_color_button.clicked.connect(self.select_font_color)
        self.font_color_preview = QLabel()
        self.font_color_preview.setAutoFillBackground(True)
        # 从配置中恢复字体颜色
        self.font_color = QColor(self.app_settings.get("font_color", "#FFFFFF"))
        self._set_color_preview(self.font_color_preview, self.font_color.name())
        grid_layout.addWidget(self.font_color_button, 3, 1)
        grid_layout.addWidget(self.font_color_preview, 3, 2)

        # 5. 透明度
        grid_layout.addWidget(QLabel("图层透明度:"), 4, 0)
        
        self.opacity_input = QLineEdit()
        self.opacity_input.setPlaceholderText("0.01 - 1.00")
        
        initial_opacity = self.app_settings.get("opacity", 0.7)
        self.opacity_input.setText(f"{initial_opacity:.2f}")

        self.opacity_input.textChanged.connect(self._validate_opacity_input)

        opacity_h_layout = QHBoxLayout() # Use a horizontal layout for input and icon
        opacity_h_layout.addWidget(self.opacity_input)

        # Add exclamation mark icon
        info_icon = QLabel()
        info_icon.setText("ⓘ") # Unicode info symbol
        info_icon.setToolTip("透明度范围: 0.01 到 1.00 (精确到两位小数)")
        info_icon.setStyleSheet("font-weight: bold; color: white;") # Orange color for info

        opacity_h_layout.addWidget(info_icon)
        opacity_h_layout.setStretch(0, 1) # Make input box stretch

        grid_layout.addLayout(opacity_h_layout, 4, 1, 1, 2)

        # 6. 显示行数
        grid_layout.addWidget(QLabel("显示行数:"), 5, 0)
        self.lines_spinbox = QSpinBox()
        self.lines_spinbox.setRange(1, 20)
        self.lines_spinbox.setValue(self.app_settings.get("lines_per_page", 10))
        grid_layout.addWidget(self.lines_spinbox, 5, 1, 1, 2)

        # 7. 每行字数
        grid_layout.addWidget(QLabel("每行字数:"), 6, 0)
        self.chars_spinbox = QSpinBox()
        self.chars_spinbox.setRange(10, 100)
        self.chars_spinbox.setValue(self.app_settings.get("chars_per_line", 40))
        grid_layout.addWidget(self.chars_spinbox, 6, 1, 1, 2)
        
        # 8. 最小化快捷键
        grid_layout.addWidget(QLabel("最小化快捷键:"), 7, 0)
        minimize_hotkey_layout = QHBoxLayout()
        self.minimize_modifier_combo = QComboBox()
        self.minimize_modifier_combo.addItems(['Ctrl', 'Alt'])
        # 从配置中恢复修饰键
        min_hotkey_str = self.app_settings.get("minimize_hotkey", "<ctrl>+m")
        min_mod = min_hotkey_str.split('+')[0].replace('<', '').replace('>', '').capitalize()
        if min_mod in [self.minimize_modifier_combo.itemText(i) for i in range(self.minimize_modifier_combo.count())]:
            self.minimize_modifier_combo.setCurrentText(min_mod)

        self.minimize_key_combo = QComboBox()
        keys = [chr(i) for i in range(ord('A'), ord('Z') + 1)] \
             + [str(i) for i in range(10)] \
             + ['-', '+', '[', ']', '\\', ';', "'", ',', '.', '/']
        self.minimize_key_combo.addItems(keys)
        # 从配置中恢复主键
        min_key_val = min_hotkey_str.split('+')[1].upper()
        if min_key_val in [self.minimize_key_combo.itemText(i) for i in range(self.minimize_key_combo.count())]:
            self.minimize_key_combo.setCurrentText(min_key_val)

        minimize_hotkey_layout.addWidget(self.minimize_modifier_combo, 1)
        minimize_hotkey_layout.addWidget(QLabel("+"), 0, Qt.AlignCenter)
        minimize_hotkey_layout.addWidget(self.minimize_key_combo, 1)
        grid_layout.addLayout(minimize_hotkey_layout, 7, 1, 1, 2)

        # 9. 关闭图层快捷键
        grid_layout.addWidget(QLabel("关闭图层快捷键:"), 8, 0)
        close_hotkey_layout = QHBoxLayout()
        self.close_modifier_combo = QComboBox()
        self.close_modifier_combo.addItems(['Ctrl', 'Alt'])
        # 从配置中恢复修饰键
        close_hotkey_str = self.app_settings.get("close_hotkey", "<alt>+q")
        close_mod = close_hotkey_str.split('+')[0].replace('<', '').replace('>', '').capitalize()
        if close_mod in [self.close_modifier_combo.itemText(i) for i in range(self.close_modifier_combo.count())]:
            self.close_modifier_combo.setCurrentText(close_mod)

        self.close_key_combo = QComboBox()
        self.close_key_combo.addItems(keys)
        # 从配置中恢复主键
        close_key_val = close_hotkey_str.split('+')[1].upper()
        if close_key_val in [self.close_key_combo.itemText(i) for i in range(self.close_key_combo.count())]:
            self.close_key_combo.setCurrentText(close_key_val)

        close_hotkey_layout.addWidget(self.close_modifier_combo, 1)
        close_hotkey_layout.addWidget(QLabel("+"), 0, Qt.AlignCenter)
        close_hotkey_layout.addWidget(self.close_key_combo, 1)
        grid_layout.addLayout(close_hotkey_layout, 8, 1, 1, 2)

        # 10. 翻页快捷键
        grid_layout.addWidget(QLabel("翻页快捷键:"), 9, 0)
        self.paging_combo = QComboBox()
        self.paging_combo.addItems(['← 和 →', 'A 和 D'])
        # 从配置中恢复翻页设置
        configured_paging = self.app_settings.get("paging_hotkey", "← 和 →")
        if configured_paging in [self.paging_combo.itemText(i) for i in range(self.paging_combo.count())]:
            self.paging_combo.setCurrentText(configured_paging)
        grid_layout.addWidget(self.paging_combo, 9, 1, 1, 2)

        # --- 控制按钮 ---
        self.start_button = QPushButton("启动阅读")
        self.start_button.setFixedHeight(40)
        self.start_button.clicked.connect(self.start_reading) # 连接到新的方法
        self.quit_button = QPushButton("退出程序")
        self.quit_button.setFixedHeight(40)
        self.quit_button.clicked.connect(QApplication.instance().quit)

        # --- 将布局添加到主布局中 ---
        main_layout.addLayout(grid_layout)
        main_layout.addStretch() # 添加一个伸缩弹簧，让按钮靠下
        main_layout.addWidget(self.start_button)
        main_layout.addWidget(self.quit_button)

        # --- 存储颜色值的变量 ---
        self.background_color = QColor('#000000')
        self.font_color = QColor('#FFFFFF')

    def load_books_to_selector(self):
        """从后端加载书籍列表并更新到下拉框"""
        book_list = self.novel_handler.get_all_books_names()
        if book_list:
            self.book_selector.addItems(book_list)
        else:
            self.book_selector.addItem("books文件夹为空")
            self.book_selector.setEnabled(False)

    def _set_color_preview(self, label, color_hex):
        """内部方法：设置颜色预览标签的背景色"""
        label.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #AAAAAA;")

    def select_bg_color(self):
        """槽函数：弹出颜色选择对话框来选择背景色"""
        color = QColorDialog.getColor(self.background_color, self, "选择背景颜色")
        if color.isValid():
            self.background_color = color
            self._set_color_preview(self.bg_color_preview, color.name())

    def select_font_color(self):
        """槽函数：弹出颜色选择对话框来选择字体颜色"""
        color = QColorDialog.getColor(self.font_color, self, "选择字体颜色")
        if color.isValid():
            self.font_color = color
            self._set_color_preview(self.font_color_preview, color.name())

    def start_reading(self):
        """收集UI设置, 加载小说为字符串, 创建并显示阅读窗口。"""
        # 1. 收集所有UI上的设置
        # 将RGB颜色和透明度组合成RGBA颜色字符串
        rgb = self.background_color.getRgb()[:3] # 获取(r, g, b)
        alpha = float(self.opacity_input.text())
        rgba_color = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"

        min_modifier = self.minimize_modifier_combo.currentText().lower()
        min_key = self.minimize_key_combo.currentText().lower()
        minimize_hotkey = f"<{min_modifier}>+{min_key}"

        close_modifier = self.close_modifier_combo.currentText().lower()
        close_key = self.close_key_combo.currentText().lower()
        close_hotkey = f"<{close_modifier}>+{close_key}"

        selected_book = self.book_selector.currentText()
        if selected_book == "books文件夹为空":
            print("没有可读的书籍。")
            return

        settings = {
            "selected_book": selected_book,
            "font_size": self.font_size_spinbox.value(),
            "background_color": rgba_color, # 使用组合后的RGBA颜色
            "font_color": self.font_color.name(),
            "lines_per_page": self.lines_spinbox.value(),
            "chars_per_line": self.chars_spinbox.value(),
            "minimize_hotkey": minimize_hotkey,
            "close_hotkey": close_hotkey,
            "paging_hotkey": self.paging_combo.currentText(),
        }

        # 2. 加载小说内容为完整字符串
        full_content, error_msg = self.novel_handler.load_book_as_string(selected_book)
        if error_msg:
            print(error_msg)
            return

        # 3. 获取这本书的起始阅读字符索引
        progress = self.app_settings.get("progress", {})
        start_char_index = progress.get(selected_book, 0)
        settings["start_char_index"] = start_char_index

        # 4. 创建和显示ReaderView
        self.reader_view = ReaderView(settings, full_content)
        self.reader_view.closed.connect(self.on_reader_closed)
        self.reader_view.show()
        self.reader_view.activateWindow()
        self.reader_view.setFocus()

        # 5. 保存当前配置到文件
        # 确保保存的配置包含所有UI上的最新值，以及当前选择的书籍
        self.app_settings["font_size"] = settings["font_size"]
        self.app_settings["background_color"] = settings["background_color"]
        self.app_settings["font_color"] = settings["font_color"]
        alpha = float(self.opacity_input.text())
        # ...
        self.app_settings["opacity"] = float(self.opacity_input.text()) # 直接从spinbox获取，因为settings里没有这个key
        self.app_settings["lines_per_page"] = settings["lines_per_page"]
        self.app_settings["chars_per_line"] = settings["chars_per_line"]
        self.app_settings["minimize_hotkey"] = settings["minimize_hotkey"]
        self.app_settings["close_hotkey"] = settings["close_hotkey"]
        self.app_settings["paging_hotkey"] = settings["paging_hotkey"]
        self.app_settings["last_selected_book"] = settings["selected_book"]
        self.config_handler.save_settings(self.app_settings)

    def on_reader_closed(self, book_name, last_char_index):
        """当阅读窗口关闭时，保存阅读进度。"""
        print(f"保存进度: 书籍 '{book_name}'，字符位置 {last_char_index}")
        if "progress" not in self.app_settings:
            self.app_settings["progress"] = {}
        self.app_settings["progress"][book_name] = last_char_index
        self.config_handler.save_settings(self.app_settings)

    def _validate_opacity_input(self, text):
        try:
            value = float(text)
            if 0.01 <= value <= 1.00 and round(value * 100) == value * 100:
                self.opacity_input.setStyleSheet("")
                self.start_button.setEnabled(True)
            else:
                self.opacity_input.setStyleSheet("border: 1px solid red;")
                self.start_button.setEnabled(False)
        except ValueError:
            self.opacity_input.setStyleSheet("border: 1px solid red;")
            self.start_button.setEnabled(False)

# --- 程序入口 ---
# 这使得该文件可以被直接运行，方便我们预览UI效果
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet()) # 应用QDarkStyle样式
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
