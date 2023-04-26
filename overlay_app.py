import sys
from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QComboBox, QPushButton, QWidget, QSizePolicy
import win32gui

class StartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.windows = []
    
    def initUI(self):
        self.setWindowTitle('Start Window')
        self.setGeometry(100, 100, 200, 200)
        
        # ウィンドウを選択するためのコンボボックス
        self.combobox = QComboBox(self)
        self.combobox.addItem('Select a window')
        self.combobox.addItems(self.get_window_list())

        # オーバーレイ実行ボタン
        self.btn_overlay = QPushButton('Launch', self)
        self.btn_overlay.clicked.connect(self.start_main_app)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.combobox)
        vbox.addWidget(self.btn_overlay)
        vbox.addStretch(1)
        self.setLayout(vbox)

    def start_main_app(self):
        combo_text = self.combobox.currentText()
        self.main_app = OverlayApp(combo_text)
        self.main_app.show()
        self.windows.append(self.main_app)

    def get_window_list(self):
        # ウィンドウのリストを取得する
        def enum_callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text:
                    results.append(window_text)

        results = []
        win32gui.EnumWindows(enum_callback, results)
        return results

    def closeEvent(self, event):
        if hasattr(self, 'main_app'):
            self.main_app.close()
        event.accept()
        
class OverlayApp(QWidget):
    def __init__(self, selected_window):
        super().__init__()
        self.selected_window = selected_window

        self.setWindowTitle('Overlay App')
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setGeometry(0, 0, 0, 0)
        
        # 閉じるボタン
        self.btn_close = QPushButton('x', self)
        self.btn_close.setGeometry(10, 10, 25, 25)
        self.btn_close.clicked.connect(self.close)

        # タイマーを設定して、選択されたウィンドウの位置とサイズを定期的に更新する
        self.update_timer = QtCore.QTimer(self)
        self.update_timer.timeout.connect(self.update_overlay_position)
        self.update_timer.start(100) # 100ミリ秒ごとに更新する
        # 選択されたウィンドウのハンドル
        self.selected_window_handle = None
        self.overlay()

    def closeEvent(self, event):
        # ウィンドウが閉じられたときに実行する処理を追加する
        print("OverlayApp closed")
        event.accept()

    def overlay(self):
        # 選択されたウィンドウのハンドルを取得する
        selected_window_text = self.selected_window
        def enum_callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text == selected_window_text:
                    results.append(hwnd)

        results = []
        win32gui.EnumWindows(enum_callback, results)
        if len(results) > 0:
            self.selected_window_handle = results[0]

            # ウィンドウの位置とサイズを更新する
            self.update_overlay_position()

    def update_overlay_position(self):
        if self.selected_window_handle is not None:
            # 選択されたウィンドウの位置とサイズを取得する
            rect = win32gui.GetWindowRect(self.selected_window_handle)
            x, y, w, h = rect
            # ウィンドウの位置とサイズを設定する
            self.setGeometry(x, y, w, h)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv) # アプリケーション作成
    start_window = StartWindow() # StartWindowオブジェクト作成
    start_window.show() # StartWindowの表示
    sys.exit(app.exec_())

