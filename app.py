# -*- coding: UTF-8 -*-
# api/index.py - GitHub Contributions API (符合插件源码要求)

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

def list_split(items, n):
    """将列表按每 n 个元素分割成子列表"""
    return [items[i:i + n] for i in range(0, len(items), n)]

def pad_to_53_weeks(contributions_flat):
    """
    将扁平贡献数组转换为插件期望的二维数组（53周，每周7天）
    如果不足53周，前面补空数据；如果最后一周不足7天，填充至7天。
    """
    # 先按7天分割
    weekly = list_split(contributions_flat, 7)
    # 确保有53周
    total_weeks = len(weekly)
    if total_weeks < 53:
        # 需要在前面补足缺失的周（用空数据）
        # 计算需要补充的周数
        need = 53 - total_weeks
        # 创建空周数据：每周7天，日期从最早日期往前推算
        if contributions_flat:
            first_date = datetime.strptime(contributions_flat[0]["date"], "%Y-%m-%d")
        else:
            # 如果没有数据，用当前日期
            first_date = datetime.now()
        empty_weeks = []
        for i in range(need):
            week_start = first_date - timedelta(weeks=need - i)  # 依次向前推
            week = []
            for j in range(7):
                date = week_start + timedelta(days=j)
                week.append({"date": date.strftime("%Y-%m-%d"), "count": 0})
            empty_weeks.append(week)
        weekly = empty_weeks + weekly
    # 如果最后一周不足7天，填充至7天
    if weekly[-1] and len(weekly[-1]) < 7:
        last_week = weekly[-1]
        pad_days = 7 - len(last_week)
        last_date = datetime.strptime(last_week[-1]["date"], "%Y-%m-%d")
        for i in range(1, pad_days + 1):
            new_date = last_date + timedelta(days=i)
            last_week.append({"date": new_date.strftime("%Y-%m-%d"), "count": 0})
    return weekly

def getdata(name):
    try:
        url = f"https://github-contributions-api.jogruber.de/v4/{name}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        total = data.get("total", 0)
        contributions_flat = data.get("contributions", [])
        # 转换为插件需要的53周二维数组
        weekly = pad_to_53_weeks(contributions_flat)
        return {
            "total": total,
            "contributions": weekly
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