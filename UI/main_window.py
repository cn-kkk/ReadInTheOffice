import sys
import os

# 将项目根目录添加到Python的模块搜索路径中
# 这样无论从哪个目录运行，都能正确导入Backend等模块
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

import qdarkstyle # 把它加回来
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout,
    QComboBox, QLabel, QSpinBox, QPushButton, QDoubleSpinBox,
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
        self.config_handler = ConfigHandler()
        self.app_settings = self.config_handler.load_settings()

        # --- 窗口基本设置 ---
        self.setWindowTitle("摸鱼阅读器 - 设置")
        self.setFixedSize(400, 550) # 增加了高度以容纳新控件

        # --- 中心控件和主布局 ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- 使用网格布局来对齐控件 ---
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15) # 设置控件间的间距

        # 1. 小说选择
        grid_layout.addWidget(QLabel("选择小说:"), 0, 0)
        self.book_selector = QComboBox()
        self.load_books_to_selector() # 调用方法加载书籍
        grid_layout.addWidget(self.book_selector, 0, 1, 1, 2) # 让下拉框占据两列

        # 2. 字体大小
        grid_layout.addWidget(QLabel("字体大小:"), 1, 0)
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 72)
        self.font_size_spinbox.setValue(14)
        grid_layout.addWidget(self.font_size_spinbox, 1, 1, 1, 2)

        # 3. 背景颜色
        grid_layout.addWidget(QLabel("背景颜色:"), 2, 0)
        self.bg_color_button = QPushButton("选择颜色")
        self.bg_color_button.clicked.connect(self.select_bg_color)
        self.bg_color_preview = QLabel()
        self.bg_color_preview.setAutoFillBackground(True)
        self._set_color_preview(self.bg_color_preview, "#000000") # 默认黑色
        grid_layout.addWidget(self.bg_color_button, 2, 1)
        grid_layout.addWidget(self.bg_color_preview, 2, 2)

        # 4. 字体颜色
        grid_layout.addWidget(QLabel("字体颜色:"), 3, 0)
        self.font_color_button = QPushButton("选择颜色")
        self.font_color_button.clicked.connect(self.select_font_color)
        self.font_color_preview = QLabel()
        self.font_color_preview.setAutoFillBackground(True)
        self._set_color_preview(self.font_color_preview, "#FFFFFF") # 默认白色
        grid_layout.addWidget(self.font_color_button, 3, 1)
        grid_layout.addWidget(self.font_color_preview, 3, 2)

        # 5. 透明度
        grid_layout.addWidget(QLabel("图层透明度:"), 4, 0)
        self.opacity_spinbox = QDoubleSpinBox()
        self.opacity_spinbox.setRange(0.1, 1.0)
        self.opacity_spinbox.setSingleStep(0.05) # 将步长调整为0.05
        self.opacity_spinbox.setValue(0.7)
        grid_layout.addWidget(self.opacity_spinbox, 4, 1, 1, 2)

        # 6. 显示行数
        grid_layout.addWidget(QLabel("显示行数:"), 5, 0)
        self.lines_spinbox = QSpinBox()
        self.lines_spinbox.setRange(1, 20)
        self.lines_spinbox.setValue(10)
        grid_layout.addWidget(self.lines_spinbox, 5, 1, 1, 2)

        # 7. 每行字数
        grid_layout.addWidget(QLabel("每行字数:"), 6, 0)
        self.chars_spinbox = QSpinBox()
        self.chars_spinbox.setRange(10, 100)
        self.chars_spinbox.setValue(40)
        grid_layout.addWidget(self.chars_spinbox, 6, 1, 1, 2)
        
        # 8. 最小化快捷键
        grid_layout.addWidget(QLabel("最小化快捷键:"), 7, 0)
        minimize_hotkey_layout = QHBoxLayout()
        self.minimize_modifier_combo = QComboBox()
        self.minimize_modifier_combo.addItems(['Ctrl', 'Alt'])
        self.minimize_key_combo = QComboBox()
        # 更新按键列表
        keys = [chr(i) for i in range(ord('A'), ord('Z') + 1)] \
             + [str(i) for i in range(10)] \
             + ['-', '+', '[', ']', '\\', ';', "'", ',', '.', '/']
        self.minimize_key_combo.addItems(keys)
        
        # 添加伸缩因子以实现居中对齐
        minimize_hotkey_layout.addWidget(self.minimize_modifier_combo, 1)
        minimize_hotkey_layout.addWidget(QLabel("+"), 0, Qt.AlignCenter)
        minimize_hotkey_layout.addWidget(self.minimize_key_combo, 1)
        grid_layout.addLayout(minimize_hotkey_layout, 7, 1, 1, 2)

        # 设置默认值
        self.minimize_key_combo.setCurrentText("M")

        # 9. 关闭图层快捷键
        grid_layout.addWidget(QLabel("关闭图层快捷键:"), 8, 0)
        close_hotkey_layout = QHBoxLayout()
        self.close_modifier_combo = QComboBox()
        self.close_modifier_combo.addItems(['Ctrl', 'Alt'])
        self.close_key_combo = QComboBox()
        # 按键列表与最小化快捷键共享
        self.close_key_combo.addItems(keys)
        close_hotkey_layout.addWidget(self.close_modifier_combo, 1)
        close_hotkey_layout.addWidget(QLabel("+"), 0, Qt.AlignCenter)
        close_hotkey_layout.addWidget(self.close_key_combo, 1)
        grid_layout.addLayout(close_hotkey_layout, 8, 1, 1, 2)

        # 设置默认值
        self.close_modifier_combo.setCurrentText("Alt")
        self.close_key_combo.setCurrentText("Q")

        # 10. 翻页快捷键
        grid_layout.addWidget(QLabel("翻页快捷键:"), 9, 0)
        self.paging_combo = QComboBox()
        self.paging_combo.addItems(['← 和 →', 'A 和 D'])
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
            "background_color": self.background_color.name(),
            "font_color": self.font_color.name(),
            "opacity": self.opacity_spinbox.value(),
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

    def on_reader_closed(self, book_name, last_char_index):
        """当阅读窗口关闭时，保存阅读进度。"""
        print(f"保存进度: 书籍 '{book_name}'，字符位置 {last_char_index}")
        if "progress" not in self.app_settings:
            self.app_settings["progress"] = {}
        self.app_settings["progress"][book_name] = last_char_index
        self.config_handler.save_settings(self.app_settings)

# --- 程序入口 ---
# 这使得该文件可以被直接运行，方便我们预览UI效果
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet()) # 应用QDarkStyle样式
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
