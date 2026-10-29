#!/bin/sh
# Trim silence and brighten a TTS line: voice_fx.sh in.mp3 out.wav [bright|calm]
# -nostdin matters: inside a `while read` loop ffmpeg otherwise eats stdin and the next line loses its first letter.
MODE=${3:-bright}
if [ "$MODE" = calm ]; then FX=""; else FX=",highshelf=f=4500:g=3.5,equalizer=f=220:t=q:w=1:g=-2,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2"; fi
ffmpeg -nostdin -y -loglevel error -i "$1" -af "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse$FX" -ar 48000 -ac 2 "$2"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$2"
