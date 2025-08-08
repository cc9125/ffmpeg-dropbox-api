# FFmpeg Dropbox Audio Split API (Railway-ready, with ffmpeg + Python)

This repo is configured for Railway using Nixpacks and explicitly installs Python 3.11 + pip + ffmpeg.

## Deploy to Railway (Free)

1. Push this folder to your GitHub repo
2. Railway → New Project → Deploy from GitHub
3. It will auto-install Python & ffmpeg via `nixpacks.toml`
4. After deploy, open `https://<your-app>.up.railway.app/` to see health JSON

## Health

GET `/` → `{"ok": true, "service": "ffmpeg-dropbox-api", "endpoints": ["/split-audio"]}`

## API

POST `/split-audio`
```
{
  "url": "https://www.dropbox.com/s/<id>/meeting.wav?dl=0",
  "segment_time": 60,
  "format": "wav"  // optional
}
```

### cURL
```
curl -X POST https://<your-app>.up.railway.app/split-audio   -H "Content-Type: application/json"   -d '{ "url": "https://www.dropbox.com/s/xxxxx/meeting.wav?dl=0", "segment_time": 60 }'
```

## Notes

- Uses `/tmp` for working files (ephemeral)
- Falls back to re-encode if stream copy fails
- Start command uses Gunicorn
