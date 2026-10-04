"""Flask entry point for the calculator backend.

Exposes a JSON HTTP API:
    POST   /api/calculate       evaluate an expression and store it in history
    GET    /api/history         list history, newest first
    DELETE /api/history/<id>    delete one history record
    DELETE /api/history         clear all history
    GET    /api/health          health check
"""

import os

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from calculator import calculate, CalculationError
import database

app = Flask(__name__)

# Reject oversized JSON bodies early.
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024


@app.errorhandler(413)
def request_too_large(_error):
    """Keep 413 responses consistent with the JSON API shape."""
    return jsonify({"success": False, "message": "Request body too large"}), 413


@app.errorhandler(HTTPException)
def api_http_error(error):
    """Return JSON for 404/405 instead of the default HTML error pages."""
    if not request.path.startswith("/api/"):
        return error
    message_by_status = {
        404: "Endpoint not found",
        405: "Method not allowed",
    }
    message = message_by_status.get(error.code, error.name)
    return jsonify({"success": False, "message": message}), error.code


@app.errorhandler(Exception)
def api_unexpected_error(error):
    """Log unexpected errors and keep API responses JSON-shaped."""
    app.logger.exception("Unhandled API exception")
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "message": "Internal server error"}), 500
    raise error


# Create the history table on startup (idempotent).
database.init_db()


@app.route("/api/health", methods=["GET"])
def health():
    """Health check used by the client and the deployment platform."""
    return jsonify({"status": "ok"})


@app.route("/api/calculate", methods=["POST"])
def calculate_endpoint():
    """Evaluate the expression in the JSON body and store successful results."""
    data = request.get_json(silent=True)

    if data is None or "expression" not in data:
        return jsonify({"success": False, "message": "Request body must contain an expression field"}), 400

    expression = data["expression"]
    if not isinstance(expression, str):
        return jsonify({"success": False, "message": "expression must be a string"}), 400

    try:
        result = calculate(expression)
    except CalculationError as e:
        return jsonify({"success": False, "message": str(e)}), 400

    database.add_history(expression, result)

    return jsonify({"success": True, "expression": expression, "result": result})


@app.route("/api/history", methods=["GET"])
def history_endpoint():
    """Return all history records, newest first."""
    return jsonify({"success": True, "history": database.get_history()})


@app.route("/api/history/<int:history_id>", methods=["DELETE"])
def delete_history_endpoint(history_id):
    """Delete the history record with the given id."""
    if not database.delete_history(history_id):
        return jsonify({"success": False, "message": "History record not found"}), 404
    return jsonify({"success": True, "message": "Deleted"})


@app.route("/api/history", methods=["DELETE"])
def clear_history_endpoint():
    """Delete all history records."""
    database.clear_history()
    return jsonify({"success": True, "message": "Cleared"})


if __name__ == "__main__":
    # 0.0.0.0 exposes the server to the emulator/phone; 127.0.0.1 would not.
    app.run(
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
    )
