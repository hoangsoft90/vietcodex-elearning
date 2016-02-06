__author__ = 'Hoang'
import os,re,sys
from PyQt4 import QtGui,QtCore
import codecs,inspect
#from subprocess import *
import subprocess

"""
get pid by port
"""
def get_pid_by_port(port):
    pids = []
    #add -n arg to rapid command
    #a = os.popen("netstat -oan |findstr \":"+str(port)+"\"").readlines()
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    a = subprocess.Popen("netstat -oan |findstr \":"+str(port)+"\"",  stdout=subprocess.PIPE, startupinfo=startupinfo).stdout.read().splitlines()
    for x in a:
          try:
              pids.append(x.split(" ")[-1])
             #pids.append(int(x[29:34]))
          except:
               pass
    return pids
    #killprocess(pids)

"""
get pid by name
"""
def get_pid_by_name(process_name):
    import os
    #you can use: Popen("tasklist",  stdout=PIPE).stdout.read().splitlines() #do not add shell=True
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    #lines = os.popen('tasklist').read().splitlines()[4:]
    lines = subprocess.Popen("tasklist", startupinfo=startupinfo, stdout=subprocess.PIPE).stdout.read().splitlines()
    pids= [item.split()[1] for item in lines if process_name in item.split()]
    if len(pids)==0:
        pids = get_pid_by_commandline(None,process_name)     #try again

    return pids
    pass

"""
get pid by process name & command line
"""
def get_pid_by_commandline(search_cmd=None,name=None):
    pids = []
    wmic = "WMIC PROCESS"
    if name!=None :
        wmic += " where (Name=\"" +name+ "\")"

    wmic += " get Name,CommandLine,Processid"

    #add -n arg to rapid command
    #a = os.popen(wmic).readlines()
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    a = subprocess.Popen(wmic, startupinfo=startupinfo,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = a.communicate()
    b=output.split(os.linesep)
    for x in b[1:]:
          try:
              if x.strip()=="": continue
              if search_cmd!=None:
                  m = re.search(search_cmd, x)
                  if m.group(0) ==None:
                      continue

              pids.append(x.split(name)[-1].strip())

             #pids.append(int(x[29:34]))
          except:
               pass
    #pids = pids[1:]
    return pids
    pass

"""
run silent command line
"""
def silent_cmd(command,callback):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    a = subprocess.Popen(command,startupinfo=startupinfo, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = a.communicate()
    b=output.split(os.linesep)
    result=[]

    for x in b[1:]:
          try:
              if inspect.isfunction(callback):callback(x,result)
          except:
               pass

    return result
    pass

"""
get current network name
"""
def get_current_network():
    def cb(x,data):
        if x.strip()=="" or re.match("(\s+)?SSID(\s+)?\:(\s+)?",x)==None: pass
        else:
            m=re.sub("(\s+)?SSID(\s+)?\:(\s+)?",'',x)
            data.append(m.strip())
        pass

    result =silent_cmd("netsh wlan show interfaces",cb)
    if len(result)>0: return result[0]
    return ""
    pass

"""
kill process
"""
def _killprocess(pids):
    for each in filter(None, set(pids)):
        if each != None:
            #os.popen("taskkill /f /pid "+str(each))
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen("taskkill /f /pid "+str(each), startupinfo=startupinfo, stdout=subprocess.PIPE, shell=True)

"""
Messagebox
"""
def msgBox(parent,txt,title="::Thong bao",buttons=QtGui.QMessageBox.Ok,default=QtGui.QMessageBox.Ok):
    QtGui.QMessageBox.question(parent, title,
        txt, buttons, default)
    pass

"""
read file from resource
"""
def readFileFromResource(file):
    """

    """
    fd = QtCore.QFile(file)
    if fd.open(QtCore.QFile.Text|QtCore.QIODevice.ReadOnly ):
        text = QtCore.QTextStream(fd).readAll()
        fd.close()
        return str(text)

    return ""
    pass

"""
read content file
"""
def readFileContent(file):
    f=codecs.open(file,mode='r',encoding='utf-8')  #seem: codecs not work with pyinstaller
    #f=open(file,mode='r')
    content = f.read()
    f.close()
    return content
    pass
"""
pyinstaller unpacks your data into a temporary folder, and stores this directory path in the _MEIPASS2 environment variable.
"""
def resource_path(relative):
    path= os.path.join(
        os.environ.get(
            "_MEIPASS2",
            os.path.abspath(".")
        ),
        relative
    )
    print path
    return path

def resource_path1(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    path= os.path.join(base_path, relative_path)

    """
    print relative_path
    return relative_path