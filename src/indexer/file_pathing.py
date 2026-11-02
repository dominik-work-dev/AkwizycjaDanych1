import os

PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DOCS_FOLDER: str = os.path.join(PROJECT_ROOT, "folder_z_dokumentami")
DEFAULT_DB_PATH: str = os.path.join(PROJECT_ROOT, "data", "index.db")

def to_project_path(path: str) -> str:
    full_path = os.path.abspath(path)
    try:
        relative = os.path.relpath(full_path, PROJECT_ROOT)
    except ValueError:
        return full_path
    if relative.startswith(".."):
        return full_path
    return relative


def to_full_path(path: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.join(PROJECT_ROOT, path)