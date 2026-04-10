from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS
import tracking_engine
from database import (get_recent_violations, get_stats, get_all_violations,
                       authenticate_user, validate_token, logout_token,
                       get_all_users, add_user, delete_user)
import os, glob, csv, yaml, time

app = Flask(__name__)
CORS(app)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ───── Auth Helpers ─────
def require_auth():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return validate_token(auth_header[7:])
    return None

def require_admin():
    user = require_auth()
    if user and user['role'] == 'admin':
        return user
    return None

# ───── Auth Endpoints ─────
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    result = authenticate_user(email, password)
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Invalid email or password"}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        logout_token(auth_header[7:])
    return jsonify({"status": "success"}), 200

@app.route('/api/auth/me', methods=['GET'])
def auth_me():
    user = require_auth()
    if user:
        return jsonify(user), 200
    return jsonify({"error": "Not authenticated"}), 401

# ───── User Management (Admin Only) ─────
@app.route('/api/users', methods=['GET'])
def list_users():
    if not require_admin():
        return jsonify({"error": "Admin access required"}), 403
    return jsonify(get_all_users()), 200

@app.route('/api/users', methods=['POST'])
def create_user():
    if not require_admin():
        return jsonify({"error": "Admin access required"}), 403
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    name = data.get('name', '').strip()
    role = data.get('role', 'viewer')
    if not email or not password or not name:
        return jsonify({"error": "Email, password, and name are required"}), 400
    if len(password) < 4:
        return jsonify({"error": "Password must be at least 4 characters"}), 400
    success = add_user(email, password, name, role)
    if success:
        return jsonify({"status": "success", "message": f"User {email} created"}), 201
    return jsonify({"error": "A user with that email already exists"}), 409

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def remove_user(user_id):
    if not require_admin():
        return jsonify({"error": "Admin access required"}), 403
    success = delete_user(user_id)
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"error": "Cannot delete the last admin account"}), 400

