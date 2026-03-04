import cv2
import os
from datetime import datetime

RECORD_FOLDER = "recordings"
os.makedirs(RECORD_FOLDER, exist_ok=True)

def generate_frames(is_recording):

    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = None

    while True:
        success, frame = cap.read()
        if not success:
            break

        if is_recording():
            if out is None:
                filename = datetime.now().strftime("recording_%Y%m%d_%H%M%S.mp4")
                filepath = os.path.join(RECORD_FOLDER, filename)
                h, w, _ = frame.shape
                out = cv2.VideoWriter(filepath, fourcc, 20.0, (w, h))

            out.write(frame)

        else:
            if out:
                out.release()
                out = None

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()
    if out:
        out.release()