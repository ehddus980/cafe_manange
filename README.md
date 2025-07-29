# 카페 주문 관리 시스템

Flask 기반의 카페 주문 관리 시스템입니다. 사용자가 메뉴를 보고 주문할 수 있고, 관리자가 주문을 관리하고 매출을 확인할 수 있습니다.

## 주요 기능

### 사용자 기능
- 메뉴 조회 및 카테고리별 필터링
- 장바구니에 상품 추가/수정/삭제
- 주문하기 (고객 정보, 배송 정보 포함)
- 온도 선택 (핫/아이스)
- 특별 요청사항 입력

### 관리자 기능
- 관리자 로그인
- 대시보드 (오늘의 주문, 매출, 대기 주문)
- 매출 관리 (날짜별 필터링, 엑셀 내보내기)
- 메뉴 관리 (추가/수정/삭제, 품절 관리)
- 카테고리 관리
- 주문 데이터 엑셀 파일로 가져오기
- 영수증 출력

## 기술 스택

- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite (개발) / PostgreSQL (운영)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Icons**: Font Awesome
- **Data Processing**: pandas, openpyxl

## 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/ehddus980/cafe_manange.git
cd cafe_manange
```

### 2. 가상환경 생성 및 활성화
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 데이터베이스 설정

#### SQLite 사용 (기본값 - 개발용)
```bash
# 별도 설정 없이 바로 실행 가능
python app.py
```

#### PostgreSQL 사용 (운영용)
```bash
# 환경변수 설정
set DATABASE_TYPE=postgresql
set DB_HOST=your-db-host
set DB_PORT=5432
set DB_NAME=cafe_db
set DB_USER=your-username
set DB_PASSWORD=your-password
set SECRET_KEY=your-secret-key
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=secure-password

# 또는 .env 파일 생성
echo DATABASE_TYPE=postgresql > .env
echo DB_HOST=your-db-host >> .env
echo DB_PORT=5432 >> .env
echo DB_NAME=cafe_db >> .env
echo DB_USER=your-username >> .env
echo DB_PASSWORD=your-password >> .env
echo SECRET_KEY=your-secret-key >> .env
echo ADMIN_USERNAME=admin >> .env
echo ADMIN_PASSWORD=secure-password >> .env
```

### 5. 데이터베이스 초기화
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 6. 애플리케이션 실행
```bash
python app.py
```

### 7. 브라우저에서 접속
- 사용자 메뉴: http://localhost:5000/menu
- 관리자 로그인: http://localhost:5000/admin/login

## 프로젝트 구조

```
cafe_management/
├── app.py                 # 메인 Flask 애플리케이션
├── config.py              # 설정 파일
├── models.py              # 데이터베이스 모델
├── requirements.txt       # Python 패키지 목록
├── README.md             # 프로젝트 설명
├── generate_sample_data.py # 샘플 데이터 생성 스크립트
├── sample_orders.xlsx    # 샘플 주문 데이터
├── .gitignore           # Git 제외 파일 설정
├── templates/           # HTML 템플릿
│   ├── base.html       # 기본 템플릿
│   ├── index.html      # 메인 페이지
│   ├── user/           # 사용자 페이지
│   │   ├── menu.html   # 메뉴 페이지
│   │   └── cart.html   # 장바구니 페이지
│   └── admin/          # 관리자 페이지
│       ├── login.html  # 로그인 페이지
│       ├── dashboard.html # 대시보드
│       ├── sales.html  # 매출 관리
│       ├── menu.html   # 메뉴 관리
│       ├── add_menu.html # 메뉴 추가
│       ├── edit_menu.html # 메뉴 수정
│       ├── categories.html # 카테고리 관리
│       ├── import_orders.html # 주문 가져오기
│       └── receipt.html # 영수증
└── static/             # 정적 파일
    ├── css/           # CSS 파일
    ├── js/            # JavaScript 파일
    └── uploads/       # 업로드된 이미지
        └── .gitkeep   # 디렉토리 유지용 파일
