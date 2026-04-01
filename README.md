# Ubuntu 划词翻译助手

这是一个适用于 Ubuntu 的后台翻译小工具。程序启动后常驻系统托盘，用户在任意应用中选中英文单词或句子并复制，然后按 `Ctrl+Alt+T`，即可弹出中文翻译。

## 功能

- 后台运行（系统托盘）
- 全局快捷键触发翻译：`Ctrl+Alt+T`
- 自动读取剪贴板文本
- 弹窗显示中文翻译结果
- 支持自定义 LibreTranslate API 地址

## 依赖安装

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install PyQt5 pynput requests
```

## 运行

```bash
python3 hello.py
```

启动后：
1. 选中英文文本并复制（`Ctrl+C`）。
2. 按 `Ctrl+Alt+T`。
3. 查看弹出的中文翻译。

## 说明

- 默认使用公开 LibreTranslate 接口：`https://libretranslate.com/translate`。
- 若接口不可用，可在托盘菜单中点击“设置翻译 API 地址”切换到你自己的服务地址。
