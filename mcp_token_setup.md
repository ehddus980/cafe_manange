# 🔑 MCP Supabase 토큰 설정 가이드

Cursor AI에서 Supabase MCP 기능을 사용하기 위한 액세스 토큰 설정 방법입니다.

## 📋 1단계: Supabase 액세스 토큰 생성

### 1. Supabase Dashboard 접속
1. [Supabase](https://supabase.com)에 로그인
2. 프로젝트 선택 또는 새 프로젝트 생성

### 2. 액세스 토큰 생성
1. **Settings** → **API** 메뉴로 이동
2. **Access Tokens** 섹션에서 **Generate new token** 클릭
3. 토큰 이름 입력 (예: "MCP Access Token")
4. **Service Role** 권한 선택
5. **Generate token** 클릭
6. 생성된 토큰을 안전한 곳에 복사

## 🔧 2단계: Cursor AI에서 토큰 설정

### 방법 1: 환경변수 설정 (권장)

#### Windows
```cmd
set SUPABASE_ACCESS_TOKEN=your-access-token-here
```

#### macOS/Linux
```bash
export SUPABASE_ACCESS_TOKEN=your-access-token-here
```

### 방법 2: .env 파일 설정
```env
SUPABASE_ACCESS_TOKEN=your-access-token-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### 방법 3: Cursor AI 설정
1. Cursor AI 설정에서 MCP 서버 설정
2. `--access-token your-access-token-here` 플래그 추가

## 🧪 3단계: 토큰 테스트

### 테스트 스크립트 실행
```bash
python mcp_supabase_setup.py
```

### 수동 테스트
```python
# Python에서 직접 테스트
import os
from dotenv import load_dotenv

load_dotenv()

# 토큰 확인
token = os.environ.get('SUPABASE_ACCESS_TOKEN')
print(f"토큰 설정됨: {'예' if token else '아니오'}")

if token:
    print(f"토큰 길이: {len(token)}")
    print(f"토큰 시작: {token[:10]}...")
```

## 🔍 4단계: MCP 기능 테스트

### 기본 기능 테스트
```python
# 프로젝트 URL 확인
project_url = mcp_supabase_get_project_url("test")
print(f"프로젝트 URL: {project_url}")

# 테이블 목록 확인
tables = mcp_supabase_list_tables(schemas=['public'])
print(f"테이블 개수: {len(tables)}")

# 브랜치 목록 확인
branches = mcp_supabase_list_branches("test")
print(f"브랜치 개수: {len(branches)}")
```

## 🚀 5단계: 데이터베이스 생성

### 자동 설정 스크립트 실행
```bash
# 전체 데이터베이스 설정
python mcp_supabase_setup.py
```

### 수동 설정 (단계별)
```python
# 1. 메뉴 테이블 생성
mcp_supabase_apply_migration(
    name="create_cafe_menu",
    query="""
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
    """
)

# 2. 주문 테이블 생성
mcp_supabase_apply_migration(
    name="create_cafe_order",
    query="""
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
    """
)

# 3. 주문 아이템 테이블 생성
mcp_supabase_apply_migration(
    name="create_cafe_order_item",
    query="""
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
    """
)
```

## 🐛 문제 해결

### 1. "Unauthorized" 오류
```
Unauthorized. Please provide a valid access token
```

**해결방법:**
- 토큰이 올바르게 설정되었는지 확인
- 토큰이 만료되지 않았는지 확인
- Service Role 권한이 있는 토큰인지 확인

### 2. "Token not found" 오류
```
Token not found in environment variables
```

**해결방법:**
- 환경변수 이름이 정확한지 확인 (`SUPABASE_ACCESS_TOKEN`)
- Cursor AI를 재시작
- 터미널을 재시작

### 3. "Invalid token" 오류
```
Invalid access token
```

**해결방법:**
- Supabase Dashboard에서 새 토큰 생성
- 토큰을 복사할 때 공백이 포함되지 않았는지 확인
- 토큰이 올바른 프로젝트의 것인지 확인

## 📊 토큰 확인 명령어

### Windows
```cmd
echo %SUPABASE_ACCESS_TOKEN%
```

### macOS/Linux
```bash
echo $SUPABASE_ACCESS_TOKEN
```

### Python
```python
import os
print(os.environ.get('SUPABASE_ACCESS_TOKEN', 'Not set'))
```

## 🔐 보안 주의사항

1. **토큰 보안**: 액세스 토큰을 안전하게 보관
2. **환경변수**: 민감한 정보는 환경변수로 관리
3. **Git 무시**: .env 파일을 .gitignore에 추가
4. **토큰 순환**: 정기적으로 토큰 갱신

## 📞 지원

- **Supabase 문서**: https://supabase.com/docs
- **MCP 문서**: https://modelcontextprotocol.io
- **Cursor AI 문서**: https://cursor.sh/docs

---

**🚀 토큰 설정이 완료되면 MCP 기능을 활용하여 Supabase 데이터베이스를 자동으로 생성할 수 있습니다!** 