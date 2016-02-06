__author__ = 'Hoang'
import threading,time
import PyQt4.QtCore
from PyQt4 import *

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""
    i=0

    def __init__(self,target=None,args=None,name=""):
        self.i+=1
        if name=="": name = "StoppableThread %d" %self.i
        super(StoppableThread, self).__init__(None,target=target,args=args,name=name)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    #isStopped
    def stopped(self):
        return self._stop.isSet()

"""
QThread
"""
class myThread(PyQt4.QtCore.QThread):

    def __init__(self, fn, args=[], kwargs={}, parent=None):
        super(myThread, self).__init__(parent)
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def run(self):
        self._fn(*self._args, **self._kwargs)

class MyThread1(PyQt4.QtCore.QThread):
    trigger = PyQt4.QtCore.pyqtSignal()
    updatePD = PyQt4.QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super(MyThread1, self).__init__(parent)

    def run(self):
        self.trigger.emit()

"""
QThread for me
"""
class hQtObject(PyQt4.QtCore.QObject):
    finished = PyQt4.QtCore.pyqtSignal()
    #add task
    add_job = None

    #callback finish
    finish_task = None

    def longRunning(self):
        print "start job in longRunning method."
        """
        count = 0
        while count < 5:
            time.sleep(1)
            count += 1
        """
        if hasattr(self.add_job, '__call__'):
            self.add_job()
        self.finished.emit()