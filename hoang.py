__author__ = 'Hoang'
from subprocess import check_output
import os
import subprocess
from subprocess import Popen, PIPE
from subprocess import call
from timeout import timeout
import errno,thread,re,socket
from PyQt4 import QtGui,QtCore
import myFuncs,data_rc
from customThread import *


"""
Vietcode class
"""
class vietcodex(QtCore.QObject):
    #mainWindown reference
    mainWin =None   #never in use
    t_monitor =None
    call_func_thread =None

    #set data transfer bride
    updateText = QtCore.pyqtSignal(str)
    invokeCallback = QtCore.pyqtSignal(object)

    #nginx http port
    nginx_http_port = "9080"
    localIP = ""    #local my ip

    def __init__(self):
        super(vietcodex, self).__init__()
        self.localIP = socket.gethostbyname(socket.gethostname())

    """
    call from first thread
    """
    def update_list(self,data,cb=None):
        def ham():
            self.updateText.emit(data)

        if hasattr(cb,'__call__') ==False:
            cb=ham

        #if self.t_monitor == None:
        self.t_monitor = myThread(ham, parent=self)
        #t_monitor = myThread(self.mainWindow_vector, parent=self)
        self.t_monitor.daemon = True
        self.t_monitor.setObjectName("monitor")
        #t_monitor.setName('monitor')
        self.t_monitor.start()

    """
    call from first thread
    """
    def call_func(self,cb=None):
        def ham():
            self.invokeCallback.emit(cb)

        #if self.t_monitor == None:
        self.call_func_thread = myThread(ham, parent=self)
        #t_monitor = myThread(self.mainWindow_vector, parent=self)
        self.call_func_thread.daemon = True
        self.call_func_thread.setObjectName("call_func")
        #t_monitor.setName('monitor')
        self.call_func_thread.start()

    def log(self,txt):

        self.updateText.emit(txt)
        pass

    def do_method(self,cb):
        self.invokeCallback.emit(cb)
        pass

    """
    kill process
    """
    def killprocess(self,pids):
        for each in filter(None, set(pids)):
            if each != None:
                self.log( "taskkill /f /pid "+str(each)+"")
                #os.popen("taskkill /f /pid "+str(each))
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                Popen("taskkill /f /pid "+str(each), startupinfo=startupinfo, stdout=PIPE, shell=True)

    """
    send data to main thread
    """
    def mainWindow_vector(self):
        self.updateText.emit("dfsdf")
        pass


    """
    start red5
    """
    def start_red5_server(self,force=True, callback=None):

        #result= subprocess.check_output(["red5.bat"],shell=True)
        #result.find("Process finished with exit code 0")
        msg = []
        myred5_port = 9991
        self.log( "Starting red5 server")
        # check my server status
        pids = myFuncs.get_pid_by_port(myred5_port)
        if len(pids)!=0:
            self.log( "started red5 server before.")
            if force == False:
                if hasattr(callback, '__call__') == True: callback(msg)
                return       #force restart my red5 server again

        #dont slient output on cmd.exe, by leave default stdout, change also for stdin,stderr since we use py2exe to deploy app
        #set slient output out,in,error: Popen("your-command", stdin=PIPE, stdout=PIPE, stderr=PIPE)
        #because we need to show debug on red5.bat and it should work property
        p = Popen([myFuncs.resource_path('data/red5.bat'),''] )
        #p = Popen(myFuncs.readFileContent(':cmd/red5.bat') )
        #p.kill()       #kill this process
        output, err = p.communicate()   #b"input data that is passed to subprocess' stdin"
        rc = p.returncode
        if str(output).find("Bootstrap exit") != -1: #error
            if hasattr(self,'tryRed5_count')==False: self.tryRed5_count=0
            self.tryRed5_count+=1

            if self.tryRed5_count<3:
                pids = myFuncs.get_pid_by_port(myred5_port)
                if len(pids)!=0:
                    self.killprocess(pids)

                #self.start_red5_server() #restart red5
            pass

        self.log( "red5 server started.")
        if output!=None: self.log("console:"+ str(output))

        if hasattr(callback, '__call__') == True: callback(msg)

        pass

    """
    stop red5 server
    """
    def stop_red5_server(self):
        red5_pid = myFuncs.get_pid_by_commandline("org.red5.server.Bootstrap","java.exe")
        if len(red5_pid)==0:
            self.log("not found red5 running")
            return

        #dont slient output on cmd.exe, by leave default stdout, change also for stdin,stderr since we use py2exe to deploy app
        #set slient output out,in,error: Popen("your-command", stdin=PIPE, stdout=PIPE, stderr=PIPE)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        p = Popen([myFuncs.resource_path(':cmd/red5-shutdown.bat'), ''] , startupinfo=startupinfo,stdin=PIPE, stdout=PIPE, stderr=PIPE)  #want this task slient
        #p = Popen(myFuncs.readFileContent(':cmd/red5-shutdown.bat') ,stdin=PIPE, stdout=PIPE, stderr=PIPE)  #want this task slient
        #p.kill()       #kill this process
        output, err = p.communicate()
        self.log("stop red5 server")
        if output != None: self.log("console:" + output)

        #find out pid for java.exe with red5 arguments
        red5_pid = myFuncs.get_pid_by_commandline("org.red5.server.Bootstrap","java.exe")
        if len(red5_pid):
            self.killprocess(red5_pid)
        return output
        pass

    """
    modify red5 config
    """
    def modify_red5_properties(self):
        import os
        localip = self.localIP
        red5_config_file =os.environ['PROGRAMFILES']+'/Red5/conf/red5.properties'
        set_change_config = False

        try:
            f = open(red5_config_file,'r')
            config = f.read()
            f.close()

            m=re.findall("rtmp\.host.+|http\.host.+",config,re.MULTILINE)
            for line in m:
                if line.split('=')[1] != localip:
                    config = config.replace(line, line.split('=')[0] + "=" + localip)
                    set_change_config=True

            #re-create red5.properties
            if set_change_config ==True:
                #backup config file before modify
                if os.path.exists(red5_config_file + ".backup") ==False:
                    os.rename(red5_config_file, red5_config_file+ ".backup")

                print config
                f=open(red5_config_file,'w')
                f.write(config)
                f.close()
        except(IOError,Exception),e:
            self.log(red5_config_file+ "not found")
        pass
    """
    test live stream create by ffmpeg
    """
    #@timeout(5, os.strerror(errno.ETIMEDOUT))
    def test_livestream(self):
        from time import sleep, time
        from command import Command

        #p = Popen('rtmpdump -v -r rtmp://192.168.1.106:1935/live/test --resume -m 5', shell=True,stdin=PIPE, stdout=PIPE, stderr=PIPE)
        #output, err = p.communicate()
        #end = time() + 5
        #while time() < end:
        #    sleep(0.001)

        #log(output)
        cmd = "ffprobe -v quiet -print_format json -show_format -show_streams rtmp://192.168.1.106/live/test"
        cmd = "rtmpdump -m 5 -v -r rtmp://192.168.1.106:1935/live/test -o test.flv --resume"

        #rtmpdump -r rtmp://192.168.1.106:1935/live/test --resume
        #output = subprocess.call("rtmpdump -m 5 -v -r rtmp://192.168.1.106:1935/live/test -o test.flv --resume",shell=True,stdout=None)
        #print output

        command = Command(r"rtmpdump -v -r rtmp://192.168.1.106:1935/live/test -o test.flv --resume")
        command.run(timeout=10)


        print "done"
        #log()
        pass

    def ajax(self):

        pass


    """
    start broadcast stream from screen to server
    """
    def start_screencast_ffmpeg(self):
        from subprocess import Popen, PIPE
        localip = self.localIP  #socket.gethostbyname(socket.gethostname())
        #do not need to kill because ffmpeg can broadcast more stream but only one stream for current playing set by ffmpeg
        #make sure to work i think
        self.stop_stream()
        self.log( "starting stream")
        #dont slient output on cmd.exe, by leave default stdout, change also for stdin,stderr since we use py2exe to deploy app
        #remove this: stdin=PIPE, stdout=PIPE, stderr=PIPE
        #because we need to show debug on red5.bat and it should work property
        #p = Popen(myFuncs.resource_path('data/ffmpeg-stream.bat '+localip+' test') )
        #set delay time before next statement :D
        self.log(myFuncs.resource_path('data/ffmpeg-stream.bat '+localip+' test'));
        p = Popen(myFuncs.resource_path('data/ffmpeg-stream.bat '+localip+' test') )
        #p = Popen(myFuncs.readFileContent(':cmd/ffmpeg-stream.bat '+localip+' test') )
        #p.kill()       #kill this process
        output, err = p.communicate()

        if output!=None: self.log('console:'+ str(output))
        
        pass

    """
    stop live stream
    """
    def stop_stream(self):
        pids = myFuncs.get_pid_by_name("ffmpeg.exe")
        if len(pids):
            self.killprocess(pids)
        self.log( "stoped stream")
        pass

    """
    start nginx server
    """
    def nginx_server(self,turn=True):
        'E:\cygwin\bin\nginx'
        if turn == True:
            #dont slient output on cmd.exe, by leave default stdout, change also for stdin,stderr since we use py2exe to deploy app
            #remove this: Popen("your-command", stdin=PIPE, stdout=PIPE, stderr=PIPE)
            p = Popen([myFuncs.resource_path(':cmd/nginx.bat'),'start'] )   #allow python open cmd for getting admin permission
            self.log("Start nginx server")
        else:
            p = Popen([myFuncs.resource_path(':cmd/nginx.bat'), 'stop'], shell=True)
            # also kill nginx process if can't stop from bat file
            #pids=get_pid_by_name("nginx.exe")
            #self.killprocess(pids)
            self.log("Stop nginx server")

        output, err = p.communicate()
        #p.kill()       #kill this process
        if output != None: self.log( "console:"+ str(output))
        return p
        pass

    """
    test rtmp stream url
    """
    def test_rtmp_server(self,rtmp_url, callback =None):
        import librtmp
        try:
            conn = librtmp.RTMP(rtmp_url, live=True)
            conn.connect()
            stream = conn.create_stream()
            # Read 1024 bytes of data
            data = stream.read(1024)

            self.log( data)
        except(Exception),e:
            if hasattr(callback, '__call__'): callback(e)

            print e
        pass

if __name__ == '__main__':

    #c=vietcodex()
    #print c.start_red5_server()
    #print stop_red5_server()

    #print test_livestream()
    #c.test_rtmp_server("rtmp://live-sin.twitch.tv/nightblue3")

    #start_screencast_ffmpeg()
    #stop_stream()

    #killprocess([12860])
    #nginx_server()
    pass