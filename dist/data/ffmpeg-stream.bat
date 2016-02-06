@echo Off
set rtmp_ip=%1
set stream_name=%2
TITLE Vietcodex.com - Broadcast live stream to server

ffmpeg  -rtbufsize 1500M -f dshow -r 10000/1001 -i video="screen-capture-recorder"  -framerate 30 -g 60 -qmax 10 -qmin 8 -vb 400k -preset veryfast -threads 0 -crf 18 -an -f flv rtmp://%rtmp_ip%/live/%stream_name% -loglevel 16