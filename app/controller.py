import base64
import mimetypes
import os
import random
import string
import urllib.parse
import uuid
from datetime import datetime, timezone

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException

from app.authentication.models import AccessTokenData
from app.db import db


class KeyEncryptionController:
    def __init__(self):
        self.api_key_salt: str | None = os.getenv("API_KEY_SALT")
        self.api_secret_salt: str | None = os.getenv("API_SECRET_SALT")
        self.access_token_salt: str | None = os.getenv("ACCESS_TOKEN_SALT")

    @staticmethod
    def encode_passphrase(key: str) -> bytes:
        return base64.urlsafe_b64encode(key.ljust(32)[:32].encode())

    def get_salt(self, salt) -> bytes:
        if salt is None:
            raise ValueError("No salt provided")
        return self.encode_passphrase(salt)

    def encrypt(self, data, passphrase, salt) -> str:
        encoded_pass: bytes = self.encode_passphrase(passphrase)
        encoded_salt: bytes = self.get_salt(salt)
        fernet = Fernet(encoded_pass)
        encrypted: bytes = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encoded_salt + encrypted).decode("utf-8")

    def decrypt(self, encrypted_data, passphrase, salt) -> str:
        encoded_pass: bytes = self.encode_passphrase(passphrase)
        encoded_salt: bytes = self.get_salt(salt)
        encrypted_data: bytes = base64.urlsafe_b64decode(encrypted_data.encode("utf-8"))
        extracted_salt = encrypted_data[:44]  # 32 bytes encoded to 44 characters
        if extracted_salt != encoded_salt:
            raise ValueError("Invalid salt")
        encrypted = encrypted_data[44:]
        fernet = Fernet(encoded_pass)
        try:
            return fernet.decrypt(encrypted).decode()
        except InvalidToken:
            raise HTTPException(status_code=403, detail="Invalid passphrase")

    def encrypt_api_key(self, api_key: str, passphrase: str) -> str:
        return self.encrypt(api_key, passphrase, self.api_key_salt)

    def encrypt_api_secret(self, api_secret: str, passphrase: str) -> str:
        return self.encrypt(api_secret, passphrase, self.api_secret_salt)

    def encrypt_access_token(self, access_token: str, passphrase: str) -> str:
        return self.encrypt(access_token, passphrase, self.access_token_salt)

    def decrypt_api_key(self, encrypted_api_key: str, passphrase: str) -> str:
        return self.decrypt(encrypted_api_key, passphrase, self.api_key_salt)

    def decrypt_api_secret(self, encrypted_api_secret: str, passphrase: str) -> str:
        return self.decrypt(encrypted_api_secret, passphrase, self.api_secret_salt)

    def decrypt_access_token(self, encrypted_access_token: str, passphrase: str) -> str:
        return self.decrypt(encrypted_access_token, passphrase, self.access_token_salt)


class BaseController:
    def __init__(self, token_data: AccessTokenData):
        # token_data isn't really doing anything yet, but is being structured like this for
        # multi-tenant database pooling and / or for possible permissions restrictions in the future.
        self.now = datetime.now(tz=timezone.utc)
        self.token_data = token_data
        self.db = db

    @staticmethod
    def generate_link():
        return str(uuid.uuid4())

    @staticmethod
    def get_filename(path):
        return os.path.basename(path)

    @staticmethod
    def get_mime_type(filename):
        mime_type, _ = mimetypes.guess_type(filename, strict=False)
        return mime_type

    @staticmethod
    def random_generator(size=4, chars=string.ascii_uppercase + string.digits):
        return "".join(random.choice(chars) for x in range(size))

    def make_safe_filename(self, file_name):
        base_name, extension = os.path.splitext(file_name)
        # Omit random characters and swap spaces with underscores
        safe_base_name = "".join(
            c if c.isalnum() or c in ["-", "_"] else "_" for c in base_name
        )
        # then make it url safe just in case
        url_safe_base_name = urllib.parse.quote_plus(safe_base_name)
        random_string = self.random_generator()
        return f"{url_safe_base_name}{random_string}{extension.lower()}"
