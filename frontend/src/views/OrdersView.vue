<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWhoAmI } from '@/composables/useWhoAmI'
import { apiRequest } from '@/utils/api'
import NavBar from '@/components/NavBar.vue'

const router = useRouter()
const { user } = useWhoAmI()

const orders = ref([])
const products = ref([])
const suppliers = ref([])
const customers = ref([])

onMounted(async () => {
  await Promise.all([
    loadOrders(),
    loadProducts(),
    loadSuppliers(),
    loadCustomers()
  ])
})

async function loadOrders() {
  const res = await apiRequest('/orders')
  const d = await res.json()
  orders.value = d.data || []
}
async function loadProducts() {
  const res = await apiRequest('/products')
  const d = await res.json()
  products.value = d.data || []
}
async function loadSuppliers() {
  const res = await apiRequest('/suppliers')
  const d = await res.json()
  suppliers.value = d.data || []
}
async function loadCustomers() {
  const res = await apiRequest('/customers')
  const d = await res.json()
  customers.value = d.data || []
}

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
  
  await apiRequest('/orders', {
    method: 'POST',
    body: orderForm.value
  })
  orderForm.value.items = []
  orderForm.value.supplier_id = ''
  orderForm.value.customer_id = ''
  await loadOrders()
  await loadProducts()
}
</script>

<template>
  <div class="dashboard">
    <NavBar />
    <div class="section" v-if="user && user.role !== 'admin'">
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
</template>
