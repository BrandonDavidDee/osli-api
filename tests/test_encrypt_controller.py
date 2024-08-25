# type: ignore
import pytest
from app.controller import KeyEncryptionController
import base64

data = "data-to-be-encrypted"
passphrase = "user_passphrase"
salt = "test_salt"


@pytest.fixture
def encryption_controller():
    return KeyEncryptionController()


class TestKeyEncryptionController:
    def test_encode_passphrase(self, encryption_controller):
        encoded = encryption_controller.encode_passphrase(passphrase)
        assert isinstance(encoded, bytes)
        assert len(encoded) == 44  # Base64 encoding of 32 bytes = 44 chars

    def test_get_salt_with_valid_salt(self, encryption_controller):
        encoded_salt = encryption_controller.get_salt(salt)

        assert isinstance(encoded_salt, bytes)
        assert len(encoded_salt) == 44

    def test_get_salt_without_salt(self, encryption_controller):
        with pytest.raises(ValueError, match="No salt provided"):
            encryption_controller.get_salt(None)

    def test_encrypt_and_decrypt(self, encryption_controller):
        encrypted = encryption_controller.encrypt(data, passphrase, salt)
        assert isinstance(encrypted, str)
        decoded_encrypted = base64.urlsafe_b64decode(encrypted.encode("utf-8"))
        assert len(decoded_encrypted) > len(salt)  # The output should be longer than the salt
        decrypted = encryption_controller.decrypt(encrypted, passphrase, salt)
        assert decrypted == data

    def test_encrypt_and_decrypt_api_key(self, encryption_controller):
        encrypted_key = encryption_controller.encrypt_api_key(data, passphrase)
        assert isinstance(encrypted_key, str)
        decrypted_key = encryption_controller.decrypt_api_key(encrypted_key, passphrase)
        assert decrypted_key == data

    def test_encrypt_and_decrypt_api_secret(self, encryption_controller):
        encrypted_key = encryption_controller.encrypt_api_secret(data, passphrase)
        assert isinstance(encrypted_key, str)
        decrypted_key = encryption_controller.decrypt_api_secret(encrypted_key, passphrase)
        assert decrypted_key == data

    def test_encrypt_and_decrypt_access_token(self, encryption_controller):
        encrypted_key = encryption_controller.encrypt_access_token(data, passphrase)
        assert isinstance(encrypted_key, str)
        decrypted_key = encryption_controller.decrypt_access_token(encrypted_key, passphrase)
        assert decrypted_key == data
