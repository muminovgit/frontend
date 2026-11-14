#!/bin/sh
# render each pilot in 4 parallel chunks (60 fps, 8 subframes), then concat -> raw-XX.mp4
S=/home/user/frontend/.claude/skills/brand-motion-reel/scripts
cd "$(dirname "$0")"
for spec in "01 516" "08 570" "02 594"; do set -- $spec; v=$1; n=$2; q=$((n/4))
  for i in 0 1 2 3; do a=$((i*q)); b=$(( i==3 ? n : (i+1)*q )); node $S/render.js ad-$v.html 1080 1920 $a $b part_${v}_$i.mp4 >/dev/null 2>>render.log & done; wait
  printf "file '%s'\n" part_${v}_0.mp4 part_${v}_1.mp4 part_${v}_2.mp4 part_${v}_3.mp4 > list_$v.txt
  ffmpeg -nostdin -y -loglevel error -f concat -safe 0 -i list_$v.txt -c copy raw-$v.mp4; echo "done $v"
done
