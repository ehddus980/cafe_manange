# 🚀 Supabase 카페 관리 시스템

PostgreSQL 기반의 Supabase를 활용한 고성능 카페 주문 관리 시스템입니다.

## ✨ 주요 특징

- **🔐 실시간 데이터베이스**: Supabase PostgreSQL 활용
- **🛡️ 보안 강화**: Row Level Security (RLS) 정책 적용
- **📊 고성능**: 인덱스 최적화 및 쿼리 성능 향상
- **🔄 실시간 동기화**: 실시간 데이터 업데이트
- **📱 반응형 디자인**: D.E Café 컬러 팔레트 적용
- **🔧 관리자 도구**: 메뉴 관리, 주문 관리, 매출 통계

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask App     │    │   Supabase      │
│   (HTML/CSS/JS) │◄──►│   (Python)      │◄──►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 데이터베이스 스키마

### 1. 메뉴 테이블 (`cafe_menu`)
```sql
- id: SERIAL PRIMARY KEY
- name: VARCHAR(100) NOT NULL
- category: VARCHAR(50) NOT NULL
- price: DECIMAL(10,2) NOT NULL
- description: TEXT
- image: VARCHAR(255)
- temperature_option: VARCHAR(20) DEFAULT 'both'
- display_order: INTEGER DEFAULT 9999
- is_soldout: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP WITH TIME ZONE
- updated_at: TIMESTAMP WITH TIME ZONE
```

### 2. 주문 테이블 (`cafe_order`)
```sql
- id: SERIAL PRIMARY KEY
- order_date: TIMESTAMP WITH TIME ZONE
- status: VARCHAR(20) NOT NULL DEFAULT 'pending'
- total_amount: INTEGER NOT NULL
- customer_name: VARCHAR(50) NOT NULL
- delivery_location: VARCHAR(100) NOT NULL
- delivery_time: VARCHAR(50)
- order_request: TEXT
- created_at: TIMESTAMP WITH TIME ZONE
- updated_at: TIMESTAMP WITH TIME ZONE
```

### 3. 주문 아이템 테이블 (`cafe_order_item`)
```sql
- id: SERIAL PRIMARY KEY
- order_id: INTEGER REFERENCES cafe_order(id)
- menu_id: INTEGER REFERENCES cafe_menu(id)
- quantity: INTEGER NOT NULL
- subtotal: DECIMAL(10,2) NOT NULL
- special_request: TEXT
- temperature: VARCHAR(10) DEFAULT 'ice'
- created_at: TIMESTAMP WITH TIME ZONE
```

## 🚀 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements_supabase.txt
```

### 2. Supabase 프로젝트 설정
1. [Supabase](https://supabase.com)에서 새 프로젝트 생성
2. 프로젝트 URL과 API 키 확인
3. `.env` 파일 생성 및 설정

### 3. 환경변수 설정
```bash
# env_supabase.example을 .env로 복사
cp env_supabase.example .env
```

`.env` 파일 편집:
```env
# Supabase 설정
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# 데이터베이스 타입
DATABASE_TYPE=supabase

# 보안 설정
SECRET_KEY=your-secret-key-change-in-production

# 관리자 계정
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### 4. 데이터베이스 설정
```bash
# Supabase Dashboard에서 SQL Editor 실행
# supabase_migration.sql 파일의 내용을 복사하여 실행
```

또는 자동 설정:
```bash
python setup_supabase.py
```

### 5. 애플리케이션 실행
```bash
python supabase_app.py
```

## 🔧 Supabase Dashboard 설정

### 1. 테이블 생성
Supabase Dashboard → SQL Editor에서 다음 SQL 실행:

```sql
-- 메뉴 테이블 생성
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

-- 주문 테이블 생성
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

-- 주문 아이템 테이블 생성
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
```

### 2. RLS 정책 설정
```sql
-- 메뉴 테이블 RLS
ALTER TABLE cafe_menu ENABLE ROW LEVEL SECURITY;
CREATE POLICY "메뉴 읽기 정책" ON cafe_menu FOR SELECT USING (true);
CREATE POLICY "메뉴 관리자 정책" ON cafe_menu FOR ALL USING (auth.role() = 'authenticated');

-- 주문 테이블 RLS
ALTER TABLE cafe_order ENABLE ROW LEVEL SECURITY;
CREATE POLICY "주문 관리자 정책" ON cafe_order FOR ALL USING (auth.role() = 'authenticated');

-- 주문 아이템 테이블 RLS
ALTER TABLE cafe_order_item ENABLE ROW LEVEL SECURITY;
CREATE POLICY "주문 아이템 관리자 정책" ON cafe_order_item FOR ALL USING (auth.role() = 'authenticated');
```

