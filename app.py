import os
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas is not available. Excel import/export features will be disabled.")
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
from functools import wraps
from io import BytesIO

# 환경변수 파일 로드
from dotenv import load_dotenv
load_dotenv()

from config import *
from models import db, Menu, Order, OrderItem

app = Flask(__name__)
app.config.from_object('config')

# 세션 설정
Session(app)

# 데이터베이스 초기화
db.init_app(app)

# 파일 업로드 설정
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 관리자 인증 데코레이터
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('관리자 로그인이 필요합니다.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# 메인 라우트
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/init_db')
def init_db():
    with app.app_context():
        db.create_all()
        flash('데이터베이스가 초기화되었습니다.', 'success')
    return redirect(url_for('index'))

@app.route('/update_db_schema')
def update_db_schema():
    with app.app_context():
        db.create_all()
        flash('데이터베이스 스키마가 업데이트되었습니다.', 'success')
    return redirect(url_for('index'))

# 사용자 라우트
@app.route('/user/menu')
def user_menu():
    categories = db.session.query(Menu.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    menus = Menu.query.filter_by(is_soldout=False).order_by(Menu.display_order, Menu.name).all()
    
    return render_template('user/menu.html', menus=menus, categories=categories)

@app.route('/user/add_to_cart', methods=['POST'])
def add_to_cart():
    menu_id = request.form.get('menu_id')
    quantity = int(request.form.get('quantity', 1))
    temperature = request.form.get('temperature', 'ice')
    special_request = request.form.get('special_request', '')
    
    menu = Menu.query.get_or_404(menu_id)
    
    if 'cart' not in session:
        session['cart'] = []
    
    # 기존 장바구니에 같은 메뉴가 있는지 확인
    cart_item = None
    for item in session['cart']:
        if (item['menu_id'] == menu_id and 
            item['temperature'] == temperature and 
            item['special_request'] == special_request):
            cart_item = item
            break
    
    if cart_item:
        cart_item['quantity'] += quantity
    else:
        session['cart'].append({
            'menu_id': menu_id,
            'name': menu.name,
            'price': menu.price,
            'quantity': quantity,
            'temperature': temperature,
            'special_request': special_request
        })
    
    session.modified = True
    flash(f'{menu.name}이(가) 장바구니에 추가되었습니다.', 'success')
    return redirect(url_for('user_menu'))

@app.route('/user/view_cart')
def view_cart():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('user/cart.html', cart=cart, total=total)

@app.route('/user/update_cart', methods=['POST'])
def update_cart():
    action = request.form.get('action')
    index = int(request.form.get('index'))
    
    if 'cart' not in session:
        return redirect(url_for('view_cart'))
    
    if action == 'update':
        quantity = int(request.form.get('quantity', 1))
        if quantity > 0:
            session['cart'][index]['quantity'] = quantity
        else:
            session['cart'].pop(index)
    elif action == 'remove':
        session['cart'].pop(index)
    
    session.modified = True
    flash('장바구니가 업데이트되었습니다.', 'success')
    return redirect(url_for('view_cart'))

@app.route('/user/place_order', methods=['POST'])
def place_order():
    cart = session.get('cart', [])
    if not cart:
        flash('장바구니가 비어있습니다.', 'error')
        return redirect(url_for('user_menu'))
    
    customer_name = request.form.get('customer_name')
    delivery_location = request.form.get('delivery_location')
    delivery_time = request.form.get('delivery_time')
    order_request = request.form.get('order_request')
    
    if not customer_name or not delivery_location:
        flash('고객명과 배달 위치를 입력해주세요.', 'error')
        return redirect(url_for('view_cart'))
    
    total_amount = sum(item['price'] * item['quantity'] for item in cart)
    
    # 주문 생성
    order = Order(
        customer_name=customer_name,
        delivery_location=delivery_location,
        delivery_time=delivery_time,
        order_request=order_request,
        total_amount=total_amount
    )
    
    db.session.add(order)
    db.session.flush()  # ID 생성을 위해 flush
    
    # 주문 항목 생성
    for item in cart:
        order_item = OrderItem(
            order_id=order.id,
            menu_id=item['menu_id'],
            quantity=item['quantity'],
            subtotal=item['price'] * item['quantity'],
            special_request=item['special_request'],
            temperature=item['temperature']
        )
        db.session.add(order_item)
    
    db.session.commit()
    
    # 장바구니 비우기
    session.pop('cart', None)
    
    flash(f'주문이 완료되었습니다. 주문번호: {order.id}', 'success')
    return redirect(url_for('user_menu'))

@app.route('/user/clear_cart', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    flash('장바구니가 비워졌습니다.', 'success')
    return redirect(url_for('user_menu'))

# 관리자 라우트
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('관리자로 로그인되었습니다.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('잘못된 로그인 정보입니다.', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('로그아웃되었습니다.', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    # 최근 주문 통계
    today = datetime.now().date()
    today_orders = Order.query.filter(
        db.func.date(Order.order_date) == today
    ).count()
    
    today_sales = db.session.query(db.func.sum(Order.total_amount)).filter(
        db.func.date(Order.order_date) == today
    ).scalar() or 0
    
    pending_orders = Order.query.filter_by(status='pending').count()
    
    return render_template('admin/dashboard.html', 
                         today_orders=today_orders,
                         today_sales=today_sales,
                         pending_orders=pending_orders)

@app.route('/admin/sales')
@admin_required
def admin_sales():
    # 기본 필터: 오늘
    start_date = request.args.get('start_date', datetime.now().strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    if start_date and end_date:
        orders = Order.query.filter(
            db.func.date(Order.order_date) >= start_date,
            db.func.date(Order.order_date) <= end_date
        ).order_by(Order.order_date.desc()).all()
    else:
        orders = Order.query.order_by(Order.order_date.desc()).all()
    
    total_sales = sum(order.total_amount for order in orders)
    total_orders = len(orders)
    
    return render_template('admin/sales.html', 
                         orders=orders,
                         total_sales=total_sales,
                         total_orders=total_orders,
                         start_date=start_date,
                         end_date=end_date)

@app.route('/admin/sales/filter', methods=['POST'])
@admin_required
def admin_sales_filter():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    return redirect(url_for('admin_sales', start_date=start_date, end_date=end_date))

@app.route('/admin/export_all_orders')
@admin_required
def admin_export_all_orders():
    if not PANDAS_AVAILABLE:
        flash('Excel 내보내기 기능을 사용하려면 pandas가 필요합니다.', 'error')
        return redirect(url_for('admin_sales'))
    
    orders = Order.query.order_by(Order.order_date.desc()).all()
    
    # Excel 파일 생성
    data = []
    for order in orders:
        for item in order.items:
            data.append({
                '주문번호': order.id,
                '주문일시': order.order_date.strftime('%Y-%m-%d %H:%M:%S'),
                '고객명': order.customer_name,
                '배달위치': order.delivery_location,
                '메뉴명': item.menu.name,
                '수량': item.quantity,
                '단가': item.menu.price,
                '소계': item.subtotal,
                '온도': item.temperature,
                '특별요청': item.special_request or '',
                '주문상태': order.status,
                '총금액': order.total_amount
            })
    
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='주문내역')
    
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'주문내역_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )

@app.route('/admin/menu')
@admin_required
def admin_menu():
    menus = Menu.query.order_by(Menu.display_order, Menu.name).all()
    categories = db.session.query(Menu.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('admin/menu.html', menus=menus, categories=categories)

@app.route('/admin/menu/add', methods=['GET', 'POST'])
@admin_required
def admin_add_menu():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        price = float(request.form.get('price'))
        description = request.form.get('description')
        temperature_option = request.form.get('temperature_option', 'both')
        
        menu = Menu(
            name=name,
            category=category,
            price=price,
            description=description,
            temperature_option=temperature_option
        )
        
        # 이미지 업로드 처리
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                menu.image = filename
        
        db.session.add(menu)
        db.session.commit()
        
        flash('메뉴가 추가되었습니다.', 'success')
        return redirect(url_for('admin_menu'))
    
    categories = db.session.query(Menu.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('admin/add_menu.html', categories=categories)

@app.route('/admin/menu/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_menu(id):
    menu = Menu.query.get_or_404(id)
    
    if request.method == 'POST':
        menu.name = request.form.get('name')
        menu.category = request.form.get('category')
        menu.price = float(request.form.get('price'))
        menu.description = request.form.get('description')
        menu.temperature_option = request.form.get('temperature_option', 'both')
        
        # 이미지 업로드 처리
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                menu.image = filename
        
        db.session.commit()
        
        flash('메뉴가 수정되었습니다.', 'success')
        return redirect(url_for('admin_menu'))
    
    categories = db.session.query(Menu.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('admin/edit_menu.html', menu=menu, categories=categories)

@app.route('/admin/menu/delete/<int:id>')
@admin_required
def admin_delete_menu(id):
    menu = Menu.query.get_or_404(id)
    db.session.delete(menu)
    db.session.commit()
    
    flash('메뉴가 삭제되었습니다.', 'success')
    return redirect(url_for('admin_menu'))

@app.route('/admin/menu/toggle_soldout/<int:id>', methods=['POST'])
@admin_required
def admin_toggle_soldout(id):
    menu = Menu.query.get_or_404(id)
    menu.is_soldout = not menu.is_soldout
    db.session.commit()
    
    return jsonify({'success': True, 'is_soldout': menu.is_soldout})

@app.route('/admin/menu/update_order', methods=['POST'])
@admin_required
def admin_update_menu_order():
    data = request.get_json()
    for item in data:
        menu = Menu.query.get(item['id'])
        if menu:
            menu.display_order = item['order']
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/categories', methods=['GET', 'POST'])
@admin_required
def admin_categories():
    if request.method == 'POST':
        category = request.form.get('category')
        if category:
            # 새 메뉴를 추가하여 카테고리 생성
            menu = Menu(
                name=f'새 메뉴 ({category})',
                category=category,
                price=0,
                description='새로 추가된 카테고리입니다.'
            )
            db.session.add(menu)
            db.session.commit()
            flash(f'카테고리 "{category}"가 추가되었습니다.', 'success')
    
    categories = db.session.query(Menu.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/delete/<category>', methods=['POST'])
@admin_required
def admin_delete_category(category):
    # 해당 카테고리의 모든 메뉴 삭제
    Menu.query.filter_by(category=category).delete()
    db.session.commit()
    
    flash(f'카테고리 "{category}"가 삭제되었습니다.', 'success')
    return redirect(url_for('admin_categories'))

@app.route('/admin/import_orders', methods=['GET', 'POST'])
@admin_required
def admin_import_orders():
    if request.method == 'POST':
        if not PANDAS_AVAILABLE:
            flash('Excel 가져오기 기능을 사용하려면 pandas가 필요합니다.', 'error')
            return redirect(request.url)
        
        if 'file' not in request.files:
            flash('파일을 선택해주세요.', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('파일을 선택해주세요.', 'error')
            return redirect(request.url)
        
        if file and file.filename.endswith('.xlsx'):
            try:
                df = pd.read_excel(file)
                
                for _, row in df.iterrows():
                    # 주문 데이터 처리
                    order = Order(
                        customer_name=row.get('고객명', ''),
                        delivery_location=row.get('배달위치', ''),
                        total_amount=row.get('총금액', 0),
                        status=row.get('주문상태', 'pending')
                    )
                    db.session.add(order)
                    db.session.flush()
                    
                    # 주문 항목 처리
                    menu_name = row.get('메뉴명', '')
                    menu = Menu.query.filter_by(name=menu_name).first()
                    
                    if menu:
                        order_item = OrderItem(
                            order_id=order.id,
                            menu_id=menu.id,
                            quantity=row.get('수량', 1),
                            subtotal=row.get('소계', 0),
                            temperature=row.get('온도', 'ice'),
                            special_request=row.get('특별요청', '')
                        )
                        db.session.add(order_item)
                
                db.session.commit()
                flash('주문 데이터가 성공적으로 가져와졌습니다.', 'success')
                
            except Exception as e:
                flash(f'파일 처리 중 오류가 발생했습니다: {str(e)}', 'error')
        else:
            flash('Excel 파일(.xlsx)만 업로드 가능합니다.', 'error')
    
    return render_template('admin/import_orders.html')

@app.route('/admin/print_receipt/<int:id>')
@admin_required
def admin_print_receipt(id):
    order = Order.query.get_or_404(id)
    return render_template('admin/receipt.html', order=order)

@app.route('/admin/get_recent_orders')
@admin_required
def get_recent_orders():
    orders = Order.query.order_by(Order.order_date.desc()).limit(10).all()
    
    data = []
    for order in orders:
        data.append({
            'id': order.id,
            'customer_name': order.customer_name,
            'total_amount': order.total_amount,
            'status': order.status,
            'order_date': order.order_date.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(data)

@app.route('/admin/update_order_status/<int:id>', methods=['POST'])
@admin_required
def update_order_status(id):
    order = Order.query.get_or_404(id)
    status = request.form.get('status')
    
    if status in ['pending', 'preparing', 'ready', 'delivered', 'cancelled']:
        order.status = status
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': '잘못된 상태입니다.'})

@app.route('/admin/delete_order/<int:id>', methods=['POST'])
@admin_required
def delete_order(id):
    order = Order.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000) 