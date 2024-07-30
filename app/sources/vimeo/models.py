from app.sources.models import SourceBase


class SourceVimeo(SourceBase):
    client_identifier: str
    client_secret: str
    access_token: str
