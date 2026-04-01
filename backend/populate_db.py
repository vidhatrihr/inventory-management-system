from werkzeug.security import generate_password_hash
from models import db, User, Product, Supplier, Customer, Order, OrderItem


def seed_db():
    # no-op if data already exists
    if User.query.count() > 0:
        return

    # seed users
    admin = User(
        name='Admin',
        email='admin@example.com',
        password=generate_password_hash('password123'),
        role='admin'
    )
    manager = User(
        name='Manager',
        email='manager@example.com',
        password=generate_password_hash('password123'),
        role='manager'
    )
    db.session.add_all([admin, manager])
    db.session.flush()

    # seed suppliers
    s1 = Supplier(name='TechParts Ltd', contact='techparts@email.com')
    s2 = Supplier(name='OfficeWorld', contact='office@world.com')
    db.session.add_all([s1, s2])
    db.session.flush()

    # seed customers
    c1 = Customer(name='Acme Corp', contact='acme@corp.com')
    c2 = Customer(name='BuildRight', contact='build@right.com')
    db.session.add_all([c1, c2])
    db.session.flush()

    # seed products
    p1 = Product(name='USB Hub', category='Electronics', cost_price=300, selling_price=500, quantity=50, safety_stock=10)
    p2 = Product(name='Notebook', category='Stationery', cost_price=40, selling_price=80, quantity=200, safety_stock=30)
    p3 = Product(name='Webcam', category='Electronics', cost_price=800, selling_price=1500, quantity=8, safety_stock=10)
    p4 = Product(name='Desk Lamp', category='Furniture', cost_price=500, selling_price=900, quantity=25, safety_stock=5)
    db.session.add_all([p1, p2, p3, p4])
    db.session.flush()

    # seed an incoming order
    o1 = Order(order_type='incoming', date='2024-03-01', supplier_id=s1.id)
    db.session.add(o1)
    db.session.flush()
    db.session.add_all([
        OrderItem(order_id=o1.id, product_id=p1.id, quantity=20),
        OrderItem(order_id=o1.id, product_id=p3.id, quantity=5),
    ])

    # seed an outgoing order
    o2 = Order(order_type='outgoing', date='2024-03-05', customer_id=c1.id)
    db.session.add(o2)
    db.session.flush()
    db.session.add_all([
        OrderItem(order_id=o2.id, product_id=p1.id, quantity=3),
        OrderItem(order_id=o2.id, product_id=p2.id, quantity=10),
    ])

    db.session.commit()
    print('Database seeded.')
    print('  Admin:   admin@example.com / password123')
    print('  Manager: manager@example.com / password123')
