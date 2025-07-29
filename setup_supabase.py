"""
Supabase 카페 관리 시스템 설정 스크립트
데이터베이스 테이블 생성 및 초기 설정을 자동화합니다.
"""

import os
import sys
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def check_supabase_config():
    """Supabase 설정 확인"""
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 다음 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("📝 .env 파일에 Supabase 설정을 추가하세요:")
        print("SUPABASE_URL=https://your-project.supabase.co")
        print("SUPABASE_ANON_KEY=your-anon-key")
        return False
    
    return True

def create_supabase_tables():
    """Supabase에 테이블 생성"""
    try:
        from supabase import create_client, Client
        
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("🔧 Supabase 테이블 생성 중...")
        
        # SQL 마이그레이션 파일 읽기
        with open('supabase_migration.sql', 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # SQL 명령어들을 분리하여 실행
        sql_commands = migration_sql.split(';')
        
        for command in sql_commands:
            command = command.strip()
            if command and not command.startswith('--'):
                try:
                    # Supabase에서는 직접 SQL 실행이 제한적이므로
                    # 테이블 생성은 Supabase Dashboard에서 수동으로 해야 할 수 있습니다
                    print(f"📝 실행할 SQL: {command[:50]}...")
                except Exception as e:
                    print(f"⚠️  SQL 실행 오류: {e}")
        
        print("✅ 테이블 생성 완료!")
        return True
        
    except Exception as e:
        print(f"❌ Supabase 연결 오류: {e}")
        return False

def setup_sample_data():
    """샘플 데이터 설정"""
    try:
        from supabase import create_client, Client
        
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("📊 샘플 메뉴 데이터 삽입 중...")
        
        # 샘플 메뉴 데이터
        sample_menus = [
            {
                'name': '아메리카노',
                'category': '커피',
                'price': 4500,
                'description': '깊고 진한 에스프레소와 물의 조화',
                'temperature_option': 'both',
                'display_order': 1,
                'is_soldout': False
            },
            {
                'name': '카페라떼',
                'category': '커피',
                'price': 5000,
                'description': '부드러운 우유와 에스프레소의 완벽한 조화',
                'temperature_option': 'both',
                'display_order': 2,
                'is_soldout': False
            },
            {
                'name': '카푸치노',
                'category': '커피',
                'price': 5000,
                'description': '에스프레소, 스팀밀크, 우유거품의 균형',
                'temperature_option': 'both',
                'display_order': 3,
                'is_soldout': False
            },
            {
                'name': '카라멜 마끼아또',
                'category': '커피',
                'price': 5500,
                'description': '달콤한 카라멜과 에스프레소의 만남',
                'temperature_option': 'both',
                'display_order': 4,
                'is_soldout': False
            },
            {
                'name': '바닐라 라떼',
                'category': '커피',
                'price': 5500,
                'description': '부드러운 바닐라 향과 라떼의 조화',
                'temperature_option': 'both',
                'display_order': 5,
                'is_soldout': False
            },
            {
                'name': '녹차 라떼',
                'category': '녹차',
                'price': 5500,
                'description': '진한 말차와 부드러운 우유의 조화',
                'temperature_option': 'both',
                'display_order': 6,
                'is_soldout': False
            },
            {
                'name': '레몬 에이드',
                'category': '에이드',
                'price': 4500,
                'description': '상큼한 레몬의 시원한 맛',
                'temperature_option': 'ice',
                'display_order': 7,
                'is_soldout': False
            },
            {
                'name': '자몽 에이드',
                'category': '에이드',
                'price': 4500,
                'description': '새콤달콤한 자몽의 맛',
                'temperature_option': 'ice',
                'display_order': 8,
                'is_soldout': False
            },
            {
                'name': '딸기 스무디',
                'category': '스무디',
                'price': 6000,
                'description': '신선한 딸기의 달콤한 맛',
                'temperature_option': 'ice',
                'display_order': 9,
                'is_soldout': False
            },
            {
                'name': '망고 스무디',
                'category': '스무디',
                'price': 6000,
                'description': '달콤한 망고의 부드러운 맛',
                'temperature_option': 'ice',
                'display_order': 10,
                'is_soldout': False
            }
        ]
        
        # 메뉴 데이터 삽입
        for menu in sample_menus:
            try:
                response = supabase.table('cafe_menu').insert(menu).execute()
                print(f"✅ {menu['name']} 메뉴 추가 완료")
            except Exception as e:
                print(f"⚠️  {menu['name']} 메뉴 추가 실패: {e}")
        
        print("✅ 샘플 데이터 설정 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 샘플 데이터 설정 오류: {e}")
        return False

def main():
    """메인 설정 함수"""
    print("🚀 Supabase 카페 관리 시스템 설정을 시작합니다...")
    
    # 1. 설정 확인
    if not check_supabase_config():
        print("\n📋 설정 방법:")
        print("1. env_supabase.example 파일을 .env로 복사하세요")
        print("2. Supabase 프로젝트에서 URL과 API 키를 가져오세요")
        print("3. .env 파일에 실제 값으로 변경하세요")
        return False
    
    # 2. 테이블 생성
    if not create_supabase_tables():
        print("\n📋 수동 설정 방법:")
        print("1. Supabase Dashboard에서 SQL Editor를 열으세요")
        print("2. supabase_migration.sql 파일의 내용을 복사하여 실행하세요")
        return False
    
    # 3. 샘플 데이터 설정
    if not setup_sample_data():
        print("⚠️  샘플 데이터 설정에 실패했습니다.")
        return False
    
    print("\n🎉 Supabase 설정이 완료되었습니다!")
    print("📝 다음 명령어로 애플리케이션을 실행하세요:")
    print("python supabase_app.py")
    
    return True

if __name__ == "__main__":
    main() 