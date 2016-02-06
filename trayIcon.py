#! /usr/bin/env python
from PyQt4 import QtGui, QtCore
import os
import images_rc

class RightClickMenu(QtGui.QMenu):
    def __init__(self, parent=None):
        QtGui.QMenu.__init__(self, "Edit", parent)

        icon = QtGui.QIcon.fromTheme("edit-cut")
        self.addAction(QtGui.QAction(icon, "&Cut", self))

        icon = QtGui.QIcon.fromTheme("edit-copy")
        self.addAction(QtGui.QAction(icon, "Copy (&X)", self))

        icon = QtGui.QIcon.fromTheme("edit-paste")
        self.addAction(QtGui.QAction(icon, "&Paste", self))
    
class LeftClickMenu(QtGui.QMenu):
    parentWindow = None
    def __init__(self, parent=None):
        QtGui.QMenu.__init__(self, "File", parent)
        self.parentWindow = parent

        showAction = QtGui.QAction(QtGui.QIcon('icon.png'), '&Show',self)
        #showAction.setShortcut('Ctrl+Q')
        showAction.setStatusTip('Show application')
        showAction.triggered.connect(self.showApp)

        exitAction = QtGui.QAction(QtGui.QIcon('icon.png'), '&Quit',self)
        #showAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Quit application')
        exitAction.triggered.connect(self.quitApp)

        self.addAction(showAction)
        self.addAction(exitAction)

    """
    show main window
    """
    def showApp(self):
        print "show main window"
        self.parentWindow.show()
        pass

    """
    quit entire app
    """
    def quitApp(self):
        #QtGui.qApp.quit
        self.parentWindow.stopEverything()
        self.parentWindow.hide()    #hide main window
        QtGui.qApp.quit()
        os._exit(1)
        self.hide() #hide tray icon
        pass

class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, parent)
        self.setIcon(QtGui.QIcon(":icons/icon.png"))

        #self.right_menu = RightClickMenu()
        #self.setContextMenu(self.right_menu)

        self.left_menu = LeftClickMenu(parent)
    
        self.activated.connect(self.click_trap)

    def click_trap(self, value):
        if value == self.Trigger: #left click!
            self.left_menu.exec_(QtGui.QCursor.pos())

    def welcome(self):
        self.showMessage("Hoangweb.com", "Phan mem day hoc truc tuyen.")
        
    def show(self):
        QtGui.QSystemTrayIcon.show(self)
        QtCore.QTimer.singleShot(100, self.welcome)

"""
if __name__ == "__main__":
    app = QtGui.QApplication([])

    tray = SystemTrayIcon()
    tray.show()
    
    #set the exec loop going
    app.exec_()
"""