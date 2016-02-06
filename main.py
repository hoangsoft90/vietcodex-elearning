__author__ = 'Hoang'

import sys
from PyQt4 import QtGui,QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import thread,socket
from hoang import vietcodex
import myFuncs,time
import data_rc
from customThread import *
from trayIcon import *

from dialog.dlg_help import *
from Elearning import *

class mainWindow(QtGui.QMainWindow):    #QWidget
    title = "VietcodeX.com"

    def _handleTextUpdate(self,_str):
        #print _str
        #_str.mainWin=self
        self.log(_str)
        pass

    def _handle_callback(self,func):
        if hasattr(func, '__call__'):
            func()
            print "invoke function"
        pass

    def __init__(self):
        super(mainWindow, self).__init__()

        #setup tray
        self.trayIcon = SystemTrayIcon(self)
        traySignal = "activated(QSystemTrayIcon::ActivationReason)"
        QtCore.QObject.connect(self.trayIcon, QtCore.SIGNAL(traySignal), self.__icon_activated)

        #instance class ( second thread call in first thread)
        #start from first thread
        self.vcdx = vietcodex()
        #self.vcdx.mainWin = self    #reference instance
        self.elearning = Elearning(parent=self.vcdx) #instance vietcode before

        #receive data from second thread
        self.vcdx.updateText.connect(self._handleTextUpdate)
        self.vcdx.invokeCallback.connect(self._handle_callback)

        #first to send data (start thread)
        self.vcdx.update_list("testing send data for updating ui",None)
        #init thread to invoke callback
        self.vcdx.call_func(None)

        #move this object to thread
        #self.objThread = QtCore.QThread()
        #self.moveToThread(self.objThread)      #note Widgets cannot be moved to a new thread


        self.initUI()
        #init
        self.init()

    def __icon_activated(self,reason):
        if reason == QtGui.QSystemTrayIcon.DoubleClick:
            self.show()     #show window when hit double mouse click on icon
        pass

    """
    write log
    """
    def log(self,_str):
        def setLog():
            if isinstance(self.logOutput,QtGui.QTextEdit):
                #self.logOutput.setText(self.logOutput.toHtml() + "\n" + str(_str))
                self.logOutput.append(str(_str))
                self.logOutput.verticalScrollBar().setValue(self.logOutput.verticalScrollBar().maximum())

        #thread.start_new_thread(setLog,())     #can' run thread on thread
        setLog()
        """
        f=open("log.txt","w")          #create new file
        f.truncate()
        f.write(str)
        f.close()
        """

    """
    current window close event, override method
    """
    def closeEvent(self, event):
        #msg = QtGui.QMessageBox.question(self, 'Thong bao',
        #    "App still running, see window tray", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        """
        if msg == QtGui.QMessageBox.Ok:
            event.accept()
        else:
            event.ignore()
        """
        if False:#self.okayToClose():
            #user asked for exit
            self.trayIcon.hide()
            event.accept()
        else:
            #"minimize"
            self.hide()
            self.trayIcon.show() #thanks @mojo
            event.ignore()


    """
    destroy everthing before quit app keep nginx server
    """
    def stopEverything(self):

        ### ffmpeg
        #stop server also stop stream
        self.vcdx.stop_stream()
        #stop ffmpeg thread
        if hasattr(self, 'startffmpeg_thread'):
            self.startffmpeg_thread.stop()
            #self.check_ffmpeg_thread.terminate()   #can use this

        ### red5
        self.vcdx.stop_red5_server()
        if hasattr(self,'startRed5_thread'):
            self.startRed5_thread.stop()        #stop startRed5 server thread

        #you still want keepping nginx server
        #verify livestream server
        self.check_to_go_livestream_client_website()
        pass

    """
    start red5 live stream server
    """
    def _start_stream_server(self):
        self.btn_startMedia_server.setDisabled(True)
        self.btn_stopMedia_server.setDisabled(False)
        self.btn_startMedia_server.setText("working..")

        def _callback(msg):
            self.log( "startRed5_thread finished...exiting")
            pass

        """
        self.red5_Thread = MyThread1()#
        self.startRed5_thread=hQtObject()
        self.startRed5_thread.add_job = self.vcdx.start_red5_server
        self.startRed5_thread.moveToThread(self.red5_Thread)
        self.startRed5_thread.finished.connect(self.red5_Thread.quit)
        self.red5_Thread.started.connect(self.startRed5_thread.longRunning)
        self.red5_Thread.finished.connect(_callback)
        self.red5_Thread.start()
        """
        #stop thread if found
        if hasattr(self,'startRed5_thread'):
            self.startRed5_thread.stop()        #stop startRed5 server thread

        #i don't know but _broadcast_livestream use this way. Because i switch to above code my stream nerver start successful
        self.startRed5_thread = StoppableThread(target=self.vcdx.start_red5_server,args = (10, ))
        self.startRed5_thread.start()
        #self.startRed5_thread.join()
        #self.log( "startRed5_thread finished...exiting")        #nerver meet, long running
        #thread.start_new_thread(self.vcdx.start_red5_server, (False,_callback))
        def _start_red5():
            time.sleep(5)   #CHECK for 5 seconds
            self.btn_startMedia_server.setDisabled(False)     #this menu alway enable

            if len(myFuncs.get_pid_by_commandline("org.red5.server.Bootstrap","java.exe"))==0:
                self.menu_item_red5_start_Action.setEnabled(True)
                self.btn_stopMedia_server.setDisabled(True)
                #myFuncs.msgBox(self,"Error to create stream.")
                self.vcdx.log ("\nUnable to start Red5, do it again.")
                #do not call self.log method
            else:

                self.menu_item_red5_start_Action.setEnabled(False)
                self.btn_stopMedia_server.setDisabled(False)

            self.btn_startMedia_server.setText("Start media server")
            pass

        self.check_red5_thread = MyThread1()

        self.red5_thread=hQtObject()
        self.red5_thread.add_job = _start_red5
        self.red5_thread.moveToThread(self.check_red5_thread)
        self.check_red5_thread.trigger.connect(self.pdialog)
        self.check_red5_thread.finished.connect(self.check_red5_thread.quit)
        self.check_red5_thread.started.connect(self.red5_thread.longRunning)
        #self.objThread.finished.connect(_callback)
        self.check_red5_thread.start()

    """
    stop media server
    """
    def _stop_stream_server(self,event):
        #self.vcdx.start_red5_server()
        reply = QtGui.QMessageBox.question(self, self.title,
                    "Turn off red5 server?", QtGui.QMessageBox.Yes |
                    QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.stop_stream_server()
        pass

    def stop_stream_server(self):
        self.btn_startMedia_server.setDisabled(False)
        self.menu_item_red5_start_Action.setEnabled(True)
        self.btn_stopMedia_server.setDisabled(True)

        self.btn_stopStream.setDisabled(True)   #also stop stream
        self.btn_startStream.setDisabled(False)

        stopRed5_thread = threading.Thread(target=self.stopEverything)
        stopRed5_thread.start()
        #stopRed5_thread.join()
        self.log("Stop red5 thread "  )
        pass
    """
    check red5 server status
    """
    def red5_server_status_event(self):
        def check_netstat():
            time.sleep(3)
            pids = myFuncs.get_pid_by_commandline("org.red5.server.Bootstrap","java.exe")
            if len(pids)>0:
                self.vcdx.log("Exists stream server")
                self.btn_stopMedia_server.setEnabled(True)
            else:
                self.vcdx.log("Not found stream server")
                self.menu_item_red5_start_Action.setEnabled(True)
                self.btn_stopMedia_server.setEnabled(False)
            pass

        #self.vcdx.do_method(check_netstat)     #do not put heavy task
        thread.start_new_thread(check_netstat, ())
        self.vcdx.log( "red5 server checking...")
        pass

    """
    stream status check
    """
    def ffmpeg_stream_status_event(self):
        def check_netstat():
            time.sleep(3)
            pids = myFuncs.get_pid_by_name("ffmpeg.exe")
            if len(pids)>0:
                self.vcdx.log("Exists live stream")
                self.btn_stopStream.setEnabled(True)
            else:
                self.vcdx.log("Not found live stream")
                self.menu_item_broadcast_stream_Action.setEnabled(True)
                self.btn_stopStream.setEnabled(False)
            pass

        #self.vcdx.do_method(check_netstat)     #do not put heavy task
        thread.start_new_thread(check_netstat, ())
        self.vcdx.log( "live stream checking...")
        pass

    """
    nginx status checker
    """
    def nginx_status_event(self):
        def check_netstat():
            time.sleep(3)
            pids = myFuncs.get_pid_by_name("nginx.exe")
            if len(pids)>0:
                self.vcdx.log("nginx server started.")
                self.btn_stopNginx.setEnabled(True)
            else:
                self.vcdx.log("nginx has not started.")
                self.menu_item_nginx_Action.setEnabled(True)
                self.btn_stopNginx.setEnabled(False)
            pass

        #self.vcdx.do_method(check_netstat)     #do not put heavy task
        thread.start_new_thread(check_netstat, ())
        self.vcdx.log( "nginx state checking...")
        pass
    """
    when start all threads
    """
    def pdialog(self):
        print "pdialog"
        if hasattr(self, 'end__broadcast_livestream_thread') and self.end__broadcast_livestream_thread:
            self.check_ffmpeg_thread.terminate()

        if hasattr(self, 'end__start_stream_server_thread') and self.end__start_stream_server_thread:
            self.check_red5_thread.terminate()
            pass

        if hasattr(self, 'end__start_nginx_thread') and self.end__start_nginx_thread:
            self.check_nginx_thread.terminate()
            pass
        pass
    """
    start _broadcast_livestream thread
    """
    def _broadcast_livestream_thread(self):
        self.end__broadcast_livestream_thread = True
        self._broadcast_livestream()
        pass

    """
    start _start_nginx thread
    """
    def _start_nginx_thread(self):
        self.end__start_nginx_thread = True
        self._start_nginx()
        pass

    """
    start _start_stream_server thread
    """
    def _start_stream_server_thread(self):
        self.end__start_stream_server_thread = True
        self._start_stream_server()
        pass

    """
    start boardcast live stream to server
    """
    def _broadcast_livestream(self):
        self.btn_startStream.setDisabled(True)  #disable start stream button
        self.btn_startStream.setText("working..")
        self.btn_stopStream.setDisabled(True)  #enable stop stream button
        #heavy job
        def start_ffmpeg():
            time.sleep(7)   #CHECK for 5 seconds
            if len(myFuncs.get_pid_by_name("ffmpeg.exe"))==0:
                self.btn_startStream.setDisabled(False)
                self.btn_stopStream.setDisabled(True)
                #myFuncs.msgBox(self,"Error to create stream.")
                self.vcdx.log ("\nUnable to create stream, check Red5 server for ready\nYou can restart Red5 server or restart live stream more times (up to 3).")
                #do not call self.log method
            else:
                self.btn_startStream.setDisabled(False)     #this menu alway enable
                self.menu_item_broadcast_stream_Action.setEnabled(False)
                self.btn_stopStream.setDisabled(False)

            self.btn_startStream.setText("Start stream")
            pass
        #thread.start_new_thread(self.vcdx.start_screencast_ffmpeg,())
        self.startffmpeg_thread = StoppableThread(target=self.vcdx.start_screencast_ffmpeg,args=())
        self.startffmpeg_thread.start()

        #check ffmpeg already
        if hasattr(self, 'check_ffmpeg_thread')==True: #and self.check_ffmpeg_thread.isRunning():
            #self.check_ffmpeg_thread.exit()
            #self.check_ffmpeg_thread.terminate()
            pass


        self.check_ffmpeg_thread = MyThread1()

        self.ffmpeg_thread=hQtObject()
        self.ffmpeg_thread.add_job = start_ffmpeg
        self.ffmpeg_thread.moveToThread(self.check_ffmpeg_thread)
        self.check_ffmpeg_thread.trigger.connect(self.pdialog)
        self.check_ffmpeg_thread.finished.connect(self.check_ffmpeg_thread.quit)
        self.check_ffmpeg_thread.started.connect(self.ffmpeg_thread.longRunning)
        #self.objThread.finished.connect(_callback)
        self.check_ffmpeg_thread.start()


        #check_ffmpeg_thread = StoppableThread(target=start_ffmpeg,args=())
        #self.moveToThread(check_ffmpeg_thread)
        #check_ffmpeg_thread.start()

        #thread.start_new_thread(start_ffmpeg,())
        pass

    """
    stop boardcast live stream
    """
    def _stop_broadcast_livestream(self,event=None):
        reply = QtGui.QMessageBox.question(self, self.title,
                    "Turn off live stream ?", QtGui.QMessageBox.Yes |
                    QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.stop_broadcast_livestream()
        pass

    def stop_broadcast_livestream(self):
        self.btn_stopStream.setDisabled(True)
        self.menu_item_broadcast_stream_Action.setEnabled(True)
        self.btn_startStream.setDisabled(False)

        stopffmpeg_thread = threading.Thread(target=self.vcdx.stop_stream)
        stopffmpeg_thread.start()

        if hasattr(self, 'startffmpeg_thread'):
            self.startffmpeg_thread.stop()   #end thread for ffmpeg
        pass
    """
    start nginx server
    """
    def _start_nginx(self):
        self.btn_startNginx.setDisabled(True)
        self.btn_stopNginx.setDisabled(False)
        self.btn_startNginx.setText("working..")

        def start_nginx():
            self.vcdx.nginx_server(True)    #start nginx with thread wrapper
            pass

        self.start_nginx_thread = StoppableThread(target=start_nginx ,args=())
        self.start_nginx_thread.start()

        def _start_nginx_server():
            time.sleep(3)   #CHECK for 3 seconds
            self.btn_startNginx.setDisabled(False)     #this menu alway enable

            if len(myFuncs.get_pid_by_name("nginx.exe"))==0:
                self.menu_item_nginx_Action.setEnabled(True)
                self.btn_stopNginx.setDisabled(True)
                #myFuncs.msgBox(self,"Error to create stream.")
                self.vcdx.log ("\nUnable to start Nginx server, do it again.")
                #do not call self.log method
            else:

                self.menu_item_nginx_Action.setEnabled(False)
                self.btn_startNginx.setDisabled(False)

            self.btn_startNginx.setText("Start nginx")
            pass

        self.check_nginx_thread = MyThread1()

        self.nginx_thread=hQtObject()
        self.nginx_thread.add_job = _start_nginx_server
        self.nginx_thread.moveToThread(self.check_nginx_thread)
        self.check_nginx_thread.trigger.connect(self.pdialog)
        self.check_nginx_thread.finished.connect(self.check_nginx_thread.quit)
        self.check_nginx_thread.started.connect(self.nginx_thread.longRunning)
        #self.objThread.finished.connect(_callback)
        self.check_nginx_thread.start()
        pass

    """
    stop nginx server
    """
    def _stop_nginx(self,event):
        reply = QtGui.QMessageBox.question(self, self.title,
                    "Stop nginx server ?", QtGui.QMessageBox.Yes |
                    QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.btn_startNginx.setDisabled(False)
            self.menu_item_nginx_Action.setEnabled(True)

            self.btn_stopNginx.setDisabled(True)

            self.vcdx.nginx_server(False)
            if hasattr(self, 'start_nginx_thread'):
                self.start_nginx_thread.stop()
        pass

    """
    bootstrap
    """
    def init(self):
        #valid red5.properties
        self.vcdx.modify_red5_properties()

        #make sure server, livestream, nginx are working
        status= self.verify_servers4livestream()

        #check red5 server for ready
        #red5_pid = myFuncs.get_pid_by_commandline("org.red5.server.Bootstrap","java.exe")
        if status['red5']:
            self.menu_item_red5_start_Action.setEnabled(False)
            self.btn_stopMedia_server.setDisabled(False)
        else:
            self.menu_item_red5_start_Action.setEnabled(True)
            self.btn_stopMedia_server.setDisabled(True)

        #check ffmpeg stream
        #ffmpeg_pids = myFuncs.get_pid_by_name("ffmpeg.exe")
        if status['ffmpeg']:
            self.menu_item_broadcast_stream_Action.setEnabled(False)
            self.btn_stopStream.setDisabled(False)
        else:
            self.menu_item_broadcast_stream_Action.setEnabled(True)
            self.btn_stopStream.setDisabled(True)

        #check nginx server for ready

        #nginx = myFuncs.get_pid_by_name("nginx.exe")
        if status['nginx']:
            self.menu_item_nginx_Action.setEnabled(False)
            self.btn_stopNginx.setDisabled(False)
        else:
            self.menu_item_nginx_Action.setEnabled(True)
            self.btn_stopNginx.setDisabled(True)


        if status['red5'] and status['ffmpeg'] :#and status['nginx']:   #we dont use nginx
            self.btn_go_site.setEnabled(True)
        else:
            #self.btn_go_site.setEnabled(False) #no, shoulh click to check
            pass
        pass

    """
    help dialog
    """
    def view_help_button_event(self,event):
        if hasattr(self, 'help')==False:
            self.help=hwDlgHelp(self)

        self.help.show()
        self.help.raise_()
        pass

    """
    go local site for playing live stream
    """
    def go_livestream_client_website(self):
        self.btn_go_site.setEnabled(False)  #disable while processing
        self.btn_go_site.setText("checking...")

        thread.start_new_thread(self.check_to_go_livestream_client_website, ())
        pass

    """
    kill all servers for live streaming
    """
    def kill_all_livestream(self):
        reply = QtGui.QMessageBox.question(self, self.title,
                    "Are you sure to kill all servers?", QtGui.QMessageBox.Yes |
                    QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        def force_kill():
            self.stopEverything()
            ###force
            #find out pid for java.exe with red5 arguments
            red5_pid = myFuncs.get_pid_by_commandline("org.red5.server.Bootstrap","java.exe")
            if len(red5_pid):
                self.vcdx.killprocess(red5_pid)

            pass

        if reply == QtGui.QMessageBox.Yes:
            thread.start_new_thread( force_kill,())
        else:
               pass

        pass
    """
    check whether all server,emit livestream,apache are working
    """
    def verify_servers4livestream(self):
        #check red5 server for ready
        red5_pid = myFuncs.get_pid_by_commandline("org.red5.server.Bootstrap","java.exe")

        #check ffmpeg stream
        ffmpeg_pids = myFuncs.get_pid_by_name("ffmpeg.exe")

        #check nginx server for ready
        nginx = myFuncs.get_pid_by_name("nginx.exe")

        #make sure server, livestream, nginx are working
        return {"red5":len(red5_pid), "ffmpeg": len(ffmpeg_pids), "nginx": len(nginx)}

    """
    create go_livestream_client_website thread
    """
    def check_to_go_livestream_client_website(self):
        import webbrowser

        #make sure server, livestream, nginx are working
        status = self.verify_servers4livestream()
        if status['red5'] and status['ffmpeg'] :    #and status['nginx']:   #do not need nginx server
            #store processor local IP on database
            self.elearning.storeLocalIP()
            self.elearning.activeElearning_site("1")        #active client site

            webbrowser.open(self.elearning.livestream_client_site)
        else:
            self.vcdx.log("No any servers found, \nYou need to start necessary servers before go elearning site.")
            self.elearning.activeElearning_site("0")

        self.btn_go_site.setEnabled(True)  #enable button
        self.btn_go_site.setText("Go E-Learning Site")  #resume button label
        pass

    """
    open task manager
    """
    def open_processes_manager(self):
        #from subprocess import Popen
        process = os.startfile('third-party\ProcessExplorer\procexp.exe')

        pass

    """
    init UI controls
    """
    def initUI(self):
        """
        exitAction = QtGui.QAction(QtGui.QIcon('images/icon_menu_left.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.setToolTip("heloos<b>dfsdf</b>")
        exitAction.triggered.connect(QtGui.qApp.quit)
        """
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        """
        init buttons
        """
        #connect button
        self.btn_startMedia_server = QtGui.QPushButton('Start media Server')
        self.btn_startMedia_server.setToolTip('Start livestream server')
        #btn.resize(btn.sizeHint())
        red5_menu = QtGui.QMenu()
        self.menu_item_red5_start_Action = QtGui.QAction(QtGui.QIcon(''), '&Start', self)
        self.menu_item_red5_start_Action.triggered.connect(self._start_stream_server_thread)
        #menu.addAction('Start', self._broadcast_livestream_thread)
        red5_menu.addAction(self.menu_item_red5_start_Action)
        red5_menu.addAction('Check exists', self.red5_server_status_event)
        self.btn_startMedia_server.setMenu(red5_menu)

        #self.btn_startMedia_server.clicked.connect(self._start_stream_server)

        #stop media server
        self.btn_stopMedia_server = QtGui.QPushButton('Stop media Server')
        self.btn_stopMedia_server.setToolTip('Stop livestream server')
        self.btn_stopMedia_server.clicked.connect(self._stop_stream_server)

        #broadcast screen
        self.btn_startStream = QtGui.QPushButton('Start stream')
        self.btn_startStream.setToolTip('Broadcast live stream to server')
        #self.btn_startStream.clicked.connect(self._broadcast_livestream)

        stream_menu = QtGui.QMenu()
        self.menu_item_broadcast_stream_Action = QtGui.QAction(QtGui.QIcon(''), '&Start', self)
        self.menu_item_broadcast_stream_Action.triggered.connect(self._broadcast_livestream_thread)
        #menu.addAction('Start', self._broadcast_livestream_thread)
        stream_menu.addAction(self.menu_item_broadcast_stream_Action)
        stream_menu.addAction('Check exists', self.ffmpeg_stream_status_event)
        self.btn_startStream.setMenu(stream_menu)

        #stop broadcast screen
        self.btn_stopStream = QtGui.QPushButton('Stop stream')
        self.btn_stopStream.setToolTip('Stop Broadcast live stream to server')
        self.btn_stopStream.clicked.connect(self._stop_broadcast_livestream)

        #start nginx server
        self.btn_startNginx = QtGui.QPushButton('Start nginx')
        self.btn_startNginx.setToolTip('Start nginx server')
        #self.btn_startNginx.clicked.connect(self._start_nginx)
        #self.btn_startNginx.setEnabled(False)   #never use this button

        nginx_menu = QtGui.QMenu()
        self.menu_item_nginx_Action = QtGui.QAction(QtGui.QIcon(''), '&Start nginx', self)
        self.menu_item_nginx_Action.triggered.connect(self._start_nginx_thread)
        nginx_menu.addAction(self.menu_item_nginx_Action)
        nginx_menu.addAction('Check exists', self.nginx_status_event)
        self.btn_startNginx.setMenu(nginx_menu)

        #start nginx server
        self.btn_stopNginx = QtGui.QPushButton('Stop nginx')
        self.btn_stopNginx.setToolTip('Stop nginx server')
        self.btn_stopNginx.clicked.connect(self._stop_nginx)
        #self.btn_stopNginx.setEnabled(False)   #never use this button

        self.lbl_status = QtGui.QLabel('@Copyright Vietcodex.edu.vn')
        #self.lbl_status.move(15, 10)

        #log output
        self.logOutput = QtGui.QTextBrowser(self)   #QTextEdit
        self.logOutput.setReadOnly(True)
        #self.logOutput.setLineWrapMode(QtGui.QTextBrowser.wordWrapMode())
        #self.logOutput.setText("hello")
        #self.logOutput.setText(self.logOutput.toHtml() +"\ndfgdhfg")
        #hoang.txtLog = self.logOutput       #reference log output handle

        #guide tip
        lbl_tip = QtGui.QLabel()
        lbl_tip.setText(myFuncs.readFileContent('data/guide_tip.txt'))

        #help button
        btn_help = QtGui.QPushButton()
        btn_help.setText("HUONG DAN")
        btn_help.clicked.connect(self.view_help_button_event)

        #kill all servers
        self.btn_kill_livestream = QtGui.QPushButton()
        self.btn_kill_livestream.setText("Kill servers")
        self.btn_kill_livestream.clicked.connect(self.kill_all_livestream)

        #go class button
        self.btn_go_site= QtGui.QPushButton()
        self.btn_go_site.setText("Active E-Learing site")
        self.btn_go_site.clicked.connect(self.go_livestream_client_website)

        #self.btn_go_site.setEnabled(False)
        #open ProcessExplorer program
        self.btn_open_procexp = QtGui.QPushButton()
        self.btn_open_procexp.setText("Task manager")
        self.btn_open_procexp.clicked.connect(self.open_processes_manager)

        #-------------------Layout----------------------
        vbox_left = QtGui.QVBoxLayout()
        vbox_left.addStretch(1)
        vbox_left.addWidget(self.btn_startMedia_server)
        vbox_left.addWidget(self.btn_stopMedia_server)

        vbox_left.addWidget(self.btn_startStream)
        vbox_left.addWidget(self.btn_stopStream)

        vbox_left.addWidget(self.btn_startNginx)
        vbox_left.addWidget(self.btn_stopNginx)



        vbox_left.addWidget(self.lbl_status)    #status

        #hbox.addWidget(exitAction)
        vbox_right = QtGui.QVBoxLayout()
        vbox_right.addStretch(1)
        vbox_right.addWidget(self.logOutput)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox_left)
        hbox.addLayout(vbox_right)

        mvbox = QtGui.QVBoxLayout()
        mvbox.addStretch(1)

        #horizontal box to hold buttons
        hbox_buttons = QtGui.QHBoxLayout()
        mvbox.addLayout(hbox_buttons)

        hbox_buttons.addWidget(btn_help)
        hbox_buttons.addWidget(self.btn_kill_livestream)
        hbox_buttons.addWidget(self.btn_open_procexp)
        hbox_buttons.addWidget(self.btn_go_site)

        mvbox.addWidget(lbl_tip)
        mvbox.addLayout(hbox)

        self.central_widget.setLayout(mvbox)
        QtGui.QToolTip.setFont(QtGui.QFont('tahoma', 10))
        #self.statusBar().showMessage('sdfsfldhgdfhgoshdposg')
        #self.setLayout(self.central_widget)
        #self.toolbar1 = self.addToolBar('Exit')
        #self.toolbar1.addAction(exitAction)

        #menubar = self.menuBar()
        #fileMenu = menubar.addMenu('&File')
        #fileMenu.addAction(exitAction)
        #status bar
        localip = socket.gethostbyname(socket.gethostname())
        self.statusBar().showMessage("IP: " +localip+ " | Network:" + myFuncs.get_current_network())

        self.setGeometry(300, 300, 400, 150)
        self.setWindowTitle(self.title)

        icon = QtGui.QIcon((':icons/icon.ico'))
        #set window icon
        self.setWindowIcon(icon)

        self.resize(400, 200)
        self.center()
        self.show()



    """
    def getpid(self,process_name):
        import os
        return [item.split()[1] for item in os.popen('tasklist').read().splitlines()[4:] if process_name in item.split()]

    def runCmd(self):
        import subprocess
        from subprocess import call
        import os
        #call("cmd")
        #call(["CURL HTTP://localhost"], shell=True)
        #print subprocess.check_output(["red5-shutdown.bat"],shell=True)

        # you can convert batch file to exe or run red5 as service
        print self.getpid("cmd.exe")



        #print subprocess.check_output(["red5.bat"],shell=True)
        #print subprocess.check_output(["red5-shutdown.bat"],shell=True)
        #other way
        from subprocess import Popen
        #p = Popen("red5-shutdown.bat")
        #stdout, stderr = p.communicate()

        import os
        #t=os.system('curl http://localhost')
        #print t
        pass
    """
    def api(self):
        import httplib
        self.runCmd()
        """
        h=httplib.HTTPConnection("localhost","80")

        #load url
        h.request("GET","/1.php")          #(method,path)

        r=h.getresponse()

        for x in r.getheaders():
             print "%s:%s"%x
        """


    def clickEvent1(self,event):
        #QtCore.QCoreApplication.instance().quit
        import thread
        import threading
        thread.start_new_thread(self.api,())


        pass

    def center(self):

        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


def main():

    app = QtGui.QApplication(sys.argv)

    # Create and display the splash screen
    splash_pix = QPixmap((':images/splash-screen.jpg'))
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()

    app.processEvents()

    # Simulate something that takes time
    time.sleep(2)

    form=mainWindow()   #wait mainWindow call init method
    splash.finish(form)

    #w.closeEvent(myevent)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()