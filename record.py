import ffmpeg
import os
from datetime import datetime
import threading

RECORD_FOLDER = "recordings"
os.makedirs(RECORD_FOLDER, exist_ok=True)

record_process = None
FFMPEG_BIN = r"C:\ffmpeg\bin\ffmpeg.exe"  # path to ffmpeg.exe

VIDEO_DEVICE = "Integrated Camera"  # Replace with exact name from ffmpeg -list_devices
AUDIO_DEVICE = "Microphone (Realtek Audio)"  # Replace with exact name

def start_recording():
    global record_process

    if record_process is not None:
        return  # already recording

    filename = datetime.now().strftime("recording_%Y%m%d_%H%M%S.mp4")
    filepath = os.path.join(RECORD_FOLDER, filename)

    stream = (
        ffmpeg
        .input(f'video={VIDEO_DEVICE}:audio={AUDIO_DEVICE}', f='dshow')
        .output(
            filepath,
            vcodec='libx264',
            acodec='aac',
            preset='ultrafast',
            pix_fmt='yuv420p',
            movflags='+faststart',  # browser-friendly
            video_bitrate='2500k',
            audio_bitrate='128k'
        )
        .global_args('-loglevel', 'error')
        .overwrite_output()
    )

    def run():
        global record_process
        # Run using your FFmpeg binary
        record_process = stream.run_async(cmd=FFMPEG_BIN)
        record_process.wait()

    threading.Thread(target=run, daemon=True).start()


def stop_recording():
    global record_process
    if record_process:
        record_process.terminate()
        record_process = None


def is_recording():
    return record_process is not None