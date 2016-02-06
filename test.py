from distutils.core import setup
import py2exe,os,re,time,inspect
from subprocess import *

import socket

from firebase import firebase

print os.environ['PROGRAMFILES']