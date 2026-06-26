from app.utils.file_storage import safe_filename, validate_upload_extension


def test_upload_extension_validation() -> None:
    assert validate_upload_extension(".pdf") is True
    assert validate_upload_extension(".exe") is False


def test_safe_filename_removes_path_and_unsafe_chars() -> None:
    assert safe_filename("../../bad file?.txt") == "bad_file_.txt"
