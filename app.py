# -*- coding: UTF-8 -*-
# api/index.py - GitHub Contributions API (flat array + total)

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

def getdata(name):
    """获取 GitHub 贡献数据，返回扁平数组 + total"""
    try:
        url = f"https://github-contributions-api.jogruber.de/v4/{name}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        total = data.get("total", 0)
        days = data.get("contributions", [])  # 第三方 API 返回的已经是扁平对象数组
        
        # 直接使用扁平数组，不进行分割
        return {
            "total": total,
            "contributions": days  # 一维数组，每个元素包含 date 和 count
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def home():
    return jsonify({
        "message": "GitHub Calendar API",
        "usage": "/?username 获取用户贡献数据，例如 /?Sunrisepeak"
    })

@app.route('/api', strict_slashes=False)
@app.route('/', strict_slashes=False)
def get_calendar():
    # 优先获取 username 参数
    username = request.args.get('username')
    if not username:
        qs = request.query_string.decode('utf-8')
        if qs and '=' not in qs:
            username = qs
    if not username:
        return jsonify({"error": "Missing username"}), 400
    
    return jsonify(getdata(username))

@app.route('/<username>', strict_slashes=False)
def get_calendar_by_path(username):
    return jsonify(getdata(username))

app = app