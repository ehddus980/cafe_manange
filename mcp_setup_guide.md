# 🔧 Supabase MCP 기능 설정 가이드

Cursor AI에서 Supabase MCP 기능을 사용하기 위한 설정 방법입니다.

## 📋 사전 준비사항

### 1. Supabase 프로젝트 생성
1. [Supabase](https://supabase.com)에 로그인
2. 새 프로젝트 생성
3. 프로젝트 URL과 API 키 확인

### 2. Supabase 액세스 토큰 생성
1. Supabase Dashboard → Settings → API
2. **Access Token** 생성 (Service Role 권한)
3. 토큰을 안전한 곳에 저장

## 🔑 MCP 토큰 설정 방법

### 방법 1: 환경변수 설정
```bash
# Windows
set SUPABASE_ACCESS_TOKEN=your-access-token

# macOS/Linux
export SUPABASE_ACCESS_TOKEN=your-access-token
```

### 방법 2: Cursor AI 설정
1. Cursor AI 설정에서 MCP 서버 설정
2. `--access-token your-access-token` 플래그 추가

### 방법 3: .env 파일 설정
```env
SUPABASE_ACCESS_TOKEN=your-access-token
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

## 🚀 MCP 기능 사용 예제

### 1. 개발 브랜치 생성
```python
# MCP 함수 호출
mcp_supabase_create_branch(
    name="cafe_management_dev",
    confirm_cost_id="confirm"
)
```

### 2. 테이블 목록 조회
```python
# MCP 함수 호출
mcp_supabase_list_tables(schemas=['public'])
```

### 3. 마이그레이션 적용
```python
# MCP 함수 호출
mcp_supabase_apply_migration(
    name="create_cafe_tables",
    query="""
    CREATE TABLE cafe_menu (
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
    """
)
```

## 📊 사용 가능한 MCP 기능들

### 프로젝트 관리
- `mcp_supabase_create_branch` - 개발 브랜치 생성
- `mcp_supabase_list_branches` - 브랜치 목록 조회
- `mcp_supabase_delete_branch` - 브랜치 삭제
- `mcp_supabase_merge_branch` - 브랜치 병합
- `mcp_supabase_reset_branch` - 브랜치 리셋
- `mcp_supabase_rebase_branch` - 브랜치 리베이스

### 데이터베이스 관리
- `mcp_supabase_list_tables` - 테이블 목록 조회
- `mcp_supabase_list_extensions` - 확장 기능 목록
- `mcp_supabase_list_migrations` - 마이그레이션 목록
- `mcp_supabase_apply_migration` - 마이그레이션 적용
- `mcp_supabase_execute_sql` - SQL 실행

### Edge Functions
- `mcp_supabase_list_edge_functions` - Edge Functions 목록
- `mcp_supabase_deploy_edge_function` - Edge Function 배포

### 모니터링 & 로그
- `mcp_supabase_get_logs` - 로그 조회
- `mcp_supabase_get_advisors` - 보안/성능 권고사항

### 개발 도구
- `mcp_supabase_generate_typescript_types` - TypeScript 타입 생성
- `mcp_supabase_search_docs` - 문서 검색

## 🔧 자동화 스크립트

### MCP를 활용한 자동 데이터베이스 설정
```python
import os
from dotenv import load_dotenv

load_dotenv()

def setup_supabase_with_mcp():
    """MCP 기능을 활용한 Supabase 설정"""
    
    # 1. 개발 브랜치 생성
    try:
        mcp_supabase_create_branch(
            name="cafe_management_setup",
            confirm_cost_id="confirm"
        )
        print("✅ 개발 브랜치 생성 완료")
    except Exception as e:
        print(f"⚠️ 브랜치 생성 실패: {e}")
    
    # 2. 테이블 생성
    tables = [
        {
            'name': 'create_cafe_menu',
            'query': '''
            CREATE TABLE cafe_menu (
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
            'name': 'create_cafe_order',
            'query': '''
            CREATE TABLE cafe_order (
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
            'name': 'create_cafe_order_item',
            'query': '''
            CREATE TABLE cafe_order_item (
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
    
    for table in tables:
        try:
            mcp_supabase_apply_migration(
                name=table['name'],
                query=table['query']
            )
            print(f"✅ {table['name']} 테이블 생성 완료")
        except Exception as e:
            print(f"⚠️ {table['name']} 테이블 생성 실패: {e}")
    
    # 3. 인덱스 생성
    indexes = [
        {
            'name': 'create_menu_indexes',
            'query': '''
            CREATE INDEX idx_menu_category ON cafe_menu(category);
            CREATE INDEX idx_menu_display_order ON cafe_menu(display_order);
            '''
        },
        {
            'name': 'create_order_indexes',
            'query': '''
            CREATE INDEX idx_order_date ON cafe_order(order_date);
            CREATE INDEX idx_order_status ON cafe_order(status);
            '''
        },
        {
            'name': 'create_order_item_indexes',
            'query': '''
            CREATE INDEX idx_order_item_order_id ON cafe_order_item(order_id);
            CREATE INDEX idx_order_item_menu_id ON cafe_order_item(menu_id);
            '''
        }
    ]
    
    for index in indexes:
        try:
            mcp_supabase_apply_migration(
                name=index['name'],
                query=index['query']
            )
            print(f"✅ {index['name']} 인덱스 생성 완료")
        except Exception as e:
            print(f"⚠️ {index['name']} 인덱스 생성 실패: {e}")
    
    # 4. RLS 정책 설정
    rls_policies = [
        {
            'name': 'setup_menu_rls',
            'query': '''
            ALTER TABLE cafe_menu ENABLE ROW LEVEL SECURITY;
            CREATE POLICY "메뉴 읽기 정책" ON cafe_menu FOR SELECT USING (true);
            CREATE POLICY "메뉴 관리자 정책" ON cafe_menu FOR ALL USING (auth.role() = 'authenticated');
            '''
        },
        {
            'name': 'setup_order_rls',
            'query': '''
            ALTER TABLE cafe_order ENABLE ROW LEVEL SECURITY;
            CREATE POLICY "주문 관리자 정책" ON cafe_order FOR ALL USING (auth.role() = 'authenticated');
            '''
        },
        {
            'name': 'setup_order_item_rls',
            'query': '''
            ALTER TABLE cafe_order_item ENABLE ROW LEVEL SECURITY;
            CREATE POLICY "주문 아이템 관리자 정책" ON cafe_order_item FOR ALL USING (auth.role() = 'authenticated');
            '''
        }
    ]
    
    for policy in rls_policies:
        try:
            mcp_supabase_apply_migration(
                name=policy['name'],
                query=policy['query']
            )
            print(f"✅ {policy['name']} RLS 정책 설정 완료")
        except Exception as e:
            print(f"⚠️ {policy['name']} RLS 정책 설정 실패: {e}")
    
    print("🎉 Supabase 데이터베이스 설정 완료!")

if __name__ == "__main__":
    setup_supabase_with_mcp()
```

## 🐛 문제 해결

### 1. 토큰 인증 오류
```
Unauthorized. Please provide a valid access token
```
**해결방법:**
- Supabase Dashboard에서 새로운 액세스 토큰 생성
- 환경변수에 올바른 토큰 설정
- Cursor AI 재시작

### 2. MCP 서버 연결 오류
**해결방법:**
- Cursor AI 설정에서 MCP 서버 확인
- 네트워크 연결 상태 확인
- 방화벽 설정 확인

### 3. 권한 부족 오류
**해결방법:**
- Service Role 권한이 있는 토큰 사용
- 프로젝트 소유자 권한 확인

## 📞 지원

- **Supabase 문서**: https://supabase.com/docs
- **MCP 문서**: https://modelcontextprotocol.io
- **Cursor AI 문서**: https://cursor.sh/docs

---

**🚀 MCP 기능을 활용하여 Supabase 데이터베이스를 자동으로 설정해보세요!** 