from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import db, Product

products_bp = Blueprint('products', __name__)


def product_to_dict(p):
  return {
      'id': p.id,
      'name': p.name,
      'category': p.category,
      'cost_price': p.cost_price,
      'selling_price': p.selling_price,
      'quantity': p.quantity,
      'safety_stock': p.safety_stock,
      'low_stock': p.quantity < p.safety_stock,
  }


@products_bp.route('/products', methods=['GET'])
@login_required
def get_products():
  products = Product.query.all()
  return jsonify({'data': [product_to_dict(p) for p in products]})


@products_bp.route('/products', methods=['POST'])
@login_required
def create_product():
  data = request.get_json()
  product = Product(
      name=data['name'],
      category=data['category'],
      cost_price=float(data['cost_price']),
      selling_price=float(data['selling_price']),
      quantity=int(data.get('quantity', 0)),
      safety_stock=int(data.get('safety_stock', 0)),
  )
  db.session.add(product)
  db.session.commit()
  return jsonify({'message': 'Product created', 'data': product_to_dict(product)})


@products_bp.route('/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
  product = Product.query.get(product_id)
  data = request.get_json()
  product.name = data['name']
  product.category = data['category']
  product.cost_price = float(data['cost_price'])
  product.selling_price = float(data['selling_price'])
  product.quantity = int(data['quantity'])
  product.safety_stock = int(data['safety_stock'])
  db.session.commit()
  return jsonify({'message': 'Product updated', 'data': product_to_dict(product)})


@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
  product = Product.query.get(product_id)
  db.session.delete(product)
  db.session.commit()
  return jsonify({'message': 'Product deleted'})