```

## 데이터베이스 모델

### Menu (메뉴)
- `id`: 고유 식별자
- `name`: 메뉴명
- `category`: 카테고리
- `price`: 가격
- `description`: 설명
- `image_path`: 이미지 경로
- `temperature_option`: 온도 옵션 (핫/아이스)
- `is_sold_out`: 품절 여부
- `order_index`: 정렬 순서

### Order (주문)
- `id`: 고유 식별자
- `customer_name`: 고객명
- `customer_phone`: 전화번호
- `delivery_location`: 배송 위치
- `delivery_time`: 배송 시간
- `special_requests`: 특별 요청사항
- `total_amount`: 총 금액
- `order_date`: 주문 날짜
- `status`: 주문 상태 (대기/완료/취소)

### OrderItem (주문 항목)
- `id`: 고유 식별자
- `order_id`: 주문 ID (외래키)
- `menu_id`: 메뉴 ID (외래키)
- `quantity`: 수량
- `temperature`: 온도 (핫/아이스)
- `special_requests`: 특별 요청사항
- `price`: 가격

## 주요 라우트

### 사용자 라우트
- `GET /`: 메인 페이지
- `GET /menu`: 메뉴 페이지
- `POST /add_to_cart`: 장바구니에 추가
- `GET /cart`: 장바구니 페이지
- `POST /update_cart`: 장바구니 수정
- `POST /place_order`: 주문하기

### 관리자 라우트
- `GET /admin/login`: 로그인 페이지
- `POST /admin/login`: 로그인 처리
- `GET /admin/dashboard`: 대시보드
- `GET /admin/sales`: 매출 관리
- `GET /admin/menu`: 메뉴 관리
- `POST /admin/add_menu`: 메뉴 추가
- `POST /admin/edit_menu`: 메뉴 수정
- `POST /admin/delete_menu`: 메뉴 삭제
- `GET /admin/categories`: 카테고리 관리
- `POST /admin/import_orders`: 주문 데이터 가져오기
- `GET /admin/export_all_orders`: 전체 주문 내보내기
- `GET /admin/receipt/<order_id>`: 영수증 출력

## 설정

### 환경변수
- `DATABASE_TYPE`: 데이터베이스 타입 ('sqlite' 또는 'postgresql')
- `DB_HOST`: 데이터베이스 호스트 (PostgreSQL 사용시)
- `DB_PORT`: 데이터베이스 포트 (PostgreSQL 사용시)
- `DB_NAME`: 데이터베이스 이름 (PostgreSQL 사용시)
- `DB_USER`: 데이터베이스 사용자명 (PostgreSQL 사용시)
- `DB_PASSWORD`: 데이터베이스 비밀번호 (PostgreSQL 사용시)
- `SECRET_KEY`: Flask 시크릿 키
- `ADMIN_USERNAME`: 관리자 사용자명
- `ADMIN_PASSWORD`: 관리자 비밀번호

### 파일 업로드 설정
- `UPLOAD_FOLDER`: 업로드 폴더 경로
- `ALLOWED_EXTENSIONS`: 허용된 파일 확장자
- `MAX_CONTENT_LENGTH`: 최대 파일 크기 (16MB)

### 세션 설정
- `PERMANENT_SESSION_LIFETIME`: 세션 유지 시간 (1일)
- `SESSION_TYPE`: 세션 타입 ('filesystem')

## 개발 고려사항

### 보안
- 관리자 비밀번호는 환경변수로 관리
- 파일 업로드 시 확장자 검증
- SQL 인젝션 방지를 위한 ORM 사용

### 성능
- 데이터베이스 인덱스 설정
- 이미지 파일 최적화
- 세션 관리 최적화

### 확장성
- 모듈화된 코드 구조
- 설정 파일 분리
- 환경별 설정 관리

## 배포 고려사항

### 서버 요구사항
- Python 3.8 이상
- PostgreSQL (운영환경)
- 웹 서버 (Nginx, Apache)
- WSGI 서버 (Gunicorn, uWSGI)

### 환경 설정
- 환경변수 설정
- 데이터베이스 마이그레이션
- 정적 파일 서빙 설정
- 로그 설정

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여

버그 리포트나 기능 제안은 GitHub Issues를 통해 해주세요.

## 변경 이력

- v1.0.0: 초기 버전 릴리즈
  - 사용자 메뉴 조회 및 주문 기능
  - 관리자 대시보드 및 매출 관리
  - 메뉴 관리 기능
  - 엑셀 데이터 가져오기/내보내기
  - PostgreSQL 지원 추가 