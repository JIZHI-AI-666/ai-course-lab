"""与根目录 hello.py 相同的课程入口。"""
from pathlib import Path
import runpy
if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "hello.py"), run_name="__main__")
