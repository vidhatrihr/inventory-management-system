<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const API = 'http://localhost:5000/api'
const opts = { credentials: 'include' }

// Auth State
const user = ref({ name: '', role: '' })
const activeTab = ref('orders') // orders, products, contacts, reports

// Data State
const products = ref([])
const orders = ref([])
const suppliers = ref([])
const customers = ref([])

onMounted(async () => {
  try {
    const res = await fetch(`${API}/me`, opts)
    if (!res.ok) throw new Error('Not logged in')
    const data = await res.json()
    user.value = data.data
    
    // Load all data
    await Promise.all([
      loadProducts(),
      loadOrders(),
      loadSuppliers(),
      loadCustomers()
    ])
  } catch (err) {
    router.push('/')
  }
})

async function logout() {
  await fetch(`${API}/logout`, { method: 'POST', ...opts })
  router.push('/')
}

function fmtCurrency(amount) {
  return '₹' + Number(amount).toFixed(2)
}

// -----------------  DATA LOADERS -----------------
async function loadProducts() {
  const res = await fetch(`${API}/products`, opts)
  const d = await res.json()
  products.value = d.data || []
}
async function loadOrders() {
  const res = await fetch(`${API}/orders`, opts)
  const d = await res.json()
  orders.value = d.data || []
}
async function loadSuppliers() {
  const res = await fetch(`${API}/suppliers`, opts)
  const d = await res.json()
  suppliers.value = d.data || []
}
async function loadCustomers() {
  const res = await fetch(`${API}/customers`, opts)
  const d = await res.json()
  customers.value = d.data || []
}

// -----------------  PRODUCTS -----------------
const productForm = ref({ id: null, name: '', category: '', cost_price: 0, selling_price: 0, quantity: 0, safety_stock: 0 })

function editProduct(p) {
  productForm.value = { ...p }
}
function clearProductForm() {
  productForm.value = { id: null, name: '', category: '', cost_price: 0, selling_price: 0, quantity: 0, safety_stock: 0 }
}

async function saveProduct() {
  const isEdit = !!productForm.value.id
  const url = isEdit ? `${API}/products/${productForm.value.id}` : `${API}/products`
  const method = isEdit ? 'PUT' : 'POST'
  
  await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    ...opts,
    body: JSON.stringify(productForm.value)
  })
  clearProductForm()
  await loadProducts()
}

async function deleteProduct(id) {
  await fetch(`${API}/products/${id}`, { method: 'DELETE', ...opts })
  await loadProducts()
}

// -----------------  CONTACTS -----------------
const supplierForm = ref({ name: '', contact: '' })
const customerForm = ref({ name: '', contact: '' })

async function addSupplier() {
  await fetch(`${API}/suppliers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    ...opts,
    body: JSON.stringify(supplierForm.value)
  })
  supplierForm.value = { name: '', contact: '' }
  await loadSuppliers()
}
async function deleteSupplier(id) {
  await fetch(`${API}/suppliers/${id}`, { method: 'DELETE', ...opts })
  await loadSuppliers()
}

async function addCustomer() {
  await fetch(`${API}/customers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    ...opts,
    body: JSON.stringify(customerForm.value)
  })
  customerForm.value = { name: '', contact: '' }
  await loadCustomers()
}
async function deleteCustomer(id) {
  await fetch(`${API}/customers/${id}`, { method: 'DELETE', ...opts })
  await loadCustomers()
}

// -----------------  ORDERS -----------------
const orderForm = ref({
  order_type: 'incoming',
  date: new Date().toISOString().split('T')[0],
  supplier_id: '',
  customer_id: '',
  items: []
})
const tempItem = ref({ product_id: '', quantity: 1 })

function addOrderItem() {
  if (!tempItem.value.product_id || tempItem.value.quantity < 1) return
  // Check if exists, update qty
  const existing = orderForm.value.items.find(i => i.product_id === tempItem.value.product_id)
  if (existing) {
    existing.quantity += tempItem.value.quantity
  } else {
    orderForm.value.items.push({ ...tempItem.value })
  }
  tempItem.value = { product_id: '', quantity: 1 }
}

function removeOrderItem(index) {
  orderForm.value.items.splice(index, 1)
}

function getProdName(id) {
  const p = products.value.find(x => x.id === id)
  return p ? p.name : 'Unknown'
}

