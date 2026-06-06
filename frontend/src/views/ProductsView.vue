<script setup>
import { ref, onMounted } from 'vue'
import { apiRequest } from '@/utils/api'
import NavBar from '@/components/NavBar.vue'

const products = ref([])
const productForm = ref({ id: null, name: '', category: '', cost_price: 0, selling_price: 0, quantity: 0, safety_stock: 0 })

onMounted(async () => {
  await loadProducts()
})

async function loadProducts() {
  const res = await apiRequest('/products')
  const d = await res.json()
  products.value = d.data || []
}

function editProduct(p) {
  productForm.value = { ...p }
}
function clearProductForm() {
  productForm.value = { id: null, name: '', category: '', cost_price: 0, selling_price: 0, quantity: 0, safety_stock: 0 }
}

async function saveProduct() {
  const isEdit = !!productForm.value.id
  const url = isEdit ? `/products/${productForm.value.id}` : `/products`
  const method = isEdit ? 'PUT' : 'POST'
  
  await apiRequest(url, {
    method,
    body: productForm.value
  })
  clearProductForm()
  await loadProducts()
}

async function deleteProduct(id) {
  await apiRequest(`/products/${id}`, { method: 'DELETE' })
  await loadProducts()
}
</script>

<template>
  <div class="dashboard">
    <NavBar />
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
</template>
