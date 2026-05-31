#!/usr/bin/env python3
"""
Transcribe a video or audio file using faster-whisper's "tiny" model.

The tiny model is chosen deliberately: it transcribes far faster than larger
models (typically many minutes of audio per wall-clock minute on CPU), so a
full-length video gets transcribed in a single pass without hitting execution
time limits. The tradeoff is lower accuracy — expect occasional errors on
proper nouns, technical terms, and acronyms.

Usage:
    python transcribe.py INPUT [--model tiny] [--outdir DIR]

Outputs two files into --outdir (default: current directory):
    transcript_timestamped.txt  - one line per segment, prefixed with [MM:SS]
    transcript.txt              - clean prose, paragraph breaks on pauses

Both files are written incrementally, so if the process is interrupted the
partial transcript is preserved.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile


def extract_audio(input_path, wav_path):
    """Extract mono 16 kHz PCM audio (what whisper expects) via ffmpeg."""
    cmd = [
        "ffmpeg", "-i", input_path,
        "-vn",                 # drop any video stream
        "-acodec", "pcm_s16le",
        "-ar", "16000",        # 16 kHz
        "-ac", "1",            # mono
        wav_path, "-y",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(result.stderr[-2000:] + "\n")
        raise RuntimeError(f"ffmpeg failed to extract audio from {input_path}")


def fmt_ts(seconds):
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"


def transcribe(input_path, model_size, outdir):
    from faster_whisper import WhisperModel

    os.makedirs(outdir, exist_ok=True)
    ts_path = os.path.join(outdir, "transcript_timestamped.txt")
    prose_path = os.path.join(outdir, "transcript.txt")

    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "audio.wav")
        sys.stderr.write("Extracting audio...\n")
        extract_audio(input_path, wav)

        sys.stderr.write(f"Loading '{model_size}' model...\n")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")

        sys.stderr.write("Transcribing (streaming output as it goes)...\n")
        # vad_filter trims silence, which speeds things up and reduces
        # hallucinated text during quiet stretches.
        segments, info = model.transcribe(wav, beam_size=5, vad_filter=True)
        sys.stderr.write(
            f"Detected language: {info.language} "
            f"(p={info.language_probability:.2f})\n"
        )

        # Stream to both files incrementally. Prose paragraphs break whenever
        # there's a gap of >=1.5s between segments (a natural pause) or the
        # running paragraph gets long.
        para = []
        prev_end = None
        with open(ts_path, "w") as f_ts, open(prose_path, "w") as f_prose:
            def flush_para():
                if para:
                    text = re.sub(r"\s+", " ", " ".join(para)).strip()
                    f_prose.write(text + "\n\n")
                    f_prose.flush()
                    para.clear()

            for seg in segments:
                line = f"[{fmt_ts(seg.start)}] {seg.text.strip()}"
                f_ts.write(line + "\n")
                f_ts.flush()

                gap = (seg.start - prev_end) if prev_end is not None else 0
                if (gap >= 1.5 and len(para) >= 3) or len(" ".join(para)) > 900:
                    flush_para()
                para.append(seg.text.strip())
                prev_end = seg.end

            flush_para()

    sys.stderr.write(f"\nWrote:\n  {ts_path}\n  {prose_path}\n")
    return ts_path, prose_path


def main():
    ap = argparse.ArgumentParser(description="Transcribe video/audio with faster-whisper tiny model.")
    ap.add_argument("input", help="Path to the video or audio file")
    ap.add_argument("--model", default="tiny",
                    help="Whisper model size (default: tiny). Use 'base'/'small' for more accuracy at the cost of speed.")
    ap.add_argument("--outdir", default=".", help="Output directory (default: current dir)")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        sys.exit(f"Input not found: {args.input}")

    transcribe(args.input, args.model, args.outdir)


if __name__ == "__main__":
    main()
