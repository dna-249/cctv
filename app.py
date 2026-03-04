from flask import Flask, render_template, Response, jsonify,  request,  send_file
import os
from flask import send_from_directory
# from server import server
from client import generate_frames
# import threading
import cv2
import numpy as np
import base64


app = Flask(__name__)

# Global recording state
recording = False

# Start socket server in background
# threading.Thread(target=server, daemon=True).start()


# Home page (video page)
@app.route('/')
def home():
    return render_template("client.html")


# Video streaming route
@app.route('/video')
def video():
    return Response(generate_frames(lambda: recording),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# Start recording
@app.route('/start_recording')
def start_recording():
    global recording
    recording = True
    return jsonify({"status": "recording"})


# Stop recording
@app.route('/stop_recording')
def stop_recording():
    global recording
    recording = False
    return jsonify({"status": "stopped"})


# Recording status (for blinking REC indicator)
@app.route('/recording_status')
def recording_status():
    return jsonify({"recording": recording})
RECORD_FOLDER = "recordings"

@app.route('/recordings')
def list_recordings():
    files = sorted(os.listdir(RECORD_FOLDER), reverse=True)
    return render_template("recordings.html", files=files)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(RECORD_FOLDER, filename)
RECORD_FOLDER = "recordings"

@app.route('/videos/<filename>')
def serve_video(filename):
    path = os.path.join("recordings", filename)
    return send_file(path, mimetype='video/mp4')

@app.route('/delete/<filename>', methods=['POST'])
def delete_video(filename):
    path = os.path.join(RECORD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
        return jsonify({"status": "success", "message": f"{filename} deleted"})
    else:
        return jsonify({"status": "error", "message": "File not found"}), 404
    
@app.route('/upload_frame', methods=['POST'])
def upload_frame():
    try:
        data = request.json['image']
        # Remove the header (data:image/jpeg;base64,)
        encoded_data = data.split(',')[1]
        
        # Convert base64 string to an OpenCV image
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # --- THIS IS WHERE YOUR CCTV LOGIC GOES ---
        # Example: Save a frame if motion is detected
        # cv2.imwrite("latest_capture.jpg", frame)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)