#!/usr/bin/env python3
"""
데이터베이스 마이그레이션 스크립트
SQLite에서 PostgreSQL로 데이터를 마이그레이션합니다.
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# 환경변수 로드
load_dotenv()

# SQLite 데이터베이스에서 데이터 읽기
def read_sqlite_data():
    """SQLite 데이터베이스에서 데이터를 읽어옵니다."""
    import sqlite3
    
    if not os.path.exists('cafe.db'):
        print("SQLite 데이터베이스 파일(cafe.db)을 찾을 수 없습니다.")
        return None
    
    conn = sqlite3.connect('cafe.db')
    cursor = conn.cursor()
    
    # 메뉴 데이터 읽기
    cursor.execute("SELECT * FROM menu")
    menus = cursor.fetchall()
    
    # 주문 데이터 읽기
    cursor.execute("SELECT * FROM `order`")
    orders = cursor.fetchall()
    
    # 주문 항목 데이터 읽기
    cursor.execute("SELECT * FROM order_item")
    order_items = cursor.fetchall()
    
    conn.close()
    
    return {
        'menus': menus,
        'orders': orders,
        'order_items': order_items
    }

# PostgreSQL 데이터베이스에 데이터 쓰기
def write_postgresql_data(data):
    """PostgreSQL 데이터베이스에 데이터를 씁니다."""
    from app import app, db, Menu, Order, OrderItem
    
    with app.app_context():
        # 기존 데이터 삭제 (주의: 모든 데이터가 삭제됩니다)
        print("기존 데이터를 삭제합니다...")
        OrderItem.query.delete()
        Order.query.delete()
        Menu.query.delete()
        db.session.commit()
        
        # 메뉴 데이터 추가
        print("메뉴 데이터를 마이그레이션합니다...")
        for menu_data in data['menus']:
            menu = Menu(
                id=menu_data[0],
                name=menu_data[1],
                category=menu_data[2],
                price=menu_data[3],
                description=menu_data[4],
                image_path=menu_data[5],
                temperature_option=menu_data[6],
                is_sold_out=bool(menu_data[7]),
                order_index=menu_data[8]
            )
            db.session.add(menu)
        
        # 주문 데이터 추가
        print("주문 데이터를 마이그레이션합니다...")
        for order_data in data['orders']:
            order = Order(
                id=order_data[0],
                customer_name=order_data[1],
                customer_phone=order_data[2],
                delivery_location=order_data[3],
                delivery_time=order_data[4],
                special_requests=order_data[5],
                total_amount=order_data[6],
                order_date=datetime.fromisoformat(order_data[7]),
                status=order_data[8]
            )
            db.session.add(order)
        
        # 주문 항목 데이터 추가
        print("주문 항목 데이터를 마이그레이션합니다...")
        for item_data in data['order_items']:
            order_item = OrderItem(
                id=item_data[0],
                order_id=item_data[1],
                menu_id=item_data[2],
                quantity=item_data[3],
                temperature=item_data[4],
                special_requests=item_data[5],
                price=item_data[6]
            )
            db.session.add(order_item)
        
        # 변경사항 저장
        db.session.commit()
        print("마이그레이션이 완료되었습니다!")

def main():
    """메인 함수"""
    print("=== 데이터베이스 마이그레이션 도구 ===")
    
    # 환경변수 확인
    database_type = os.environ.get('DATABASE_TYPE', 'sqlite')
    if database_type != 'postgresql':
        print("PostgreSQL로 설정되지 않았습니다.")
        print("환경변수 DATABASE_TYPE=postgresql로 설정해주세요.")
        return
    
    # SQLite 데이터 읽기
    print("SQLite 데이터베이스에서 데이터를 읽어옵니다...")
    data = read_sqlite_data()
    
    if not data:
        print("마이그레이션을 중단합니다.")
        return
    
    print(f"읽어온 데이터:")
    print(f"- 메뉴: {len(data['menus'])}개")
    print(f"- 주문: {len(data['orders'])}개")
    print(f"- 주문 항목: {len(data['order_items'])}개")
    
    # 사용자 확인
    confirm = input("\nPostgreSQL로 마이그레이션하시겠습니까? (y/N): ")
    if confirm.lower() != 'y':
        print("마이그레이션을 취소합니다.")
        return
    
    # PostgreSQL에 데이터 쓰기
    try:
        write_postgresql_data(data)
        print("마이그레이션이 성공적으로 완료되었습니다!")
    except Exception as e:
        print(f"마이그레이션 중 오류가 발생했습니다: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 