# -*- coding: UTF-8 -*-
# api/index.py - GitHub Contributions API for hexo-filter-gitcalendar

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # 允许所有跨域请求，解决浏览器 CORS 限制

def getdata(name):
    """从第三方 GitHub 贡献 API 获取数据并返回"""
    try:
        # 第三方 API 地址，返回的数据包含 total 和 contributions（扁平数组）
        url = f"https://github-contributions-api.jogruber.de/v4/{name}"
        # 设置超时，避免长时间阻塞
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()  # 如果状态码不是 200，抛出异常
        data = resp.json()
        return data
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def home():
    """API 根路径，返回使用说明"""
    return jsonify({
        "message": "GitHub Calendar API",
        "usage": [
            "/<username>  - 例如 /Sunrisepeak",
            "/api?username=<name>  - 标准查询参数",
            "/api?<name>  - 非标准查询参数（插件使用的格式）"
        ]
    })

@app.route('/<username>', strict_slashes=False)
def get_calendar_by_path(username):
    """处理路径参数，如 /Sunrisepeak"""
    return jsonify(getdata(username))

@app.route('/api', strict_slashes=False)
def get_calendar_by_query():
    """处理查询参数，兼容插件可能使用的两种格式"""
    # 1. 尝试获取标准参数 ?username=xxx
    username = request.args.get('username')
    if username:
        return jsonify(getdata(username))

    # 2. 尝试直接使用原始查询字符串（插件可能发送 ?Sunrisepeak）
    qs = request.query_string.decode('utf-8')
    if qs and '=' not in qs:
        # 查询字符串中不包含等号，将其整体作为用户名
        username = qs
        return jsonify(getdata(username))

    # 3. 没有提供用户名，返回错误
    return jsonify({"error": "Missing username parameter"}), 400

# Vercel 需要将 app 作为模块级变量导出
app = app