# -*- coding: UTF-8 -*-
# api/index.py - GitHub Contributions API (参考代码格式)

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

def list_split(items, n):
    """将列表按每n个元素分割成子列表"""
    return [items[i:i + n] for i in range(0, len(items), n)]

def getdata(name):
    """获取GitHub贡献数据，返回与参考代码完全相同的格式"""
    try:
        # 使用第三方API获取数据
        url = f"https://github-contributions-api.jogruber.de/v4/{name}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        # 获取总贡献数
        total = data.get("total", 0)
        # 获取贡献数组（扁平对象数组）
        days = data.get("contributions", [])
        
        # 转换为 {date, count} 格式（第三方API已经符合）
        datalist = [{"date": day["date"], "count": day["count"]} for day in days]
        
        # 按周分割（每7天一组）
        weekly = list_split(datalist, 7)
        
        # 返回与参考代码一致的结构
        return {
            "total": total,
            "contributions": weekly
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}

@app.route('/', strict_slashes=False)
def home():
    """根路径返回使用说明（与参考代码一致）"""
    return jsonify({
        "message": "GitHub Calendar API",
        "usage": "/?username 获取用户贡献数据，例如 /?Sunrisepeak"
    })

@app.route('/api', strict_slashes=False)
@app.route('/', strict_slashes=False)  # 同时支持根路径加查询参数
def get_calendar():
    """处理查询参数，支持 /?username 和 /api?username 格式"""
    # 获取查询字符串中的参数
    username = request.args.get('username')
    if not username:
        # 如果没有username参数，尝试将整个查询字符串作为用户名（如 ?Sunrisepeak）
        qs = request.query_string.decode('utf-8')
        if qs and '=' not in qs:
            username = qs
    if not username:
        return jsonify({"error": "Missing username parameter"}), 400
    
    data = getdata(username)
    return jsonify(data)

# 为了兼容可能使用路径参数的旧配置，保留一个可选的路由
@app.route('/<username>', strict_slashes=False)
def get_calendar_by_path(username):
    """处理路径参数，如 /Sunrisepeak（返回相同格式）"""
    data = getdata(username)
    return jsonify(data)

# Vercel需要
app = app