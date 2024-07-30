import mimetypes

import boto3
from cryptography.fernet import Fernet

from app.authentication.models import AccessTokenData
from app.db import db


class BaseController:
    def __init__(self, token_data: AccessTokenData):
        self.token_data = token_data
        self.db = db

    @staticmethod
    def get_mime_type(filename):
        mime_type, _ = mimetypes.guess_type(filename, strict=False)
        return mime_type

    @staticmethod
    def get_s3_client(aws_access_key_id: str, aws_secret_access_key: str):
        return boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    @staticmethod
    def encrypt_api_key(api_key, passphrase):
        fernet = Fernet(passphrase)
        return fernet.encrypt(api_key.encode())

    @staticmethod
    def decrypt_api_key(encrypted_api_key, passphrase):
        fernet = Fernet(passphrase)
        return fernet.decrypt(encrypted_api_key).decode()
