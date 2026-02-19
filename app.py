# -*- coding: UTF-8 -*- author：abbkirito
from flask import Flask, jsonify, request
import requests
import re

app = Flask(__name__)

def list_split(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]
def getdata(name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    gitpage = requests.get(f"https://github.com/{name}", headers=headers)
    data = gitpage.text
    
    # 新的正则表达式 - 匹配 GitHub 2024+ 的贡献图数据
    # 格式: data-date="YYYY-MM-DD" data-level="N"
    pattern = re.compile(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d+)"')
    matches = pattern.findall(data)
    
    if not matches:
        # 尝试另一种可能的格式
        pattern = re.compile(r'(\d{4}-\d{2}-\d{2})[^"]*"(\d+)"[^>]*contribution')
        matches = pattern.findall(data)
    
    if not matches:
        return {"error": "No contribution data found", "matches_count": 0}
    
    # 解析匹配结果
    datadate = [m[0] for m in matches]
    datacount = [int(m[1]) for m in matches]
    
    # 排序
    sorted_data = sorted(zip(datadate, datacount))
    datadate, datacount = zip(*sorted_data)
    
    contributions = sum(datacount)
    datalist = []
    for index, item in enumerate(datadate):
        itemlist = {"date": item, "count": datacount[index]}
        datalist.append(itemlist)
    datalistsplit = list_split(datalist, 7)
    
    return {
        "total": contributions,
        "contributions": datalistsplit
    }
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