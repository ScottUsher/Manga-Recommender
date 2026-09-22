from PyInstaller.utils.hooks import collect_all, copy_metadata

datas, binaries, hiddenimports = collect_all("streamlit")
metadata = copy_metadata("streamlit")

a = Analysis(
    ["Launcher.py"],
    pathex=[],
    binaries=binaries,
    datas=[
        ("manga_recomendation.py", "."),
        ("datalist.json", "."),
        *datas,
        *metadata,
    ],
    hiddenimports=[
    "recomendation_processing"
],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name="MyRecommender",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)