# FFmpeg Dropbox Audio Split API

This is a simple Flask API to split audio files from Dropbox using ffmpeg.

## 🧪 How it works

- Accepts a Dropbox share link
- Downloads the file
- Splits it into 60-second segments using ffmpeg
- Returns a list of split files

## 🛠 Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/oPuGyN?referrer=chatgpt)

## Example Request

```
POST /split-audio
Content-Type: application/json

{
  "url": "https://www.dropbox.com/s/xxxxx/meeting.wav?dl=0",
  "segment_time": 60
}
```