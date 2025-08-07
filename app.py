from flask import Flask, request, jsonify
import os
import subprocess
import uuid

app = Flask(__name__)

@app.route('/split-audio', methods=['POST'])
def split_audio():
    data = request.get_json()
    dropbox_url = data.get('url')
    segment_time = int(data.get('segment_time', 60))

    if not dropbox_url or not dropbox_url.startswith("https://www.dropbox.com"):
        return jsonify({"error": "Missing or invalid Dropbox share URL"}), 400

    # Convert Dropbox share URL to direct download URL
    dl_url = dropbox_url.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("?dl=0", "")

    # Generate unique working directory
    work_id = uuid.uuid4().hex
    input_file = f"/tmp/audio_{work_id}.wav"
    output_dir = f"/tmp/splits_{work_id}"
    os.makedirs(output_dir, exist_ok=True)

    # Download file from Dropbox
    subprocess.run(["curl", "-L", dl_url, "-o", input_file], check=True)

    # Split with ffmpeg
    output_pattern = os.path.join(output_dir, "segment-%03d.wav")
    subprocess.run([
        "ffmpeg", "-i", input_file,
        "-f", "segment", "-segment_time", str(segment_time),
        "-c", "copy", output_pattern
    ], check=True)

    # List output segments
    segments = sorted(os.listdir(output_dir))
    result = [f"segment: {name}" for name in segments]

    # Clean up input file
    os.remove(input_file)

    return jsonify({
        "status": "success",
        "segments": result
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))