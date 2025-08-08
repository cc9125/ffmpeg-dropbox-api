# FFmpeg Dropbox Audio Split API (Railway-ready)

A minimal Flask API that downloads an audio file from a Dropbox share link and splits it into fixed-length segments using ffmpeg.

## Deploy to Railway (Free)

1. Push this folder to your GitHub repo (e.g., `ffmpeg-dropbox-api-railway`)
2. Create a New Project on https://railway.app → Deploy from GitHub
3. It will auto-install `ffmpeg` via `nixpacks.toml` and run `python app.py`
4. After deploy, open `https://<your-app>.up.railway.app/` to see health JSON

> If you prefer Gunicorn: set Start Command to `gunicorn app:app --bind 0.0.0.0:$PORT`

## Health Check

GET `/` → should return:
```json
{"ok": true, "service": "ffmpeg-dropbox-api", "endpoints": ["/split-audio"]}
```

## API

POST `/split-audio`
```json
{
  "url": "https://www.dropbox.com/s/<id>/meeting.wav?dl=0",
  "segment_time": 60,
  "format": "wav" // optional, wav/mp3/m4a
}
```

### cURL
```bash
curl -X POST https://<your-app>.up.railway.app/split-audio   -H "Content-Type: application/json"   -d '{ "url": "https://www.dropbox.com/s/xxxxx/meeting.wav?dl=0", "segment_time": 60 }'
```

## Notes

- Uses `/tmp` for working files. Railway ephemeral storage is fine for short jobs.
- If stream copy fails, it falls back to re-encode for compatibility.
- Next step: in Make.com, call this API, then upload `/tmp/splits_*` files to Dropbox and continue to Whisper → merge → summarize → LINE.
