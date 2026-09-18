import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-in-production")

    # MySQL (XAMPP defaults)
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "abcd@1234")
    MYSQL_DB = os.environ.get("MYSQL_DB", "cafe_db")
    MYSQL_CURSORCLASS = "DictCursor"

    # Uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024  # 4 MB
