import os

from cryptography.fernet import Fernet

from app.masking.base_strategy import MaskingStrategy

KEYFILE_PATH = os.getenv("FERNET_KEY_PATH", ".keyfile")


def _load_or_generate_key() -> bytes:
    if os.path.exists(KEYFILE_PATH):
        with open(KEYFILE_PATH, "rb") as f:
            return f.read().strip()
    key = Fernet.generate_key()
    with open(KEYFILE_PATH, "wb") as f:
        f.write(key)
    try:
        os.chmod(KEYFILE_PATH, 0o600)
    except (AttributeError, OSError):
        pass
    return key


FERNET_KEY = _load_or_generate_key()
_cipher = Fernet(FERNET_KEY)


class AESStrategy(MaskingStrategy):
    @property
    def name(self) -> str:
        return "encriptacion"

    @property
    def reversible(self) -> bool:
        return True

    def mask(self, value: str) -> str:
        token = _cipher.encrypt(value.encode("utf-8"))
        return f"enc::{token.decode('utf-8')[:30]}..."

    @staticmethod
    def encrypt_raw(value: str) -> str:
        return _cipher.encrypt(value.encode("utf-8")).decode("utf-8")

    @staticmethod
    def decrypt_raw(token: str) -> str:
        return _cipher.decrypt(token.encode("utf-8")).decode("utf-8")
