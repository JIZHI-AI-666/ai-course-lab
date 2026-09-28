"""项目根目录和 data/ 目录的统一定位工具。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"


def root_path(*parts):
    """返回项目根目录下的路径。"""
    return ROOT.joinpath(*parts)


def data_path(*parts):
    """返回 data/ 目录下的路径，不依赖当前工作目录。"""
    return DATA_DIR.joinpath(*parts)
