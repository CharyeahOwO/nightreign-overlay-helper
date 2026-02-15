from pathlib import Path
import os
import sys
import shutil
from datetime import timedelta
from platformdirs import user_data_dir, user_desktop_dir
import yaml
import tomllib


APP_NAME = "nightreign-overlay-helper"
APP_NAME_CHS = "黑夜君临悬浮助手"

def get_version() -> str:
    """从 pyproject.toml 读取版本号，自动适配源码和 PyInstaller 打包环境"""
    # 检测是否为 PyInstaller 打包后的环境
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后：pyproject.toml 在程序根目录（_MEIPASS）
        pyproject_path = Path(sys._MEIPASS) / "pyproject.toml"
    else:
        # 源码环境：pyproject.toml 在项目根目录
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]
    except Exception:
        return "unknown"

APP_VERSION = get_version()
APP_FULLNAME = f"{APP_NAME_CHS}v{APP_VERSION}"
APP_AUTHOR = "NeuraXmy"

GAME_WINDOW_TITLE = "ELDEN RING NIGHTREIGN"


def get_asset_path(path: str) -> str:
    return str(Path("assets") / path)

def get_data_path(path: str) -> str:
    return str(Path("data") / path)

def _is_writable_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        test_file = path / ".write_test"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("ok")
        if test_file.exists():
            test_file.unlink()
        return True
    except Exception:
        return False

def _get_appdata_dir_candidates() -> list[Path]:
    candidates: list[Path] = []
    if appdata := os.getenv("APPDATA"):
        candidates.append(Path(appdata) / APP_NAME)
    if localappdata := os.getenv("LOCALAPPDATA"):
        candidates.append(Path(localappdata) / APP_NAME)
    candidates.append(Path(user_data_dir(appname=APP_NAME, appauthor=APP_AUTHOR)))
    candidates.append(Path.home() / f".{APP_NAME}")
    unique: list[Path] = []
    for path in candidates:
        if path not in unique:
            unique.append(path)
    return unique

def _select_appdata_dir(filename: str) -> Path:
    filename_path = Path(filename) if filename else Path()
    candidates = _get_appdata_dir_candidates()
    for candidate in candidates:
        target = candidate / filename_path
        if target.exists() and _is_writable_dir(candidate):
            return candidate
    for candidate in candidates:
        if _is_writable_dir(candidate):
            for legacy in candidates:
                if legacy == candidate:
                    continue
                legacy_target = legacy / filename_path
                if legacy_target.exists() and legacy_target.is_file():
                    try:
                        target = candidate / filename_path
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(legacy_target, target)
                    except Exception:
                        pass
                    break
            return candidate
    fallback = Path.cwd() / APP_NAME
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback

def get_appdata_path(filename: str) -> str:
    base_dir = _select_appdata_dir(filename)
    if filename:
        return str(base_dir / filename)
    return str(base_dir)

def get_desktop_path(filename: str = "") -> str:
    desktop = Path(user_desktop_dir())
    desktop.mkdir(exist_ok=True)
    return str(desktop / filename) if filename else str(desktop)


ICON_PATH = get_asset_path("icon.ico")


def get_readable_timedelta(t: timedelta) -> str:
    seconds = int(t.total_seconds())
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}小时{minutes}分钟{seconds}秒"
    elif minutes > 0:
        return f"{minutes}分钟{seconds}秒"
    else:
        return f"{seconds}秒"
    

def load_yaml(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Failed to load YAML file {path}: {e}")
        return {}

def save_yaml(path: str, data: dict):
    # 保存到临时文件然后替换，防止写入过程中程序崩溃导致文件损坏
    tmp_path = None
    try:
        dir_name = os.path.dirname(path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True)
        os.replace(tmp_path, path)
    except Exception as e:
        print(f"Failed to save YAML file {path}: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

