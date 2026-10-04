"""
app.py —— 计算器后端的"前台接待员"（入口文件）。

它把 calculator.py（算）和 database.py（存）串起来，通过 HTTP 接口对外服务。
前端只跟这个文件打交道。

对外提供的接口：
    POST   /api/calculate       计算表达式（并自动存历史）
    GET    /api/history         查询所有历史
    DELETE /api/history/<id>    删除指定 id 的历史
    DELETE /api/history         清空全部历史（加分项）
    GET    /api/health          健康检查
"""

import os

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

# 把另两个文件"拉进来"一起用：
#   calculator 里的 calculate 函数和 CalculationError 错误类型
#   database   里的几个数据库函数
from calculator import calculate, CalculationError
import database

app = Flask(__name__)

# 只允许 API 接收小型 JSON 请求，避免意外的大请求占用资源。
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024


@app.errorhandler(413)
def request_too_large(_error):
    """Keep oversized request errors consistent with the rest of the JSON API."""
    return jsonify({"success": False, "message": "请求体过大"}), 413


@app.errorhandler(HTTPException)
def api_http_error(error):
    """让 API 的 404、405 等错误也保持 JSON 格式。"""
    if not request.path.startswith("/api/"):
        return error
    message_by_status = {
        404: "接口不存在",
        405: "请求方法不支持",
    }
    message = message_by_status.get(error.code, error.name)
    return jsonify({"success": False, "message": message}), error.code


@app.errorhandler(Exception)
def api_unexpected_error(error):
    """记录服务端异常，并避免 API 把 HTML 错误页返回给 Android。"""
    app.logger.exception("未处理的 API 异常")
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "message": "服务器内部错误"}), 500
    raise error

# 启动时建表（表不存在才建，重复执行也安全）
database.init_db()


@app.route("/api/health", methods=["GET"])
def health():
    """健康检查：确认后端还活着。"""
    return jsonify({"status": "ok"})


@app.route("/api/calculate", methods=["POST"])
def calculate_endpoint():
    """计算接口。前端发 {"expression": "1+2"}，我们算好并返回结果。"""
    # 1. 读取前端发来的 JSON。request.get_json 把 JSON 文本解析成字典
    data = request.get_json(silent=True)

    # 2. 输入校验：没发 JSON、或缺少 expression 字段，返回 400（请求错误）
    if data is None or "expression" not in data:
        return jsonify({"success": False, "message": "请求体需要包含 expression 字段"}), 400

    expression = data["expression"]
    if not isinstance(expression, str):
        return jsonify({"success": False, "message": "expression 必须是字符串"}), 400

    # 3. 调用计算器。出错就返回 400 和原因（如"不能除以 0"）
    try:
        result = calculate(expression)
    except CalculationError as e:
        return jsonify({"success": False, "message": str(e)}), 400

    # 4. 计算成功，存入历史数据库
    database.add_history(expression, result)

    # 5. 把结果返回给前端
    return jsonify({"success": True, "expression": expression, "result": result})


@app.route("/api/history", methods=["GET"])
def history_endpoint():
    """查询历史接口。返回所有历史（新的在前）。"""
    return jsonify({"success": True, "history": database.get_history()})


@app.route("/api/history/<int:history_id>", methods=["DELETE"])
def delete_history_endpoint(history_id):
    """删除一条历史。路径里的 <int:history_id> 会被 Flask 自动转成整数。"""
    if not database.delete_history(history_id):
        return jsonify({"success": False, "message": "历史记录不存在"}), 404
    return jsonify({"success": True, "message": "已删除"})


@app.route("/api/history", methods=["DELETE"])
def clear_history_endpoint():
    """清空全部历史（加分项）。"""
    database.clear_history()
    return jsonify({"success": True, "message": "已清空"})


if __name__ == "__main__":
    # host="0.0.0.0" 表示监听所有网络接口，这样手机/模拟器才能连上它
    # （如果是 127.0.0.1，就只有本机能访问，手机连不到）
    app.run(
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
    )
