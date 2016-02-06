
from distutils.core import setup
import py2exe,os
import glob

def find_data_files(source,target,patterns):
    """Locates the specified data-files and returns the matches
    in a data_files compatible format.

    source is the root of the source data tree.
        Use '' or '.' for current directory.
    target is the root of the target data tree.
        Use '' or '.' for the distribution directory.
    patterns is a sequence of glob-patterns for the
        files you want to copy.
    """
    if glob.has_magic(source) or glob.has_magic(target):
        raise ValueError("Magic not allowed in src, target")
    ret = {}
    for pattern in patterns:
        pattern = os.path.join(source,pattern)
        for filename in glob.glob(pattern):
            if os.path.isfile(filename):
                targetpath = os.path.join(target,os.path.relpath(filename,source))
                path = os.path.dirname(targetpath)
                ret.setdefault(path,[]).append(filename)
    return sorted(ret.items())

Mydata_files = []   #[('images', ['c:/path/to/image/image.png'])]

"""
#images
for files in os.listdir('images/'):
    f1 = 'images/' + files
    if os.path.isfile(f1): # skip directories
        f2 = 'images', [f1]
        Mydata_files.append(f2)
"""
#data
for files in os.listdir('data/'):
    f1 = 'data/' + files
    if os.path.isfile(f1): # skip directories
        f2 = 'data', [f1]
        Mydata_files.append(f2)


#plugins imageformats
for files in os.listdir('C:/Python27/Lib/site-packages/PyQt4/plugins/imageformats/'):
    f1 = "C:\Python27\Lib\site-packages\PyQt4\plugins\imageformats/" + files
    if os.path.isfile(f1): # skip directories
        f2 = 'imageformats', [f1]
        Mydata_files.append(f2)

#other necessary files
Mydata_files.append(('',['C:\Python27\w9xpopen.exe']))

Mydata_files.append(('third-party\ProcessExplorer',['third-party\ProcessExplorer/Eula.txt']))
Mydata_files.append(('third-party\ProcessExplorer',['third-party\ProcessExplorer/procexp.exe']))
Mydata_files.append(('third-party\ProcessExplorer',['third-party\ProcessExplorer/procexp.chm']))

"""
_list=find_data_files('third-party\ProcessExplorer','',[
        '*',
        #'*'
        #'images/*',
    ])
for item in _list:
    Mydata_files.append(item)
"""

setup(
    #console=['main.py'],
    name="VietcodeX",
    version="1.0",
    description="Phan mem hoc truc tuyen.",
    author="Hoangweb.COM",
    data_files = Mydata_files,
    options={
                "py2exe":{
                    "dll_excludes": ["MSVCP90.dll", "HID.DLL", "w9xpopen.exe"],
                       "unbuffered": True,
                    #"bundle_files":1,
                        "optimize": 2,
                    'compressed': True,
                    'includes':['sip'],
                        #"excludes": ["email"]
                }
        },
    windows = [{
        'script': 'main.py',
        "icon_resources": [(1, "icon.ico")]
        }]
)