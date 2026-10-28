#!/bin/sh
# Loudness of the delivered (AAC) file: integrated LUFS + true peak
ffmpeg -hide_banner -nostats -i "$1" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:)" | tail -2
