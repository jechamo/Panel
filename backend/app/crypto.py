from pathlib import Path

from cryptography.fernet import Fernet

from .db import DATA_DIR

_KEY_FILE: Path = DATA_DIR / ".master_key"


def _load_or_create_key() -> bytes:
    if _KEY_FILE.exists():
        return _KEY_FILE.read_bytes()
    key = Fernet.generate_key()
    _KEY_FILE.write_bytes(key)
    _KEY_FILE.chmod(0o600)
    return key


_fernet = Fernet(_load_or_create_key())


def encrypt(plaintext: str) -> bytes:
    return _fernet.encrypt(plaintext.encode("utf-8"))


def decrypt(ciphertext: bytes) -> str:
    if not ciphertext:
        return ""
    return _fernet.decrypt(ciphertext).decode("utf-8")
