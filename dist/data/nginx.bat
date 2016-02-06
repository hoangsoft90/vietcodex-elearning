@echo Off
set arg1=%1
set cygwin_bin = E:/cygwin/bin
rem CD /D %cygwin_bin%
TITLE Vietcodex.com - Start nginx server

echo %cygwin_bin%

if '%arg1%'=='start' E:/cygwin/bin/nginx.exe
if '%arg1%'=='stop' E:/cygwin/bin/nginx.exe -s stop
