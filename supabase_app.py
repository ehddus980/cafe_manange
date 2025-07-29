"""
Supabase를 사용하는 카페 관리 시스템
PostgreSQL 데이터베이스와 Supabase 클라이언트를 활용한 개선된 버전
"""

import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_session import Session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
from functools import wraps
from supabase import create_client, Client
from supabase_config import validate_supabase_config, get_database_uri

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

# Supabase 클라이언트 초기화
try:
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_ANON_KEY')
    
    if supabase_url and supabase_key:
        supabase: Client = create_client(supabase_url, supabase_key)
        SUPABASE_AVAILABLE = True
        print("✅ Supabase 클라이언트가 성공적으로 초기화되었습니다.")
    else:
        SUPABASE_AVAILABLE = False
        print("⚠️  Supabase 설정이 없습니다. 로컬 SQLite를 사용합니다.")
except Exception as e:
    SUPABASE_AVAILABLE = False
    print(f"❌ Supabase 클라이언트 초기화 실패: {e}")

# Flask 앱 초기화
app = Flask(__name__)

# 설정
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 관리자 계정 설정
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Session 초기화
Session(app)

# pandas 의존성 확인
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas is not available. Excel import/export features will be disabled.")

def admin_required(f):
    """관리자 권한이 필요한 라우트를 위한 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('관리자 로그인이 필요합니다.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """업로드된 파일이 허용된 확장자인지 확인"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Supabase 데이터베이스 함수들
def get_all_menus():
    """모든 메뉴 조회"""
    if SUPABASE_AVAILABLE:
        try:
            response = supabase.table('cafe_menu').select('*').order('display_order').execute()
            return response.data
        except Exception as e:
            print(f"메뉴 조회 오류: {e}")
            return []
    else:
        # 로컬 SQLite 사용 (기존 로직)
        return []

def get_menu_by_id(menu_id):
    """ID로 메뉴 조회"""
    if SUPABASE_AVAILABLE:
        try:
            response = supabase.table('cafe_menu').select('*').eq('id', menu_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"메뉴 조회 오류: {e}")
            return None
    else:
        # 로컬 SQLite 사용
        return None

def create_menu(menu_data):
    """새 메뉴 생성"""
    if SUPABASE_AVAILABLE:
        try:
            response = supabase.table('cafe_menu').insert(menu_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"메뉴 생성 오류: {e}")
            return None
    else:
        # 로컬 SQLite 사용
        return None

def update_menu(menu_id, menu_data):
    """메뉴 수정"""
    if SUPABASE_AVAILABLE:
        try:
            response = supabase.table('cafe_menu').update(menu_data).eq('id', menu_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"메뉴 수정 오류: {e}")
            return None
    else:
        # 로컬 SQLite 사용
        return None

def delete_menu(menu_id):
    """메뉴 삭제"""
    if SUPABASE_AVAILABLE:
        try:
            response = supabase.table('cafe_menu').delete().eq('id', menu_id).execute()
            return True
        except Exception as e:
            print(f"메뉴 삭제 오류: {e}")
            return False
    else:
        # 로컬 SQLite 사용
        return False

def get_all_orders():
    """모든 주문 조회"""
    if SUPABASE_AVAILABLE:
        try:
            response = supabase.table('cafe_order').select('*').order('order_date', desc=True).execute()
            return response.data
        except Exception as e:
            print(f"주문 조회 오류: {e}")
            return []
    else:
        # 로컬 SQLite 사용
        return []

def create_order(order_data):
    """새 주문 생성"""
    if SUPABASE_AVAILABLE:
        try:
            response = supabase.table('cafe_order').insert(order_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"주문 생성 오류: {e}")
            return None
    else:
        # 로컬 SQLite 사용
        return None

def create_order_item(item_data):
    """주문 아이템 생성"""
    if SUPABASE_AVAILABLE:
        try:
            response = supabase.table('cafe_order_item').insert(item_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"주문 아이템 생성 오류: {e}")
            return None
    else:
        # 로컬 SQLite 사용
        return None

def get_order_details(order_id):
    """주문 상세 정보 조회"""
    if SUPABASE_AVAILABLE:
        try:
            # 주문 정보
            order_response = supabase.table('cafe_order').select('*').eq('id', order_id).execute()
            if not order_response.data:
                return None, []
            
            order = order_response.data[0]
            
            # 주문 아이템들
            items_response = supabase.table('cafe_order_item').select('*, cafe_menu(*)').eq('order_id', order_id).execute()
            items = items_response.data
            
            return order, items
        except Exception as e:
            print(f"주문 상세 조회 오류: {e}")
            return None, []
    else:
        # 로컬 SQLite 사용
        return None, []

