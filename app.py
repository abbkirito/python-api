# -*- coding: UTF-8 -*-
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
    
    # 新的正则表达式（GitHub 2024+ 页面结构）
    # 匹配 data-date 和 contribution count
    datadatereg = re.compile(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d+)"')
    matches = datadatereg.findall(data)
    
    if not matches:
        # 备用方案：尝试旧版正则
        datadatereg = re.compile(r'data-date="(.*?)" data-level')
        datacountreg = re.compile(r'<span class="sr-only">(.*?) contribution')
        datadate = datadatereg.findall(data)
        datacount = datacountreg.findall(data)
        datacount = list(map(int, [0 if i == "No" else i for i in datacount]))
    else:
        datadate = [m[0] for m in matches]
        datacount = [int(m[1]) for m in matches]
    
    if not datadate:
        return {"error": "No data found", "html_snippet": data[:500]}
    
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