---
name: video-transcribe
description: Transcribe speech from a video or audio file into text using a fast, lower-accuracy local model (faster-whisper "tiny"). Use this whenever the user uploads a video (.mp4, .mov, .mkv, .webm, .avi) or audio file (.mp3, .wav, .m4a, .aac, .flac, .ogg) and asks to transcribe it, get a transcript, get captions/subtitles, or extract what's said in it. Also trigger when the user says things like "transcribe this", "what does this video say", "turn this recording into text", or references transcribing a clip. Prefer this skill over trying to read media files directly — Claude cannot natively process audio/video, and this skill handles the full extract-and-transcribe pipeline locally.
---

# Video / Audio Transcription (tiny model)

Transcribe speech from a video or audio file to text. This skill runs everything
locally: it extracts the audio with `ffmpeg`, then transcribes it with
`faster-whisper` using the **`tiny`** model.

## Why the tiny model

The `tiny` model is the default on purpose. It transcribes much faster than
larger models, so even a 10–20 minute video finishes in a single pass without
hitting the bash execution time limit. Larger models (`small`, `base`) tend to
time out partway through and force awkward chunk-and-stitch workarounds.

The tradeoff is accuracy. The tiny model reliably gets the gist and most words
right, but makes occasional errors on:
- Proper nouns and names
- Technical terms, jargon, and acronyms (e.g. "AMPK" → "A&PK")
- Numbers spoken quickly

After transcribing, **skim the output and flag likely errors to the user**
rather than presenting it as perfect. If they need higher accuracy, mention they
can re-run with `--model base` or `--model small` (slower; may need the audio
split into chunks for long files).

## Workflow

1. **Locate the file.** It's usually under `/mnt/user-data/uploads/`. Confirm the
   path and check the duration so you can set expectations:
   ```bash
   ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "INPUT"
   ```

2. **Install dependencies** (faster-whisper; ffmpeg is usually preinstalled):
   ```bash
   pip install -q faster-whisper --break-system-packages
   ```

3. **Run the transcription script**, writing outputs to the outputs directory:
   ```bash
   python scripts/transcribe.py "INPUT" --outdir /mnt/user-data/outputs
   ```
   This produces two files:
   - `transcript.txt` — clean prose with paragraph breaks (best for reading)
   - `transcript_timestamped.txt` — one line per segment, prefixed `[MM:SS]`

   Both are written incrementally, so if anything interrupts the run the partial
   transcript is still on disk.

4. **Present the results.** Use the `present_files` tool to surface both files.
   Give a one-line summary of what the video is about, then **call out specific
   likely transcription errors** you noticed so the user can fix them if it
   matters for their use case.

## Notes

- The script defaults to the `tiny` model. Pass `--model base` or `--model small`
  for better accuracy. For long videos on a larger model, the run may exceed the
  time limit — in that case split the audio (e.g. `ffmpeg -ss`/`-t`) into chunks,
  transcribe each with a time offset, and stitch the results.
- For audio-only input the pipeline is identical; ffmpeg just re-encodes it.
- If the user wants subtitles, the timestamped file can be converted to SRT/VTT
  format on request.
- If `ffmpeg` is missing, install it with `apt-get install -y ffmpeg` (or tell the
  user to enable network access if the install is blocked).
