# -*- coding: UTF-8 -*-
# author：abbkirito
from flask import Flask, jsonify
import requests
from flask_cors import CORS  # 需安装：pip install flask-cors

app = Flask(__name__)
CORS(app)  # 允许所有跨域请求（解决前端跨域问题）

def getdata(name):
    try:
        # 调用第三方 GitHub 贡献 API
        response = requests.get(f"https://github-contributions-api.jogruber.de/v4/{name}")
        data = response.json()
        
        # 提取 total 和 contributions（扁平数组）
        total = data.get("total", 0)
        contributions = data.get("contributions", [])  # 已经是扁平数组
        
        # 确保每个条目包含 date 和 count（第三方 API 已包含）
        flat_contributions = [
            {"date": item["date"], "count": item["count"]}
            for item in contributions
        ]
        
        # 返回插件可能期望的格式（包含 total 和扁平 contributions）
        return {
            "total": total,
            "contributions": flat_contributions
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
@app.route('/<username>/')
def get_calendar(username):
    data = getdata(username)
    return jsonify(data)
if __name__ == '__main__':
    app.run(debug=True)