import os
import cv2
import numpy as np
import base64
import time
from flask import Flask, render_template, Response, jsonify, request, send_from_directory, send_file

app = Flask(__name__)

# --- CONFIGURATION ---
RECORD_FOLDER = "recordings"
if not os.path.exists(RECORD_FOLDER):
    os.makedirs(RECORD_FOLDER)

# Global states
recording = False
latest_frame = None
video_writer = None

# --- HELPERS ---
def get_video_filename():
    return os.path.join(RECORD_FOLDER, f"recording_{int(time.time())}.mp4")

# --- ROUTES ---

@app.route('/')
def home():
    return render_template("client.html")

@app.route('/upload_frame', methods=['POST'])
def upload_frame():
    global latest_frame, recording, video_writer
    try:
        data = request.json['image']
        encoded_data = data.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        latest_frame = frame  # Update the live feed

        # Handle Recording Logic
        if recording:
            if video_writer is None:
                # Initialize writer on first frame of recording
                height, width, _ = frame.shape
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(get_video_filename(), fourcc, 10.0, (width, height))
            
            video_writer.write(frame)
        else:
            if video_writer is not None:
                video_writer.release()
                video_writer = None

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/video')
def video():
    # Stream the latest frame received from the browser back to any viewers
    def stream():
        while True:
            if latest_frame is not None:
                ret, buffer = cv2.imencode('.jpg', latest_frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.1) # 10 FPS
    return Response(stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

# --- RECORDING CONTROL ---

@app.route('/start_recording')
def start_recording():
    global recording
    recording = True
    return jsonify({"status": "recording"})

@app.route('/stop_recording')
def stop_recording():
    global recording
    recording = False
    return jsonify({"status": "stopped"})

@app.route('/recording_status')
def recording_status():
    return jsonify({"recording": recording})

# --- FILE MANAGEMENT ---

@app.route('/recordings')
def list_recordings():
    files = sorted(os.listdir(RECORD_FOLDER), reverse=True)
    return render_template("recordings.html", files=files)

@app.route('/videos/<filename>')
def serve_video(filename):
    return send_from_directory(RECORD_FOLDER, filename)

@app.route('/delete/<filename>', methods=['POST'])
def delete_video(filename):
    path = os.path.join(RECORD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 404

if __name__ == '__main__':
    # For Render: Use the PORT env variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)