def get_sales_statistics():
    """매출 통계 조회"""
    if SUPABASE_AVAILABLE:
        try:
            # 오늘 매출
            today = datetime.now().date()
            today_response = supabase.table('cafe_order').select('total_amount').eq('order_date', today.isoformat()).execute()
            today_sales = sum(item['total_amount'] for item in today_response.data)
            
            # 이번 주 매출
            week_start = today - timedelta(days=today.weekday())
            week_response = supabase.table('cafe_order').select('total_amount').gte('order_date', week_start.isoformat()).execute()
            week_sales = sum(item['total_amount'] for item in week_response.data)
            
            # 이번 달 매출
            month_start = today.replace(day=1)
            month_response = supabase.table('cafe_order').select('total_amount').gte('order_date', month_start.isoformat()).execute()
            month_sales = sum(item['total_amount'] for item in month_response.data)
            
            # 총 주문 수
            total_orders_response = supabase.table('cafe_order').select('id', count='exact').execute()
            total_orders = total_orders_response.count if hasattr(total_orders_response, 'count') else len(total_orders_response.data)
            
            return {
                'today_sales': today_sales,
                'week_sales': week_sales,
                'month_sales': month_sales,
                'total_orders': total_orders
            }
        except Exception as e:
            print(f"매출 통계 조회 오류: {e}")
            return {'today_sales': 0, 'week_sales': 0, 'month_sales': 0, 'total_orders': 0}
    else:
        # 로컬 SQLite 사용
        return {'today_sales': 0, 'week_sales': 0, 'month_sales': 0, 'total_orders': 0}

# 라우트 정의
@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/menu')
def menu():
    """메뉴 페이지"""
    menus = get_all_menus()
    categories = list(set(menu['category'] for menu in menus))
    return render_template('user/menu.html', menus=menus, categories=categories)

