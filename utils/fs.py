import os


def make_dirs(path: str) -> None:
    path = path.strip()
    if not os.path.exists(path):
        os.makedirs(path)
