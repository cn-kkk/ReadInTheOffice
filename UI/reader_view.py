import sys
from threading import Thread
from pynput import keyboard
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QPoint, Signal, Slot
from PySide6.QtGui import QKeyEvent, QMouseEvent, QFont

class ReaderView(QWidget):
    """
    基于完整字符串内容和字符索引来显示小说的阅读图层。
    """
    # 定义信号
    toggle_visibility_signal = Signal()
    close_signal = Signal()
    closed = Signal(str, int) # 关闭时发出，参数为(书名, 字符索引)

    def __init__(self, settings, full_content):
        super().__init__()

        # --- 初始化成员变量 ---
        self.settings = settings
        self.full_content = full_content
        self.hotkey_listener = None
        self.current_char_index = self.settings.get("start_char_index", 0)
        self.page_char_count = self.settings.get("chars_per_line", 40) * self.settings.get("lines_per_page", 10)

        # --- 窗口属性设置 ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        # 重新启用 Qt.WA_TranslucentBackground
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.resize(600, 400)

        # --- UI控件设置 ---
        self.text_label = QLabel(self)
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        font = QFont()
        font.setPointSize(self.settings.get("font_size", 14))
        self.text_label.setFont(font)
        
        # 直接使用传入的background_color，它现在是带有alpha通道的rgba字符串
        bg_color = self.settings.get("background_color", "rgba(0,0,0,0.7)")
        font_color = self.settings.get("font_color", "#FFFFFF")
        self.text_label.setStyleSheet(f'''
            background-color: {bg_color};
            color: {font_color};
            padding: 10px; border-radius: 5px;
        ''')

        # --- 布局 ---
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.text_label)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- 信号连接 ---
        self.toggle_visibility_signal.connect(self.toggle_visibility)
        self.close_signal.connect(self.close)

        # --- 初始化 ---
        self._drag_start_position = None
        self.update_display()
        self.start_hotkey_listener()

    def update_display(self):
        """根据当前字符索引，从完整字符串中切片、排版并显示内容"""
        page_content = self.full_content[self.current_char_index : self.current_char_index + self.page_char_count]
        
        if not page_content:
            self.text_label.setText("(已到末尾)")
            return

        chars_per_line = self.settings.get("chars_per_line", 40)
        lines = [page_content[i:i+chars_per_line] for i in range(0, len(page_content), chars_per_line)]
        
        self.text_label.setText("\n".join(lines))

    def next_page(self):
        next_index = self.current_char_index + self.page_char_count
        if next_index < len(self.full_content):
            self.current_char_index = next_index
            self.update_display()

    def prev_page(self):
        prev_index = self.current_char_index - self.page_char_count
        if prev_index >= 0:
            self.current_char_index = prev_index
            self.update_display()

    def start_hotkey_listener(self):
        minimize_hotkey_str = self.settings.get("minimize_hotkey", "<ctrl>+m")
        close_hotkey_str = self.settings.get("close_hotkey", "<alt>+q")
        def on_minimize(): self.toggle_visibility_signal.emit()
        def on_close(): self.close_signal.emit()
        hotkeys = {minimize_hotkey_str: on_minimize, close_hotkey_str: on_close}
        def start_listener():
            self.hotkey_listener = keyboard.GlobalHotKeys(hotkeys)
            self.hotkey_listener.run()
        listener_thread = Thread(target=start_listener, daemon=True)
        listener_thread.start()

    @Slot()
    def toggle_visibility(self):
        if self.isVisible(): self.hide()
        else: self.show()

    def keyPressEvent(self, event: QKeyEvent):
        paging_style = self.settings.get("paging_hotkey", "← 和 →")
        if paging_style == "← 和 →":
            if event.key() == Qt.Key_Right: self.next_page()
            elif event.key() == Qt.Key_Left: self.prev_page()
        elif paging_style == "A 和 D":
            if event.key() == Qt.Key_D: self.next_page()
            elif event.key() == Qt.Key_A: self.prev_page()

    def showEvent(self, event: QKeyEvent):
        """窗口显示时，强制刷新尺寸和布局。"""
        super().showEvent(event)
        # 强制让窗口根据内容调整一次尺寸，这通常能解决初次显示的布局问题
        self.adjustSize()
        self.updateGeometry()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # 检查鼠标点击位置是否在text_label的有效区域内
            if self.text_label.geometry().contains(event.pos()):
                self._drag_start_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
            else:
                event.ignore() # 忽略事件，让它穿透

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and self._drag_start_position:
            self.move(event.globalPosition().toPoint() - self._drag_start_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_start_position = None
        event.accept()

    def closeEvent(self, event):
        if self.hotkey_listener: self.hotkey_listener.stop()
        self.closed.emit(self.settings.get("selected_book", ""), self.current_char_index)
        self.deleteLater()
        event.accept()