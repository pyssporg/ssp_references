from __future__ import annotations


def setup_directory(*args, **kwargs):
    from .setup import setup_directory as _setup_directory

    return _setup_directory(*args, **kwargs)


__all__ = ["setup_directory"]
