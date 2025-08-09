import sys
import os

project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(project_root)

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon # 新增导入
import qdarkstyle
from UI.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 设置应用程序图标
    # 确定打包后的资源基础路径
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe，使用 sys._MEIPASS
        base_path = sys._MEIPASS
    else:
        # 否则，使用当前文件所在目录
        base_path = project_root # 或者 os.path.abspath(os.path.dirname(__file__))

    app_icon_path = os.path.join(base_path, "resources", "book.png")
    app.setWindowIcon(QIcon(app_icon_path)) # 添加这一行
    app.setStyleSheet(qdarkstyle.load_stylesheet() + """
        QToolTip {
            background-color: #333333; /* 深灰色背景，与暗色主题协调 */
            color: white; /* 白色文字 */
            border: 1px solid #555555; /* 可选边框 */
        }
    """) # 应用QDarkStyle样式
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
