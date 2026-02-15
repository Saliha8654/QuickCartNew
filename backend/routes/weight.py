from flask import Blueprint, request, jsonify
weight_bp = Blueprint("weight", __name__)
@weight_bp.post("/weight/verify")
def verify_weight():
    body = request.get_json(force=True)
    weight_g = float(body.get("weight_g", 0))
    expected_g = float(body.get("expected_g", 0))
    tolerance = float(body.get("tolerance", 0.1))
    lower = expected_g * (1 - tolerance)
    upper = expected_g * (1 + tolerance)
    ok = lower <= weight_g <= upper
    return jsonify({"ok": ok, "expected": expected_g, "measured": weight_g, "lower": lower, "upper": upper})
