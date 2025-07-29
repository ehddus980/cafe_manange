import os
from datetime import timedelta

# 데이터베이스 설정
SQLALCHEMY_DATABASE_URI = 'sqlite:///cafe.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 파일 업로드 설정
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 세션 설정
PERMANENT_SESSION_LIFETIME = timedelta(days=1)
SESSION_TYPE = 'filesystem'

# 보안 설정
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

# 관리자 계정 설정
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'  # 실제 운영시에는 환경변수로 관리 