async function submitOrder() {
  if (orderForm.value.items.length === 0) return alert('Add at least one item')
  
  await fetch(`${API}/orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    ...opts,
    body: JSON.stringify(orderForm.value)
  })
  orderForm.value.items = []
  orderForm.value.supplier_id = ''
  orderForm.value.customer_id = ''
  await loadOrders()
  await loadProducts() // refresh stock
}


// -----------------  REPORTS -----------------
const inventoryValue = computed(() => {
  return products.value.reduce((sum, p) => sum + (p.quantity * p.cost_price), 0)
})
</script>

<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <div>
        <h1>Welcome, {{ user.name }} ({{ user.role }})</h1>
      </div>
      <button @click="logout" class="btn-danger">Sign out</button>
    </div>

    <!-- TABS -->
    <div class="tabs">
      <button class="tab" :class="{active: activeTab === 'orders'}" @click="activeTab='orders'">Orders</button>
      <button v-if="user.role === 'admin'" class="tab" :class="{active: activeTab === 'products'}" @click="activeTab='products'">Products</button>
      <button v-if="user.role === 'admin'" class="tab" :class="{active: activeTab === 'contacts'}" @click="activeTab='contacts'">Contacts</button>
      <button v-if="user.role === 'admin'" class="tab" :class="{active: activeTab === 'reports'}" @click="activeTab='reports'">Reports</button>
    </div>

    <!-- ================= ORDERS VIEW ================= -->
    <div v-if="activeTab === 'orders'">
      <div class="section" v-if="user.role !== 'admin'">
        <h2>Create New Order</h2>
        <form @submit.prevent="submitOrder">
          <div class="grid-form">
            <div class="form-group">
              <label>Type</label>
              <select v-model="orderForm.order_type">
                <option value="incoming">Incoming (From Supplier)</option>
                <option value="outgoing">Outgoing (To Customer)</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Date</label>
              <input type="date" v-model="orderForm.date" required />
            </div>

            <div class="form-group" v-if="orderForm.order_type === 'incoming'">
              <label>Supplier</label>
              <select v-model="orderForm.supplier_id" required>
                <option value="" disabled>Select Supplier</option>
                <option v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
            </div>

            <div class="form-group" v-if="orderForm.order_type === 'outgoing'">
              <label>Customer</label>
              <select v-model="orderForm.customer_id" required>
                <option value="" disabled>Select Customer</option>
                <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
          </div>

          <h3 style="margin: 1rem 0 0.5rem; font-size: 1rem;">Add Products to Order</h3>
          <div style="display: flex; gap: 1rem; align-items: end; margin-bottom: 1rem; background: var(--surface-alt); padding: 1rem; border-radius: var(--radius)">
            <div class="form-group" style="flex: 2; margin-bottom: 0;">
              <select v-model="tempItem.product_id">
                <option value="" disabled>Choose Product</option>
                <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }} (In Stock: {{ p.quantity }})</option>
              </select>
            </div>
            <div class="form-group" style="flex: 1; margin-bottom: 0;">
              <input type="number" v-model="tempItem.quantity" min="1" placeholder="Qty" />
            </div>
            <button type="button" @click="addOrderItem" class="btn-primary" style="margin-top:0; width: auto; height: 42px;">Add</button>
          </div>

          <!-- Items List -->
          <ul style="margin-bottom: 1rem; padding-left: 1rem; color: var(--text-muted);">
            <li v-for="(item, idx) in orderForm.items" :key="idx" style="margin-bottom: 0.5rem">
              {{ getProdName(item.product_id) }} &times; {{ item.quantity }}
              <button type="button" @click="removeOrderItem(idx)" class="btn-danger" style="margin-left: 1rem; border:none;">Remove</button>
            </li>
          </ul>

          <button type="submit" class="btn-primary" :disabled="orderForm.items.length === 0">Submit Order</button>
        </form>
      </div>

      <div class="section">
        <h2>Order History</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Type</th>
              <th>Date</th>
              <th>Partner</th>
              <th>Items</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="o in orders" :key="o.id">
              <td>#{{ o.id }}</td>
              <td>
                <span :class="o.order_type === 'incoming' ? 'accent' : 'danger'" style="text-transform: capitalize">
                  {{ o.order_type }}
                </span>
              </td>
              <td>{{ o.date }}</td>
              <td>{{ o.order_type === 'incoming' ? o.supplier?.name : o.customer?.name }}</td>
              <td>
                <div v-for="i in o.items" :key="i.id" style="font-size: 0.85rem; color: var(--text-muted)">
                   {{ i.quantity }}x {{ i.product_name }}
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ================= PRODUCTS VIEW ================= -->
    <div v-if="activeTab === 'products' && user.role === 'admin'">
      <div class="section">
        <h2>{{ productForm.id ? 'Edit Product' : 'Add New Product' }}</h2>
        <form @submit.prevent="saveProduct" class="grid-form">
          <div class="form-group">
            <label>Name</label>
            <input type="text" v-model="productForm.name" required />
          </div>
          <div class="form-group">
            <label>Category</label>
            <input type="text" v-model="productForm.category" required />
          </div>
          <div class="form-group">
            <label>Cost Price</label>
            <input type="number" step="0.01" v-model="productForm.cost_price" required />
          </div>
          <div class="form-group">
            <label>Selling Price</label>
            <input type="number" step="0.01" v-model="productForm.selling_price" required />
          </div>
          <div class="form-group">
            <label>Current Qty</label>
            <input type="number" v-model="productForm.quantity" />
          </div>
          <div class="form-group">
            <label>Safety Stock</label>
            <input type="number" v-model="productForm.safety_stock" />
          </div>
          <div style="display:flex; gap:0.5rem; margin-bottom: 1rem;">
             <button type="submit" class="btn-primary">{{ productForm.id ? 'Update' : 'Add' }}</button>
             <button v-if="productForm.id" type="button" @click="clearProductForm" class="btn-danger" style="margin-top:0; height: 42px;">Cancel</button>
          </div>
        </form>
      </div>

      <div class="section">
        <h2>Inventory Items</h2>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Category</th>
              <th>Cost (₹)</th>
              <th>Sell (₹)</th>
              <th>Qty Left</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in products" :key="p.id">
              <td>
                {{ p.name }}
                <span v-if="p.low_stock" class="low-stock" style="margin-left:0.5rem; font-size:0.8rem">⚠️ Low</span>
              </td>
              <td>{{ p.category }}</td>
              <td>{{ p.cost_price }}</td>
              <td>{{ p.selling_price }}</td>
              <td :class="{'low-stock': p.low_stock}">{{ p.quantity }} / {{ p.safety_stock }}</td>
              <td>
                <button @click="editProduct(p)" class="btn-primary" style="padding:0.2rem 0.5rem; width:auto; margin:0 0.5rem 0 0">Edit</button>
                <button @click="deleteProduct(p.id)" class="btn-danger">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>


    <!-- ================= CONTACTS VIEW ================= -->
    <div v-if="activeTab === 'contacts' && user.role === 'admin'">
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
        
        <!-- SUPPLIERS -->
        <div class="section">
          <h2>Suppliers</h2>
          <form @submit.prevent="addSupplier" style="display:flex; gap: 0.5rem; margin-bottom: 1rem; align-items: end;">
            <div class="form-group" style="flex: 1; margin-bottom: 0;">
              <input type="text" v-model="supplierForm.name" placeholder="Name" required />
            </div>
            <button type="submit" class="btn-primary" style="margin-top:0; width:auto; height: 42px;">Add</button>
          </form>
          <table>
            <tbody>
              <tr v-for="s in suppliers" :key="s.id">
                <td>{{ s.name }}</td>
                <td style="text-align:right">
                   <button @click="deleteSupplier(s.id)" class="btn-danger">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- CUSTOMERS -->
        <div class="section">
          <h2>Customers</h2>
          <form @submit.prevent="addCustomer" style="display:flex; gap: 0.5rem; margin-bottom: 1rem; align-items: end;">
            <div class="form-group" style="flex: 1; margin-bottom: 0;">
              <input type="text" v-model="customerForm.name" placeholder="Name" required />
            </div>
            <button type="submit" class="btn-primary" style="margin-top:0; width:auto; height: 42px;">Add</button>
          </form>
          <table>
            <tbody>
              <tr v-for="c in customers" :key="c.id">
                <td>{{ c.name }}</td>
                <td style="text-align:right">
                   <button @click="deleteCustomer(c.id)" class="btn-danger">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>

    <!-- ================= REPORTS VIEW ================= -->
    <div v-if="activeTab === 'reports' && user.role === 'admin'">
      <div class="section">
        <h2>Dashboard Reports</h2>
        
        <div style="display:flex; gap: 2rem; margin-top: 1rem;">
          <div style="background: var(--surface-alt); padding: 1.5rem; border-radius: var(--radius); border: 1px solid var(--border); flex:1">
            <div style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.5rem">Total Inventory Value (Cost)</div>
            <div style="font-size: 2rem; font-weight: 600; color: var(--accent)">{{ fmtCurrency(inventoryValue) }}</div>
          </div>
          
          <div style="background: var(--surface-alt); padding: 1.5rem; border-radius: var(--radius); border: 1px solid var(--border); flex:1">
            <div style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.5rem">Total Products Checked</div>
            <div style="font-size: 2rem; font-weight: 600;">{{ products.length }} items</div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