@app.route('/cart')
def cart():
    """장바구니 페이지"""
    cart_items = session.get('cart', [])
    total = sum(item['subtotal'] for item in cart_items)
    return render_template('user/cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """장바구니에 상품 추가"""
    menu_id = request.form.get('menu_id')
    quantity = int(request.form.get('quantity', 1))
    temperature = request.form.get('temperature', 'ice')
    special_request = request.form.get('special_request', '')
    
    menu = get_menu_by_id(int(menu_id))
    if menu:
        subtotal = menu['price'] * quantity
        
        cart_item = {
            'menu_id': menu_id,
            'name': menu['name'],
            'price': menu['price'],
            'quantity': quantity,
            'subtotal': subtotal,
            'temperature': temperature,
            'special_request': special_request
        }
        
        cart = session.get('cart', [])
        cart.append(cart_item)
        session['cart'] = cart
        
        flash('장바구니에 추가되었습니다.', 'success')
    
    return redirect(url_for('menu'))

@app.route('/remove_from_cart/<int:index>')
def remove_from_cart(index):
    """장바구니에서 상품 제거"""
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        cart.pop(index)
        session['cart'] = cart
        flash('장바구니에서 제거되었습니다.', 'success')
    
    return redirect(url_for('cart'))

@app.route('/place_order', methods=['POST'])
def place_order():
    """주문 완료"""
    cart_items = session.get('cart', [])
    if not cart_items:
        flash('장바구니가 비어있습니다.', 'error')
        return redirect(url_for('cart'))
    
    customer_name = request.form.get('customer_name')
    delivery_location = request.form.get('delivery_location')
    delivery_time = request.form.get('delivery_time')
    order_request = request.form.get('order_request', '')
    
    if not customer_name or not delivery_location:
        flash('고객명과 배송지역을 입력해주세요.', 'error')
        return redirect(url_for('cart'))
    
    total_amount = sum(item['subtotal'] for item in cart_items)
    
    # 주문 생성
    order_data = {
        'customer_name': customer_name,
        'delivery_location': delivery_location,
        'delivery_time': delivery_time,
        'order_request': order_request,
        'total_amount': total_amount,
        'status': 'pending'
    }
    
    order = create_order(order_data)
    if order:
        # 주문 아이템들 생성
        for item in cart_items:
            item_data = {
                'order_id': order['id'],
                'menu_id': item['menu_id'],
                'quantity': item['quantity'],
                'subtotal': item['subtotal'],
                'special_request': item['special_request'],
                'temperature': item['temperature']
            }
            create_order_item(item_data)
        
        # 장바구니 비우기
        session.pop('cart', None)
        
        flash('주문이 완료되었습니다!', 'success')
        return redirect(url_for('order_complete', order_id=order['id']))
    else:
        flash('주문 처리 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('cart'))

@app.route('/order_complete/<int:order_id>')
def order_complete(order_id):
    """주문 완료 페이지"""
    order, items = get_order_details(order_id)
    if not order:
        flash('주문을 찾을 수 없습니다.', 'error')
        return redirect(url_for('index'))
    
    return render_template('user/order_complete.html', order=order, items=items)

# 관리자 라우트
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """관리자 로그인"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('관리자 로그인이 완료되었습니다.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """관리자 로그아웃"""
    session.pop('admin_logged_in', None)
    flash('로그아웃되었습니다.', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """관리자 대시보드"""
    stats = get_sales_statistics()
    recent_orders = get_all_orders()[:5]  # 최근 5개 주문
    
    return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders)

@app.route('/admin/sales')
@admin_required
def admin_sales():
    """매출 관리"""
    orders = get_all_orders()
    return render_template('admin/sales.html', orders=orders)

@app.route('/admin/menu')
@admin_required
def admin_menu():
    """메뉴 관리"""
    menus = get_all_menus()
    return render_template('admin/menu.html', menus=menus)

@app.route('/admin/menu/add', methods=['GET', 'POST'])
@admin_required
def admin_add_menu():
    """메뉴 추가"""
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        price = float(request.form.get('price', 0))
        description = request.form.get('description', '')
        temperature_option = request.form.get('temperature_option', 'both')
        display_order = int(request.form.get('display_order', 9999))
        
        # 이미지 업로드 처리
        image = ''
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename
        
        menu_data = {
            'name': name,
            'category': category,
            'price': price,
            'description': description,
            'image': image,
            'temperature_option': temperature_option,
            'display_order': display_order,
            'is_soldout': False
        }
        
        if create_menu(menu_data):
            flash('메뉴가 추가되었습니다.', 'success')
            return redirect(url_for('admin_menu'))
        else:
            flash('메뉴 추가 중 오류가 발생했습니다.', 'error')
    
    return render_template('admin/add_menu.html')

@app.route('/admin/menu/edit/<int:menu_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_menu(menu_id):
    """메뉴 수정"""
    menu = get_menu_by_id(menu_id)
    if not menu:
        flash('메뉴를 찾을 수 없습니다.', 'error')
        return redirect(url_for('admin_menu'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        price = float(request.form.get('price', 0))
        description = request.form.get('description', '')
        temperature_option = request.form.get('temperature_option', 'both')
        display_order = int(request.form.get('display_order', 9999))
        is_soldout = 'is_soldout' in request.form
        
        # 이미지 업로드 처리
        image = menu['image']
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename
        
        menu_data = {
            'name': name,
            'category': category,
            'price': price,
            'description': description,
            'image': image,
            'temperature_option': temperature_option,
            'display_order': display_order,
            'is_soldout': is_soldout
        }
        
        if update_menu(menu_id, menu_data):
            flash('메뉴가 수정되었습니다.', 'success')
            return redirect(url_for('admin_menu'))
        else:
            flash('메뉴 수정 중 오류가 발생했습니다.', 'error')
    
    return render_template('admin/edit_menu.html', menu=menu)

@app.route('/admin/menu/delete/<int:menu_id>')
@admin_required
def admin_delete_menu(menu_id):
    """메뉴 삭제"""
    if delete_menu(menu_id):
        flash('메뉴가 삭제되었습니다.', 'success')
    else:
        flash('메뉴 삭제 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('admin_menu'))

@app.route('/admin/order/<int:order_id>')
@admin_required
def admin_order_detail(order_id):
    """주문 상세 보기"""
    order, items = get_order_details(order_id)
    if not order:
        flash('주문을 찾을 수 없습니다.', 'error')
        return redirect(url_for('admin_sales'))
    
    return render_template('admin/order_detail.html', order=order, items=items)

@app.route('/admin/order/<int:order_id>/status', methods=['POST'])
@admin_required
def admin_update_order_status(order_id):
    """주문 상태 업데이트"""
    status = request.form.get('status')
    
    if SUPABASE_AVAILABLE:
        try:
            supabase.table('cafe_order').update({'status': status}).eq('id', order_id).execute()
            flash('주문 상태가 업데이트되었습니다.', 'success')
        except Exception as e:
            flash('주문 상태 업데이트 중 오류가 발생했습니다.', 'error')
    else:
        flash('Supabase 연결이 필요합니다.', 'error')
    
    return redirect(url_for('admin_order_detail', order_id=order_id))

if __name__ == '__main__':
    # Supabase 설정 검증
    if SUPABASE_AVAILABLE:
        print("🚀 Supabase 모드로 실행됩니다.")
    else:
        print("⚠️  로컬 SQLite 모드로 실행됩니다.")
        print("📝 Supabase를 사용하려면 .env 파일에 설정을 추가하세요.")
    
    # 업로드 폴더 생성
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 앱 실행
    app.run(debug=True, host='0.0.0.0', port=5000) 