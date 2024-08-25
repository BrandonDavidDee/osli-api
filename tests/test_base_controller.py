# type: ignore
import pytest
import string
from app.controller import BaseController
from app.authentication.models import AccessTokenData

token_data = AccessTokenData(user_id="1")


@pytest.fixture
def base_controller():
    return BaseController(token_data)


class TestBaseController:
    def test_generate_link(self, base_controller):
        link = base_controller.generate_link()
        assert isinstance(link, str)

    def test_get_filename(self, base_controller):
        path = "/some/directory/file.txt"
        expected_filename = "file.txt"
        filename = base_controller.get_filename(path)
        assert filename == expected_filename

    def test_get_mime_type_with_valid_filename(self, base_controller):
        filename = "file.txt"
        expected_mime_type = "text/plain"
        mime_type = base_controller.get_mime_type(filename)
        assert mime_type == expected_mime_type

    def test_get_mime_type_with_invalid_filename(self, base_controller):
        filename = "file.unknownextension"
        expected_mime_type = None
        mime_type = base_controller.get_mime_type(filename)
        assert mime_type == expected_mime_type

    def test_get_mime_type_with_none(self, base_controller):
        assert base_controller.get_mime_type(None) is None

    def test_random_generator(self, base_controller):
        size = 10
        result = base_controller.random_generator(size=size)
        assert len(result) == size
        assert all(c in string.ascii_uppercase + string.digits for c in result)

    def test_random_generator_randomness(self, base_controller):
        result1 = base_controller.random_generator()
        result2 = base_controller.random_generator()
        assert result1 != result2