### 3. 인덱스 생성
```sql
-- 성능 최적화를 위한 인덱스
CREATE INDEX idx_menu_category ON cafe_menu(category);
CREATE INDEX idx_menu_display_order ON cafe_menu(display_order);
CREATE INDEX idx_order_date ON cafe_order(order_date);
CREATE INDEX idx_order_status ON cafe_order(status);
CREATE INDEX idx_order_item_order_id ON cafe_order_item(order_id);
CREATE INDEX idx_order_item_menu_id ON cafe_order_item(menu_id);
```

## 📊 주요 기능

### 1. 사용자 기능
- **메뉴 브라우징**: 카테고리별 메뉴 조회
- **장바구니**: 상품 추가/제거, 수량 조정
- **주문**: 배송 정보 입력, 주문 완료
- **주문 확인**: 주문 상태 및 상세 정보 확인

### 2. 관리자 기능
- **대시보드**: 매출 통계, 최근 주문 현황
- **메뉴 관리**: 메뉴 추가/수정/삭제, 품절 처리
- **주문 관리**: 주문 상태 업데이트, 상세 정보 확인
- **매출 관리**: 일별/주별/월별 매출 통계
- **카테고리 관리**: 메뉴 카테고리 관리

### 3. 고급 기능
- **실시간 업데이트**: 주문 상태 실시간 변경
- **이미지 업로드**: 메뉴 이미지 관리
- **Excel 내보내기**: 주문 데이터 Excel 형식 다운로드
- **검색 및 필터**: 메뉴 검색, 주문 필터링

## 🔐 보안 기능

### 1. Row Level Security (RLS)
- **메뉴 테이블**: 모든 사용자가 읽기 가능, 관리자만 수정
- **주문 테이블**: 관리자만 모든 작업 가능
- **주문 아이템 테이블**: 관리자만 모든 작업 가능

### 2. 인증 및 권한
- **관리자 로그인**: 세션 기반 인증
- **API 키 관리**: Supabase API 키 보안
- **환경변수**: 민감한 정보 환경변수로 관리

## 🚀 배포 가이드

### 1. 로컬 개발 환경
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements_supabase.txt

# 환경변수 설정
cp env_supabase.example .env
# .env 파일 편집

# 데이터베이스 설정
python setup_supabase.py

# 애플리케이션 실행
python supabase_app.py
```

### 2. 클라우드 배포
- **Heroku**: `Procfile` 및 `runtime.txt` 추가
- **Vercel**: `vercel.json` 설정
- **Railway**: 자동 배포 지원
- **AWS/GCP**: Docker 컨테이너 배포

## 📈 성능 최적화

### 1. 데이터베이스 최적화
- **인덱스**: 자주 조회되는 컬럼에 인덱스 적용
- **쿼리 최적화**: JOIN 및 서브쿼리 최적화
- **연결 풀링**: 데이터베이스 연결 재사용

### 2. 애플리케이션 최적화
- **캐싱**: Redis를 활용한 세션 및 데이터 캐싱
- **CDN**: 정적 파일 CDN 배포
- **로드 밸런싱**: 트래픽 분산 처리

## 🐛 문제 해결

### 1. Supabase 연결 오류
```bash
# 환경변수 확인
echo $SUPABASE_URL
echo $SUPABASE_ANON_KEY

# 연결 테스트
python -c "from supabase import create_client; print('연결 성공')"
```

### 2. 테이블 생성 오류
```sql
-- 테이블 존재 여부 확인
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name LIKE 'cafe_%';
```

### 3. RLS 정책 오류
```sql
-- RLS 정책 확인
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies WHERE tablename LIKE 'cafe_%';
```

## 📞 지원 및 문의

- **GitHub Issues**: 버그 리포트 및 기능 요청
- **Documentation**: 상세한 API 문서
- **Community**: 개발자 커뮤니티 참여

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

**🎉 Supabase를 활용한 현대적인 카페 관리 시스템을 경험해보세요!** 