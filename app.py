from flask import Flask, request, jsonify
import os
import subprocess
import uuid

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return jsonify({"ok": True, "service": "ffmpeg-dropbox-api", "endpoints": ["/split-audio"]})

@app.route('/split-audio', methods=['POST'])
def split_audio():
    data = request.get_json(silent=True) or {}
    dropbox_url = data.get('url')
    segment_time = int(data.get('segment_time', 60))
    output_format = data.get('format', 'wav')  # wav/mp3/m4a, etc.

    if not dropbox_url or "dropbox.com" not in dropbox_url:
        return jsonify({"error": "Missing or invalid Dropbox share URL"}), 400

    # Convert Dropbox share URL to direct download URL
    dl_url = dropbox_url.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("?dl=0", "")

    work_id = uuid.uuid4().hex
    input_path = f"/tmp/input_{work_id}"
    output_dir = f"/tmp/splits_{work_id}"
    os.makedirs(output_dir, exist_ok=True)

    # Download file from Dropbox
    try:
        subprocess.run(["curl", "-L", dl_url, "-o", input_path], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to download from Dropbox", "detail": str(e)}), 500

    # Probe to detect audio stream and ensure readable by ffmpeg
    try:
        subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", input_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        return jsonify({"error": "ffprobe could not read the input file"}), 400

    # Ensure extension for output pattern
    ext = output_format.lower().strip(".")
    output_pattern = os.path.join(output_dir, f"segment-%03d.{ext}")

    # Try stream copy (fast). If fails, fallback to re-encode.
    def split_with_cmd(cmd):
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return None
        except subprocess.CalledProcessError as e:
            return e

    err = split_with_cmd([
        "ffmpeg", "-hide_banner", "-nostdin", "-y",
        "-i", input_path,
        "-f", "segment", "-segment_time", str(segment_time),
        "-c", "copy",
        output_pattern
    ])
    if err:
        audio_codec = "aac" if ext in ("mp3","m4a","aac") else "pcm_s16le"
        bitrate = "128k" if ext in ("mp3","m4a","aac") else None
        cmd = ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-i", input_path,
               "-f", "segment", "-segment_time", str(segment_time),
               "-map", "0:a:0", "-vn", "-c:a", audio_codec]
        if bitrate:
            cmd += ["-b:a", bitrate]
        cmd += [output_pattern]
        err2 = split_with_cmd(cmd)
        if err2:
            return jsonify({"error": "ffmpeg split failed", "detail": err2.stderr.decode(errors="ignore")[:4000]}), 500

    files = sorted(os.listdir(output_dir))
    segments = [f for f in files if f.startswith("segment-")]
    payload = {
        "status": "success",
        "count": len(segments),
        "segments": segments,
        "work_dir": output_dir
    }

    try:
        os.remove(input_path)
    except Exception:
        pass

    return jsonify(payload), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
