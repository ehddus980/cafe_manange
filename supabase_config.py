"""
Supabase 설정 파일
카페 관리 시스템을 Supabase PostgreSQL과 연결하기 위한 설정
"""

import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# Supabase 설정
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://azbainuzywfzfpijammw.supabase.co')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

# PostgreSQL 연결 설정 (Supabase)
DB_HOST = os.environ.get('DB_HOST', 'db.azbainuzywfzfpijammw.supabase.co')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'postgres')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

# 데이터베이스 URI 구성
def get_database_uri():
    """데이터베이스 타입에 따라 URI를 반환"""
    database_type = os.environ.get('DATABASE_TYPE', 'supabase')
    
    if database_type == 'supabase':
        # Supabase PostgreSQL 연결
        return f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    else:
        # 로컬 SQLite 연결 (기본값)
        return 'sqlite:///cafe.db'

# Supabase 설정 검증
def validate_supabase_config():
    """Supabase 설정이 올바른지 검증"""
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  경고: 다음 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("📝 .env 파일에 Supabase 설정을 추가하세요:")
        print("SUPABASE_URL=https://your-project.supabase.co")
        print("SUPABASE_ANON_KEY=your-anon-key")
        print("SUPABASE_SERVICE_ROLE_KEY=your-service-role-key")
        return False
    
    return True

# RLS 정책 설정
RLS_POLICIES = {
    'cafe_menu': {
        'select': 'true',  # 모든 사용자가 메뉴를 볼 수 있음
        'insert': 'auth.role() = \'authenticated\'',  # 인증된 사용자만 추가 가능
        'update': 'auth.role() = \'authenticated\'',  # 인증된 사용자만 수정 가능
        'delete': 'auth.role() = \'authenticated\''   # 인증된 사용자만 삭제 가능
    },
    'cafe_order': {
        'select': 'auth.role() = \'authenticated\'',
        'insert': 'auth.role() = \'authenticated\'',
        'update': 'auth.role() = \'authenticated\'',
        'delete': 'auth.role() = \'authenticated\''
    },
    'cafe_order_item': {
        'select': 'auth.role() = \'authenticated\'',
        'insert': 'auth.role() = \'authenticated\'',
        'update': 'auth.role() = \'authenticated\'',
        'delete': 'auth.role() = \'authenticated\''
    }
}

# 테이블 스키마 정보
TABLE_SCHEMAS = {
    'cafe_menu': {
        'columns': [
            'id SERIAL PRIMARY KEY',
            'name VARCHAR(100) NOT NULL',
            'category VARCHAR(50) NOT NULL',
            'price DECIMAL(10,2) NOT NULL',
            'description TEXT',
            'image VARCHAR(255)',
            'temperature_option VARCHAR(20) DEFAULT \'both\'',
            'display_order INTEGER DEFAULT 9999',
            'is_soldout BOOLEAN DEFAULT FALSE',
            'created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()',
            'updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()'
        ],
        'indexes': [
            'CREATE INDEX idx_menu_category ON cafe_menu(category)',
            'CREATE INDEX idx_menu_display_order ON cafe_menu(display_order)'
        ]
    },
    'cafe_order': {
        'columns': [
            'id SERIAL PRIMARY KEY',
            'order_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()',
            'status VARCHAR(20) NOT NULL DEFAULT \'pending\'',
            'total_amount INTEGER NOT NULL',
            'customer_name VARCHAR(50) NOT NULL',
            'delivery_location VARCHAR(100) NOT NULL',
            'delivery_time VARCHAR(50)',
            'order_request TEXT',
            'created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()',
            'updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()'
        ],
        'indexes': [
            'CREATE INDEX idx_order_date ON cafe_order(order_date)',
            'CREATE INDEX idx_order_status ON cafe_order(status)'
        ]
    },
    'cafe_order_item': {
        'columns': [
            'id SERIAL PRIMARY KEY',
            'order_id INTEGER NOT NULL REFERENCES cafe_order(id) ON DELETE CASCADE',
            'menu_id INTEGER NOT NULL REFERENCES cafe_menu(id) ON DELETE CASCADE',
            'quantity INTEGER NOT NULL',
            'subtotal DECIMAL(10,2) NOT NULL',
            'special_request TEXT',
            'temperature VARCHAR(10) DEFAULT \'ice\'',
            'created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()'
        ],
        'indexes': [
            'CREATE INDEX idx_order_item_order_id ON cafe_order_item(order_id)',
            'CREATE INDEX idx_order_item_menu_id ON cafe_order_item(menu_id)'
        ]
    }
}

if __name__ == "__main__":
    # 설정 검증
    if validate_supabase_config():
        print("✅ Supabase 설정이 올바르게 구성되었습니다.")
        print(f"📊 데이터베이스 URI: {get_database_uri()}")
    else:
        print("❌ Supabase 설정을 확인해주세요.") 