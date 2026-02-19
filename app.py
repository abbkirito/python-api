# -*- coding: UTF-8 -*- author：abbkirito
from flask import Flask, jsonify, request
import requests
import re

app = Flask(__name__)

def list_split(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]

def getdata(name):
    try:
        # 使用第三方 GitHub 贡献 API
        response = requests.get(f"https://github-contributions-api.jogruber.de/v4/{name}")
        data = response.json()
        
        # 解析返回的数据
        contributions = data.get("total", 0)
        days = data.get("contributions", [])
        
        # 转换为需要的格式
        datalist = []
        for day in days:
            itemlist = {
                "date": day.get("date"),
                "count": day.get("count", 0)
            }
            datalist.append(itemlist)
        
        datalistsplit = list_split(datalist, 7)
        
        return {
            "total": contributions,
            "contributions": datalistsplit
        }
    except Exception as e:
        return {"error": str(e)}
@app.route('/', strict_slashes=False)
def home():
    return jsonify({
        "message": "GitHub Calendar API",
        "usage": "/<username> 获取用户贡献数据，例如 /abbkirito"
    })

@app.route('/<username>')
def get_calendar(username):
    try:
        data = getdata(username)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e), "username": username}), 500

if __name__ == '__main__':
    app.run(debug=True)