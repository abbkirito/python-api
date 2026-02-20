# -*- coding: UTF-8 -*-
# api/index.py - GitHub Contributions API (flat array padded to multiple of 7)

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

def pad_to_weekly(data):
    """将扁平数组填充到长度为7的倍数，用未来日期的空数据填充"""
    if not data:
        return data
    remainder = len(data) % 7
    if remainder == 0:
        return data
    # 需要填充的天数
    pad_days = 7 - remainder
    # 获取最后一个日期
    last_date_str = data[-1]["date"]
    last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
    # 生成填充数据
    padded = data[:]
    for i in range(1, pad_days + 1):
        new_date = last_date + timedelta(days=i)
        padded.append({
            "date": new_date.strftime("%Y-%m-%d"),
            "count": 0
        })
    return padded

def getdata(name):
    try:
        url = f"https://github-contributions-api.jogruber.de/v4/{name}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # 提取扁平数组
        contributions = data.get("contributions", [])
        # 填充到7的倍数
        padded_contributions = pad_to_weekly(contributions)
        return {
            "total": data.get("total", 0),
            "contributions": padded_contributions
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