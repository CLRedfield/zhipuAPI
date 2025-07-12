import os
import sys
import json
import webview
import threading
from flask import Flask, render_template, request, Response
from zhipuai import ZhipuAI
from waitress import serve

def resource_path(relative_path):
    """ 获取资源的绝对路径, 适用于开发环境和 PyInstaller 打包环境 """
    try:
        # PyInstaller 创建的临时文件夹, 并将路径存储在 _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# 使用正确的路径初始化 Flask
app = Flask(
    __name__,
    template_folder=resource_path('templates'),
    static_folder=resource_path('static')
)

# 使用你的API Key
api_key = os.getenv("ZHIPUAI_API_KEY", "133e608f967247f285c297bdeeaed081.CXhxRhwuxtmafx78")
client = ZhipuAI(api_key=api_key)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])

    def generate():
        try:
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=messages,
                stream=True,
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        yield f"data: [DONE]\n\n"

    return Response(generate(), mimetype="text/event-stream")

def run_server():
    """在后台线程中运行 waitress 服务器"""
    serve(app, host="127.0.0.1", port=5000)

if __name__ == "__main__":
    # 在一个单独的线程中启动服务器
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # 创建并启动 webview 窗口
    webview.create_window(
        '智谱AI助手',
        'http://127.0.0.1:5000',
        width=800,
        height=700,
        resizable=True,
        text_select=True # 允许在窗口中选择文本
    )
    webview.start(debug=False)