# ───── Multi-Camera Endpoints ─────
@app.route('/video_feed/<cam_id>')
def video_feed_cam(cam_id):
    if cam_id not in ['cam1', 'cam2', 'cam3', 'cam4']:
        return "Invalid camera ID", 400
    cam = tracking_engine.get_camera(cam_id)
    return Response(cam.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed')
def video_feed():
    """Legacy endpoint — serves cam1."""
    cam = tracking_engine.get_camera('cam1')
    return Response(cam.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/cameras', methods=['GET'])
def cameras_status():
    return jsonify(tracking_engine.get_all_camera_statuses()), 200

@app.route('/api/set_source', methods=['POST'])
def update_source():
    data = request.json
    cam_id = data.get('cam_id', 'cam1')
    source = data.get('source')
    if cam_id not in ['cam1', 'cam2', 'cam3', 'cam4']:
        return jsonify({"status": "error", "message": "Invalid camera ID"}), 400
    if source is not None:
        cam = tracking_engine.get_camera(cam_id)
        success = cam.set_source(source)
        if success:
            return jsonify({"status": "success", "message": f"{cam_id} connected to {source}"}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to open video source."}), 400
    return jsonify({"status": "error", "message": "No source provided"}), 400

@app.route('/api/toggle_detection', methods=['POST'])
def toggle_detection():
    data = request.json
    cam_id = data.get('cam_id', 'cam1')
    state = data.get('state', False)
    if cam_id not in ['cam1', 'cam2', 'cam3', 'cam4']:
        return jsonify({"status": "error", "message": "Invalid camera ID"}), 400
    cam = tracking_engine.get_camera(cam_id)
    cam.is_detecting = state
    return jsonify({"status": "success", "detecting": state}), 200

@app.route('/api/cameras/<cam_id>/disconnect', methods=['POST'])
def disconnect_camera(cam_id):
    if cam_id not in ['cam1', 'cam2', 'cam3', 'cam4']:
        return jsonify({"status": "error"}), 400
    cam = tracking_engine.get_camera(cam_id)
    cam.disconnect()
    return jsonify({"status": "success", "message": f"{cam_id} disconnected"}), 200

# ───── Stats & Logs ─────
@app.route('/api/stats', methods=['GET'])
def stats():
    try:
        return jsonify(get_stats()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def logs():
    try:
        limit = request.args.get('limit', default=10, type=int)
        return jsonify(get_recent_violations(limit=limit)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs/all', methods=['GET'])
def logs_all():
    try:
        return jsonify(get_all_violations()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs', methods=['DELETE'])
def clear_logs():
    from database import delete_all_violations
    try:
        delete_all_violations()
        snapshot_dir = os.path.join(os.path.dirname(__file__), 'snapshots')
        files = glob.glob(os.path.join(snapshot_dir, '*.jpg'))
        for f in files: os.remove(f)
        return jsonify({"status": "success", "message": "All data cleared"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ───── Settings ─────
@app.route('/api/settings', methods=['GET'])
def get_settings():
    return jsonify({
        "confidence": tracking_engine.CONFIDENCE_THRESHOLD,
        "audio_alerts": tracking_engine.AUDIO_ALARMS_ENABLED
    })

@app.route('/api/settings', methods=['POST'])
def update_settings():
    data = request.json
    if 'confidence' in data:
        tracking_engine.CONFIDENCE_THRESHOLD = float(data['confidence'])
    if 'audio_alerts' in data:
        tracking_engine.AUDIO_ALARMS_ENABLED = bool(data['audio_alerts'])
    return jsonify({"status": "success"})

# ───── Status ─────
@app.route('/api/status', methods=['GET'])
def get_status():
    alarm_active = False
    if tracking_engine.AUDIO_ALARMS_ENABLED:
        if time.time() - tracking_engine.last_alarm_time < 2:
            alarm_active = True

    from database import DB_PATH
    db_size = "Unknown"
    if os.path.exists(DB_PATH):
        db_size = f"{os.path.getsize(DB_PATH) / 1024:.1f} KB"

    latest = None
    try:
        recent = get_recent_violations(limit=1)
        if recent:
            latest = recent[0]
    except:
        pass

    return jsonify({
        "alarm": alarm_active,
        "latest_violation": latest,
        "diagnostics": {
            "model": "YOLOv8s",
            "db_size": db_size,
            "server": "localhost:5000"
        }
    })

# ───── Model Performance Endpoints ─────
@app.route('/api/model/metrics', methods=['GET'])
def model_metrics():
    """Parse results.csv and return training metrics as JSON."""
    csv_path = os.path.join(PROJECT_ROOT, 'runs', 'detect', 'yolov8s_model', 'results.csv')
    if not os.path.exists(csv_path):
        return jsonify({"error": "results.csv not found"}), 404

    import math
    metrics = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned = {}
            for k, v in row.items():
                key = k.strip()
                try:
                    val = float(v.strip())
                    # Replace Infinity and NaN with None (becomes null in JSON)
                    cleaned[key] = None if (math.isinf(val) or math.isnan(val)) else round(val, 4)
                except:
                    cleaned[key] = v.strip()
            metrics.append(cleaned)
    return jsonify(metrics), 200

@app.route('/api/model/config', methods=['GET'])
def model_config():
    """Parse args.yaml and return training config."""
    yaml_path = os.path.join(PROJECT_ROOT, 'runs', 'detect', 'yolov8s_model', 'args.yaml')
    if not os.path.exists(yaml_path):
        return jsonify({"error": "args.yaml not found"}), 404

    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    return jsonify(config), 200

@app.route('/model_assets/<path:filename>')
def serve_model_asset(filename):
    """Serve training images (confusion matrix, curves, etc.)."""
    asset_dir = os.path.join(PROJECT_ROOT, 'runs', 'detect', 'yolov8s_model')
    return send_from_directory(asset_dir, filename)

# ───── Snapshots ─────
@app.route('/snapshots/<path:filename>')
def serve_snapshot(filename):
    snapshot_dir = os.path.join(os.path.dirname(__file__), 'snapshots')
    return send_from_directory(snapshot_dir, filename)

if __name__ == '__main__':
    print("[INFO] Starting Flask Server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
