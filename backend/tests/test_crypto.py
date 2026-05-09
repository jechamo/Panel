def test_fernet_roundtrip():
    from app.crypto import decrypt, encrypt

    secret = "sk-ant-very-secret-token"
    cipher = encrypt(secret)
    assert isinstance(cipher, bytes)
    assert cipher != secret.encode()
    assert cipher.startswith(b"gAAAA")  # Fernet token prefix
    assert decrypt(cipher) == secret


def test_decrypt_empty_returns_empty():
    from app.crypto import decrypt

    assert decrypt(b"") == ""


def test_master_key_persists_across_imports():
    from app.crypto import encrypt
    from app.db import DATA_DIR

    cipher = encrypt("hello")
    key_file = DATA_DIR / ".master_key"
    assert key_file.exists()
    # Another encryption with the same module should produce decryptable output
    from app.crypto import decrypt

    assert decrypt(cipher) == "hello"
