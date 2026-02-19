# -*- coding: UTF-8 -*-
# api/index.py - GitHub Contributions API for hexo-filter-gitcalendar (with weekly split)

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # 允许所有跨域请求

def list_split(items, n):
    """将列表按每 n 个元素分割成子列表"""
    return [items[i:i + n] for i in range(0, len(items), n)]

def getdata(name):
    """获取 GitHub 贡献数据并转换为插件需要的格式"""
    try:
        url = f"https://github-contributions-api.jogruber.de/v4/{name}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        total = data.get("total", 0)
        days = data.get("contributions", [])
        
        # 统一转换为 {date, count} 格式
        datalist = []
        for day in days:
            datalist.append({
                "date": day.get("date"),
                "count": day.get("count", 0)
            })
        
        # 按周分割（每7天一组）
        weekly = list_split(datalist, 7)
        
        return {
            "total": total,
            "contributions": weekly
        }
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
        username = qs
        return jsonify(getdata(username))

    # 3. 没有提供用户名，返回错误
    return jsonify({"error": "Missing username parameter"}), 400

# Vercel 需要将 app 作为模块级变量导出
app = app