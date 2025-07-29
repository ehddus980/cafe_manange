import os
from datetime import timedelta

# 데이터베이스 설정
# 환경변수로 데이터베이스 타입 선택 가능
DATABASE_TYPE = os.environ.get('DATABASE_TYPE', 'sqlite')  # 'sqlite' 또는 'postgresql'

if DATABASE_TYPE == 'postgresql':
    # PostgreSQL 설정 (환경변수에서 가져옴)
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'cafe_db')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
else:
    # SQLite 설정 (기본값)
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
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')  # 실제 운영시에는 환경변수로 관리 