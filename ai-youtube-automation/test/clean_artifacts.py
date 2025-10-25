# clean_artifacts.py
import shutil
from pathlib import Path

root = Path("artifacts/artifacts")
if root.exists():
    for sub in root.iterdir():
        dest = Path("artifacts") / sub.name
        if not dest.exists():
            shutil.move(str(sub), str(dest))
    shutil.rmtree(root)
    print("✅ Moved nested artifacts/ contents to root and removed duplicates.")
else:
    print("✅ No nested artifacts/ found.")
