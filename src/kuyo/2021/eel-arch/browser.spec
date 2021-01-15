# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['eel_arch.py'],
             pathex=['~/work/eel_arch'],
             binaries=[],
             datas=[('index.html', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='eel_arch',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='icon.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='eel_arch')
app = BUNDLE(coll,
             name='eel_arch.app',
             icon='icon.icns',
             bundle_identifier="net.ykrods.eel_arch",
             info_plist={
                 'NSPrincipalClass': 'NSApplication',
                 'NSAppleScriptEnabled': False,
                 'LSUIElement': False,
                 'LSBackgroundOnly': False,
             })
