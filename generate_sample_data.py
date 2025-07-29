import pandas as pd
from datetime import datetime, timedelta
import random

# 샘플 메뉴 데이터
sample_menus = [
    {'name': '아메리카노', 'price': 4500},
    {'name': '카페라떼', 'price': 5500},
    {'name': '카푸치노', 'price': 5500},
    {'name': '에스프레소', 'price': 3500},
    {'name': '바닐라라떼', 'price': 6000},
    {'name': '카라멜마끼아또', 'price': 6000},
    {'name': '모카', 'price': 6500},
    {'name': '녹차라떼', 'price': 5500},
    {'name': '딸기스무디', 'price': 7000},
    {'name': '망고스무디', 'price': 7000},
    {'name': '초코라떼', 'price': 6000},
    {'name': '토피넛라떼', 'price': 6500}
]

# 샘플 고객 데이터
sample_customers = [
    {'name': '홍길동', 'location': '서울시 강남구 테헤란로 123'},
    {'name': '김철수', 'location': '서울시 서초구 반포대로 456'},
    {'name': '이영희', 'location': '서울시 마포구 홍대입구 789'},
    {'name': '박민수', 'location': '서울시 송파구 잠실로 321'},
    {'name': '정수진', 'location': '서울시 종로구 종로 654'},
    {'name': '최지영', 'location': '서울시 영등포구 여의대로 987'},
    {'name': '강동현', 'location': '서울시 광진구 능동로 147'},
    {'name': '윤서연', 'location': '서울시 성동구 왕십리로 258'}
]

# 샘플 특별 요청사항
special_requests = [
    '설탕 적게',
    '시럽 추가',
    '우유 대신 두유로',
    '얼음 적게',
    '샷 추가',
    '휘핑크림 없이',
    '따뜻하게',
    '차갑게',
    '샷 2개 추가',
    '시럽 2배로'
]

# 주문 상태
order_statuses = ['pending', 'preparing', 'ready', 'delivered', 'cancelled']

def generate_sample_orders(num_orders=5):
    """샘플 주문 데이터 생성"""
    orders_data = []
    
    # 현재 시간부터 과거로 거슬러 올라가며 주문 생성
    base_time = datetime.now()
    
    for i in range(num_orders):
        # 주문 시간 (최근 7일 내에서 랜덤)
        order_time = base_time - timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # 고객 정보
        customer = random.choice(sample_customers)
        
        # 주문할 메뉴 개수 (1-4개)
        num_items = random.randint(1, 4)
        
        total_amount = 0
        order_items = []
        
        # 주문 항목 생성
        for j in range(num_items):
            menu = random.choice(sample_menus)
            quantity = random.randint(1, 3)
            subtotal = menu['price'] * quantity
            total_amount += subtotal
            
            # 온도 선택
            temperature = random.choice(['ice', 'hot'])
            
            # 특별 요청사항 (50% 확률)
            special_request = random.choice(special_requests) if random.random() > 0.5 else ''
            
            order_items.append({
                '고객명': customer['name'],
                '배달위치': customer['location'],
                '메뉴명': menu['name'],
                '수량': quantity,
                '단가': menu['price'],
                '소계': subtotal,
                '온도': temperature,
                '특별요청': special_request,
                '총금액': total_amount,
                '주문상태': random.choice(order_statuses),
                '주문일시': order_time.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # 각 주문 항목을 별도 행으로 추가
        orders_data.extend(order_items)
    
    return orders_data

def create_excel_file(filename='sample_orders.xlsx'):
    """Excel 파일 생성"""
    # 샘플 데이터 생성
    orders_data = generate_sample_orders(5)
    
    # DataFrame 생성
    df = pd.DataFrame(orders_data)
    
    # Excel 파일로 저장
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='주문내역', index=False)
        
        # 열 너비 자동 조정
        worksheet = writer.sheets['주문내역']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"샘플 주문 데이터가 '{filename}' 파일로 생성되었습니다.")
    print(f"총 {len(orders_data)}개의 주문 항목이 포함되어 있습니다.")
    
    return filename

if __name__ == "__main__":
    # 샘플 데이터 생성
    filename = create_excel_file()
    
    # 생성된 데이터 미리보기
    df = pd.read_excel(filename)
    print("\n생성된 데이터 미리보기:")
    print(df.head(10))
    
    print(f"\n파일 위치: {filename}")
    print("이 파일을 관리자 페이지의 '데이터 가져오기'에서 업로드할 수 있습니다.") 