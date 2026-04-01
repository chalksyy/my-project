#!/usr/bin/env python3
"""Ubuntu 后台划词翻译工具。

运行后常驻系统托盘：
1. 在任意应用中选中英文单词或句子并复制（通常 Ctrl+C）。
2. 按快捷键 Ctrl+Alt+T。
3. 弹窗展示中文翻译。

依赖：
    pip install PyQt5 pynput requests
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Optional

import requests
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QInputDialog,
    QMenu,
    QMessageBox,
    QSystemTrayIcon,
)
from pynput import keyboard


@dataclass
class Config:
    """应用配置。"""

    source_lang: str = "en"
    target_lang: str = "zh"
    api_url: str = "https://libretranslate.com/translate"
    timeout: int = 8


class Translator:
    """翻译服务封装。"""

    def __init__(self, config: Config):
        self.config = config

    def translate(self, text: str) -> str:
        payload = {
            "q": text,
            "source": self.config.source_lang,
            "target": self.config.target_lang,
            "format": "text",
        }
        response = requests.post(
            self.config.api_url,
            json=payload,
            timeout=self.config.timeout,
        )
        response.raise_for_status()
        data = response.json()

        translated = data.get("translatedText")
        if not translated:
            raise ValueError("翻译结果为空，可能是接口返回异常。")
        return translated


class TrayApp:
    """系统托盘应用。"""

    def __init__(self):
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setQuitOnLastWindowClosed(False)

        self.config = Config()
        self.translator = Translator(self.config)

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon.fromTheme("accessories-dictionary"))
        self.tray.setToolTip("划词翻译助手（Ctrl+Alt+T）")

        self._build_menu()
        self.listener: Optional[keyboard.Listener] = None
        self.hotkey: Optional[keyboard.GlobalHotKeys] = None

    def _build_menu(self) -> None:
        menu = QMenu()

        translate_action = QAction("立即翻译剪贴板", menu)
        translate_action.triggered.connect(self.translate_clipboard)
        menu.addAction(translate_action)

        api_action = QAction("设置翻译 API 地址", menu)
        api_action.triggered.connect(self.set_api_url)
        menu.addAction(api_action)

        menu.addSeparator()

        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(self.quit)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)

    def set_api_url(self) -> None:
        new_url, ok = QInputDialog.getText(
            None,
            "设置 API 地址",
            "请输入 LibreTranslate API 地址：",
            text=self.config.api_url,
        )
        if ok and new_url.strip():
            self.config.api_url = new_url.strip()
            self.tray.showMessage("配置更新", f"API 已更新为：{self.config.api_url}")

    def _read_clipboard_text(self) -> str:
        clipboard = self.qt_app.clipboard()
        text = clipboard.text().strip()
        if not text:
            raise ValueError("剪贴板为空。请先选中文本并复制（Ctrl+C）。")
        return text

    def _show_translation(self, original: str, translated: str) -> None:
        QMessageBox.information(
            None,
            "翻译结果",
            f"原文：\n{original}\n\n译文：\n{translated}",
        )

    def translate_clipboard(self) -> None:
        try:
            text = self._read_clipboard_text()
            translated = self.translator.translate(text)
            self._show_translation(text, translated)
        except Exception as exc:  # 运行期异常统一提示，避免后台直接崩溃
            self.tray.showMessage("翻译失败", str(exc), QSystemTrayIcon.Warning)

    def _trigger_translate(self) -> None:
        # 将翻译调用切换回 Qt 主线程执行
        QTimer.singleShot(0, self.translate_clipboard)

    def _start_hotkey(self) -> None:
        self.hotkey = keyboard.GlobalHotKeys({"<ctrl>+<alt>+t": self._trigger_translate})
        self.hotkey.start()

    def run(self) -> int:
        self._start_hotkey()
        self.tray.show()
        self.tray.showMessage(
            "划词翻译助手已启动",
            "选中英文文本后复制，再按 Ctrl+Alt+T 查看中文翻译。",
        )
        return self.qt_app.exec_()

    def quit(self) -> None:
        if self.hotkey is not None:
            self.hotkey.stop()
        self.tray.hide()
        self.qt_app.quit()


if __name__ == "__main__":
    app = TrayApp()
    sys.exit(app.run())
