from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import db, Order, OrderItem, Product, Supplier, Customer

orders_bp = Blueprint('orders', __name__)


def order_to_dict(o):
  return {
      'id': o.id,
      'order_type': o.order_type,
      'date': o.date,
      'supplier': {'id': o.supplier.id, 'name': o.supplier.name} if o.supplier else None,
      'customer': {'id': o.customer.id, 'name': o.customer.name} if o.customer else None,
      'items': [
          {
              'id': item.id,
              'product_id': item.product.id,
              'product_name': item.product.name,
              'quantity': item.quantity,
              'cost_price': item.product.cost_price,
              'selling_price': item.product.selling_price
          }
          for item in o.items
      ]
  }


@orders_bp.route('/orders', methods=['GET'])
@login_required
def get_orders():
  orders = Order.query.all()
  return jsonify({'data': [order_to_dict(o) for o in orders]})


@orders_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
  data = request.get_json()
  order_type = data['order_type']

  order = Order(
      order_type=order_type,
      date=data['date'],
      supplier_id=data.get('supplier_id'),
      customer_id=data.get('customer_id')
  )
  db.session.add(order)
  db.session.flush() # get order.id

  # Handle items and update product stock
  items_data = data.get('items', [])
  for item_data in items_data:
    product = Product.query.get(item_data['product_id'])
    if not product:
      continue

    qty = int(item_data['quantity'])

    # Adjust stock
    if order_type == 'incoming':
      product.quantity += qty
    elif order_type == 'outgoing':
      # Optionally check if qty > product.quantity here
      product.quantity -= qty

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=qty
    )
    db.session.add(order_item)

  db.session.commit()
  return jsonify({'message': 'Order created', 'data': order_to_dict(order)})
