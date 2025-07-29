from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Menu(db.Model):
    __tablename__ = 'cafe_menu'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    temperature_option = db.Column(db.String(20), default='both')
    display_order = db.Column(db.Integer, default=9999)
    is_soldout = db.Column(db.Boolean, default=False)
    
    # 관계 설정
    order_items = db.relationship('OrderItem', backref='menu', lazy=True)
    
    def __repr__(self):
        return f'<Menu {self.name}>'

class Order(db.Model):
    __tablename__ = 'cafe_order'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.String(20), nullable=False, default='pending')
    total_amount = db.Column(db.Integer, nullable=False)
    customer_name = db.Column(db.String(50), nullable=False)
    delivery_location = db.Column(db.String(100), nullable=False)
    delivery_time = db.Column(db.String(50), nullable=True)
    order_request = db.Column(db.Text, nullable=True)
    
    # 관계 설정
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.id}>'

class OrderItem(db.Model):
    __tablename__ = 'cafe_order_item'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('cafe_order.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('cafe_menu.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    special_request = db.Column(db.Text)
    temperature = db.Column(db.String(10), default='ice')
    
    def __repr__(self):
        return f'<OrderItem {self.id}>' 