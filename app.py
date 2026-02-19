# -*- coding: UTF-8 -*-
from flask import Flask, jsonify, request
import requests
import re

app = Flask(__name__)

def list_split(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]

def getdata(name):
    gitpage = requests.get(f"https://github.com/{name}")
    data = gitpage.text
    datadatereg = re.compile(r'data-date="(.*?)" data-level')
    datacountreg = re.compile(r'<span class="sr-only">(.*?) contribution')
    datadate = datadatereg.findall(data)
    datacount = datacountreg.findall(data)
    datacount = list(map(int, [0 if i == "No" else i for i in datacount]))

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

@app.route('/')
def home():
    return jsonify({
        "message": "GitHub Calendar API",
        "usage": "/?user=username 或 /<username> 获取用户贡献数据"
    })

@app.route('/<username>')
def get_calendar(username):
    try:
        data = getdata(username)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)

