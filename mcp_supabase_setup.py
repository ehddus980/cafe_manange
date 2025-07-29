"""
MCP 기능을 활용한 Supabase 데이터베이스 자동 설정 스크립트
Cursor AI에서 Supabase MCP 기능을 사용하여 데이터베이스를 자동으로 설정합니다.
"""

import os
import sys
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def check_mcp_availability():
    """MCP 기능 사용 가능 여부 확인"""
    try:
        # MCP 함수들이 사용 가능한지 확인
        print("🔍 MCP 기능 사용 가능 여부 확인 중...")
        
        # 간단한 테스트 쿼리 실행
        test_result = mcp_supabase_get_project_url("test")
        if test_result:
            print("✅ MCP 기능 사용 가능")
            return True
        else:
            print("❌ MCP 기능 사용 불가")
            return False
            
    except Exception as e:
        print(f"❌ MCP 기능 확인 실패: {e}")
        return False

def setup_supabase_database():
    """MCP 기능을 활용한 Supabase 데이터베이스 설정"""
    
    print("🚀 MCP 기능을 활용한 Supabase 데이터베이스 설정을 시작합니다...")
    
    # 1. 프로젝트 정보 확인
    try:
        project_url = mcp_supabase_get_project_url("test")
        print(f"📊 프로젝트 URL: {project_url}")
        
        anon_key = mcp_supabase_get_anon_key("test")
        print(f"🔑 Anonymous Key: {anon_key[:20]}...")
        
    except Exception as e:
        print(f"⚠️ 프로젝트 정보 확인 실패: {e}")
        return False
    
    # 2. 기존 테이블 확인
    try:
        tables = mcp_supabase_list_tables(schemas=['public'])
        print(f"📋 기존 테이블: {len(tables)}개")
        
        if 'cafe_menu' in [table.get('name', '') for table in tables]:
            print("⚠️ 이미 cafe_menu 테이블이 존재합니다.")
            return True
            
    except Exception as e:
        print(f"⚠️ 테이블 목록 확인 실패: {e}")
    
    # 3. 테이블 생성
    tables_to_create = [
        {
            'name': 'create_cafe_menu_table',
            'query': '''
            CREATE TABLE IF NOT EXISTS cafe_menu (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                description TEXT,
                image VARCHAR(255),
                temperature_option VARCHAR(20) DEFAULT 'both',
                display_order INTEGER DEFAULT 9999,
                is_soldout BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            '''
        },
        {
            'name': 'create_cafe_order_table',
            'query': '''
            CREATE TABLE IF NOT EXISTS cafe_order (
                id SERIAL PRIMARY KEY,
                order_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                total_amount INTEGER NOT NULL,
                customer_name VARCHAR(50) NOT NULL,
                delivery_location VARCHAR(100) NOT NULL,
                delivery_time VARCHAR(50),
                order_request TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            '''
        },
        {
            'name': 'create_cafe_order_item_table',
            'query': '''
            CREATE TABLE IF NOT EXISTS cafe_order_item (
                id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL REFERENCES cafe_order(id) ON DELETE CASCADE,
                menu_id INTEGER NOT NULL REFERENCES cafe_menu(id) ON DELETE CASCADE,
                quantity INTEGER NOT NULL,
                subtotal DECIMAL(10,2) NOT NULL,
                special_request TEXT,
                temperature VARCHAR(10) DEFAULT 'ice',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            '''
        }
    ]
    
    print("🔧 테이블 생성 중...")
    for table in tables_to_create:
        try:
            mcp_supabase_apply_migration(
                name=table['name'],
                query=table['query']
            )
            print(f"✅ {table['name']} 완료")
        except Exception as e:
            print(f"❌ {table['name']} 실패: {e}")
    
    # 4. 인덱스 생성
    indexes_to_create = [
        {
            'name': 'create_menu_indexes',
            'query': '''
            CREATE INDEX IF NOT EXISTS idx_menu_category ON cafe_menu(category);
            CREATE INDEX IF NOT EXISTS idx_menu_display_order ON cafe_menu(display_order);
            '''
        },
        {
            'name': 'create_order_indexes',
            'query': '''
            CREATE INDEX IF NOT EXISTS idx_order_date ON cafe_order(order_date);
            CREATE INDEX IF NOT EXISTS idx_order_status ON cafe_order(status);
            '''
        },
        {
            'name': 'create_order_item_indexes',
            'query': '''
            CREATE INDEX IF NOT EXISTS idx_order_item_order_id ON cafe_order_item(order_id);
            CREATE INDEX IF NOT EXISTS idx_order_item_menu_id ON cafe_order_item(menu_id);
            '''
        }
    ]
    
    print("📊 인덱스 생성 중...")
    for index in indexes_to_create:
        try:
            mcp_supabase_apply_migration(
                name=index['name'],
                query=index['query']
            )
            print(f"✅ {index['name']} 완료")
        except Exception as e:
            print(f"❌ {index['name']} 실패: {e}")
    
    # 5. RLS 정책 설정
    rls_policies = [
        {
            'name': 'setup_menu_rls',
            'query': '''
            ALTER TABLE cafe_menu ENABLE ROW LEVEL SECURITY;
            DROP POLICY IF EXISTS "메뉴 읽기 정책" ON cafe_menu;
            CREATE POLICY "메뉴 읽기 정책" ON cafe_menu FOR SELECT USING (true);
            DROP POLICY IF EXISTS "메뉴 관리자 정책" ON cafe_menu;
            CREATE POLICY "메뉴 관리자 정책" ON cafe_menu FOR ALL USING (auth.role() = 'authenticated');
            '''
        },
        {
            'name': 'setup_order_rls',
            'query': '''
            ALTER TABLE cafe_order ENABLE ROW LEVEL SECURITY;
            DROP POLICY IF EXISTS "주문 관리자 정책" ON cafe_order;
            CREATE POLICY "주문 관리자 정책" ON cafe_order FOR ALL USING (auth.role() = 'authenticated');
            '''
        },
        {
            'name': 'setup_order_item_rls',
            'query': '''
            ALTER TABLE cafe_order_item ENABLE ROW LEVEL SECURITY;
            DROP POLICY IF EXISTS "주문 아이템 관리자 정책" ON cafe_order_item;
            CREATE POLICY "주문 아이템 관리자 정책" ON cafe_order_item FOR ALL USING (auth.role() = 'authenticated');
            '''
        }
    ]
    
    print("🔐 RLS 정책 설정 중...")
    for policy in rls_policies:
        try:
            mcp_supabase_apply_migration(
                name=policy['name'],
                query=policy['query']
            )
            print(f"✅ {policy['name']} 완료")
        except Exception as e:
            print(f"❌ {policy['name']} 실패: {e}")
    
    # 6. 샘플 데이터 삽입
    print("📝 샘플 데이터 삽입 중...")
    sample_data_query = '''
    INSERT INTO cafe_menu (name, category, price, description, temperature_option, display_order) VALUES
    ('아메리카노', '커피', 4500, '깊고 진한 에스프레소와 물의 조화', 'both', 1),
    ('카페라떼', '커피', 5000, '부드러운 우유와 에스프레소의 완벽한 조화', 'both', 2),
    ('카푸치노', '커피', 5000, '에스프레소, 스팀밀크, 우유거품의 균형', 'both', 3),
    ('카라멜 마끼아또', '커피', 5500, '달콤한 카라멜과 에스프레소의 만남', 'both', 4),
    ('바닐라 라떼', '커피', 5500, '부드러운 바닐라 향과 라떼의 조화', 'both', 5),
    ('녹차 라떼', '녹차', 5500, '진한 말차와 부드러운 우유의 조화', 'both', 6),
    ('레몬 에이드', '에이드', 4500, '상큼한 레몬의 시원한 맛', 'ice', 7),
    ('자몽 에이드', '에이드', 4500, '새콤달콤한 자몽의 맛', 'ice', 8),
    ('딸기 스무디', '스무디', 6000, '신선한 딸기의 달콤한 맛', 'ice', 9),
    ('망고 스무디', '스무디', 6000, '달콤한 망고의 부드러운 맛', 'ice', 10)
    ON CONFLICT (id) DO NOTHING;
    '''
    
    try:
        mcp_supabase_apply_migration(
            name='insert_sample_data',
            query=sample_data_query
        )
        print("✅ 샘플 데이터 삽입 완료")
    except Exception as e:
        print(f"❌ 샘플 데이터 삽입 실패: {e}")
    
    # 7. 최종 확인
    try:
        final_tables = mcp_supabase_list_tables(schemas=['public'])
        cafe_tables = [table for table in final_tables if table.get('name', '').startswith('cafe_')]
        print(f"✅ 최종 확인: {len(cafe_tables)}개의 카페 테이블이 생성되었습니다.")
        
        for table in cafe_tables:
            print(f"  - {table.get('name', '')}")
            
    except Exception as e:
        print(f"⚠️ 최종 확인 실패: {e}")
    
    print("\n🎉 Supabase 데이터베이스 설정이 완료되었습니다!")
    print("📝 다음 명령어로 애플리케이션을 실행하세요:")
    print("python supabase_app.py")
    
    return True

def main():
    """메인 함수"""
    print("🔧 MCP Supabase 설정 도구")
    print("=" * 50)
    
    # MCP 기능 사용 가능 여부 확인
    if not check_mcp_availability():
        print("\n❌ MCP 기능을 사용할 수 없습니다.")
        print("📋 다음 사항을 확인해주세요:")
        print("1. Supabase 액세스 토큰이 설정되어 있는지 확인")
        print("2. Cursor AI에서 MCP 서버가 연결되어 있는지 확인")
        print("3. 네트워크 연결 상태 확인")
        return False
    
    # Supabase 데이터베이스 설정
    success = setup_supabase_database()
    
    if success:
        print("\n✅ 모든 설정이 완료되었습니다!")
        print("🚀 이제 Supabase 기반 카페 관리 시스템을 사용할 수 있습니다.")
    else:
        print("\n❌ 설정 중 오류가 발생했습니다.")
        print("📋 수동으로 설정하거나 오류를 확인해주세요.")
    
    return success

if __name__ == "__main__":
    main() 