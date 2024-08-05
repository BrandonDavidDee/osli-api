import mimetypes
import os
import random
import string
import urllib.parse
from datetime import datetime, timezone

from cryptography.fernet import Fernet

from app.authentication.models import AccessTokenData
from app.db import db


class BaseController:
    def __init__(self, token_data: AccessTokenData):
        # token_data isn't really doing anything yet, but is being structured like this for
        # multi-tenant database pooling and / or for possible permissions restrictions in the future.
        self.now = datetime.now(tz=timezone.utc)
        self.token_data = token_data
        self.db = db

    @staticmethod
    def get_filename(path):
        return os.path.basename(path)

    @staticmethod
    def get_mime_type(filename):
        mime_type, _ = mimetypes.guess_type(filename, strict=False)
        return mime_type

    @staticmethod
    def encrypt_api_key(api_key, passphrase):
        fernet = Fernet(passphrase)
        return fernet.encrypt(api_key.encode())

    @staticmethod
    def decrypt_api_key(encrypted_api_key, passphrase):
        fernet = Fernet(passphrase)
        return fernet.decrypt(encrypted_api_key).decode()

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
