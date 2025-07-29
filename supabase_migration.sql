-- Supabase 카페 관리 시스템 데이터베이스 마이그레이션
-- PostgreSQL용 테이블 생성 스크립트

-- 1. 메뉴 테이블 생성
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

-- 2. 주문 테이블 생성
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

-- 3. 주문 아이템 테이블 생성
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

-- 4. 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_menu_category ON cafe_menu(category);
CREATE INDEX IF NOT EXISTS idx_menu_display_order ON cafe_menu(display_order);
CREATE INDEX IF NOT EXISTS idx_order_date ON cafe_order(order_date);
CREATE INDEX IF NOT EXISTS idx_order_status ON cafe_order(status);
CREATE INDEX IF NOT EXISTS idx_order_item_order_id ON cafe_order_item(order_id);
CREATE INDEX IF NOT EXISTS idx_order_item_menu_id ON cafe_order_item(menu_id);

-- 5. RLS (Row Level Security) 정책 설정
-- 메뉴 테이블 - 모든 사용자가 읽기 가능
ALTER TABLE cafe_menu ENABLE ROW LEVEL SECURITY;
CREATE POLICY "메뉴 읽기 정책" ON cafe_menu FOR SELECT USING (true);

-- 주문 테이블 - 관리자만 모든 작업 가능
ALTER TABLE cafe_order ENABLE ROW LEVEL SECURITY;
CREATE POLICY "주문 관리자 정책" ON cafe_order FOR ALL USING (auth.role() = 'authenticated');

-- 주문 아이템 테이블 - 관리자만 모든 작업 가능
ALTER TABLE cafe_order_item ENABLE ROW LEVEL SECURITY;
CREATE POLICY "주문 아이템 관리자 정책" ON cafe_order_item FOR ALL USING (auth.role() = 'authenticated');

-- 6. 샘플 데이터 삽입
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
('망고 스무디', '스무디', 6000, '달콤한 망고의 부드러운 맛', 'ice', 10);

-- 7. 함수 생성 (업데이트 시간 자동 갱신)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 8. 트리거 생성
CREATE TRIGGER update_cafe_menu_updated_at BEFORE UPDATE ON cafe_menu
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cafe_order_updated_at BEFORE UPDATE ON cafe_order
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 9. 뷰 생성 (주문 상세 정보)
CREATE OR REPLACE VIEW order_details AS
SELECT 
    o.id as order_id,
    o.order_date,
    o.status,
    o.total_amount,
    o.customer_name,
    o.delivery_location,
    o.delivery_time,
    o.order_request,
    oi.id as item_id,
    oi.quantity,
    oi.subtotal,
    oi.special_request,
    oi.temperature,
    m.name as menu_name,
    m.category as menu_category,
    m.price as menu_price
FROM cafe_order o
LEFT JOIN cafe_order_item oi ON o.id = oi.order_id
LEFT JOIN cafe_menu m ON oi.menu_id = m.id;

-- 10. 통계 함수 생성
CREATE OR REPLACE FUNCTION get_daily_sales(date_param DATE)
RETURNS TABLE(
    total_orders INTEGER,
    total_amount INTEGER,
    avg_order_amount DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_orders,
        COALESCE(SUM(total_amount), 0)::INTEGER as total_amount,
        COALESCE(AVG(total_amount), 0)::DECIMAL(10,2) as avg_order_amount
    FROM cafe_order 
    WHERE DATE(order_date) = date_param;
END;
$$ LANGUAGE plpgsql; 