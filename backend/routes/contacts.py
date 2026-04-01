from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import db, Supplier, Customer, Order

contacts_bp = Blueprint('contacts', __name__)


# ---------------- Suppliers ----------------

def supplier_to_dict(s):
    return {'id': s.id, 'name': s.name, 'contact': s.contact}

@contacts_bp.route('/suppliers', methods=['GET'])
@login_required
def get_suppliers():
    suppliers = Supplier.query.all()
    return jsonify({'data': [supplier_to_dict(s) for s in suppliers]})

@contacts_bp.route('/suppliers', methods=['POST'])
@login_required
def create_supplier():
    data = request.get_json()
    supplier = Supplier(name=data['name'], contact=data.get('contact', ''))
    db.session.add(supplier)
    db.session.commit()
    return jsonify({'message': 'Supplier created', 'data': supplier_to_dict(supplier)})

@contacts_bp.route('/suppliers/<int:supplier_id>', methods=['PUT'])
@login_required
def update_supplier(supplier_id):
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        return jsonify({'message': 'Supplier not found'}), 404
        
    data = request.get_json()
    supplier.name = data.get('name', supplier.name)
    supplier.contact = data.get('contact', supplier.contact)
    db.session.commit()
    return jsonify({'message': 'Supplier updated', 'data': supplier_to_dict(supplier)})

@contacts_bp.route('/suppliers/<int:supplier_id>', methods=['DELETE'])
@login_required
def delete_supplier(supplier_id):
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        return jsonify({'message': 'Supplier not found'}), 404
    
    # Check if supplier has orders
    orders_count = Order.query.filter_by(supplier_id=supplier_id).count()
    if orders_count > 0:
        return jsonify({'message': 'Cannot delete supplier with existing orders'}), 400
        
    db.session.delete(supplier)
    db.session.commit()
    return jsonify({'message': 'Supplier deleted'})


# ---------------- Customers ----------------

def customer_to_dict(c):
    return {'id': c.id, 'name': c.name, 'contact': c.contact}

@contacts_bp.route('/customers', methods=['GET'])
@login_required
def get_customers():
    customers = Customer.query.all()
    return jsonify({'data': [customer_to_dict(c) for c in customers]})

@contacts_bp.route('/customers', methods=['POST'])
@login_required
def create_customer():
    data = request.get_json()
    customer = Customer(name=data['name'], contact=data.get('contact', ''))
    db.session.add(customer)
    db.session.commit()
    return jsonify({'message': 'Customer created', 'data': customer_to_dict(customer)})

@contacts_bp.route('/customers/<int:customer_id>', methods=['PUT'])
@login_required
def update_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'message': 'Customer not found'}), 404
        
    data = request.get_json()
    customer.name = data.get('name', customer.name)
    customer.contact = data.get('contact', customer.contact)
    db.session.commit()
    return jsonify({'message': 'Customer updated', 'data': customer_to_dict(customer)})

@contacts_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
@login_required
def delete_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'message': 'Customer not found'}), 404
        
    # Check if customer has orders
    orders_count = Order.query.filter_by(customer_id=customer_id).count()
    if orders_count > 0:
        return jsonify({'message': 'Cannot delete customer with existing orders'}), 400
        
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted'})
