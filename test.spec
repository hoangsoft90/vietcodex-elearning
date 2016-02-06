# -*- mode: python -*-
a = Analysis(['test.py'],
             pathex=['C:\\Users\\Hoangweb Ltd\\Documents\\python1'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='test.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
