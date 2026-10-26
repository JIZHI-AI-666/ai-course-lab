"""跨周导入、数据路径与 .env 加载。

各周脚本开头固定三行：

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import weekpath; weekpath.load_env()
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "week03_Python", "data")


def _register():
    paths = [ROOT]
    if os.path.isdir(ROOT):
        for name in sorted(os.listdir(ROOT)):
            path = os.path.join(ROOT, name)
            if os.path.isdir(path) and name.startswith("week"):
                paths.append(path)
    for path in paths:
        if path not in sys.path:
            sys.path.insert(0, path)


def root_path(*parts):
    return os.path.join(ROOT, *parts)


def data_path(*parts):
    return os.path.join(DATA_DIR, *parts)


def load_env():
    """读取仓库根目录 .env；没有 python-dotenv 时按 KEY=VALUE 解析。"""
    env_file = os.path.join(ROOT, ".env")
    if not os.path.exists(env_file):
        return False
    try:
        from dotenv import load_dotenv
    except ImportError:
        with open(env_file, encoding="utf-8") as file:
            for raw_line in file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
        return True
    load_dotenv(env_file, override=False)
    return True


_register()
