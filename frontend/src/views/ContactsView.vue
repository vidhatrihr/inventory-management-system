<script setup>
import { ref, onMounted } from 'vue'
import { apiRequest } from '@/utils/api'
import NavBar from '@/components/NavBar.vue'

const suppliers = ref([])
const customers = ref([])

const supplierForm = ref({ name: '', contact: '' })
const customerForm = ref({ name: '', contact: '' })

onMounted(async () => {
  await Promise.all([
    loadSuppliers(),
    loadCustomers()
  ])
})

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

async function addSupplier() {
  await apiRequest('/suppliers', {
    method: 'POST',
    body: supplierForm.value
  })
  supplierForm.value = { name: '', contact: '' }
  await loadSuppliers()
}
async function deleteSupplier(id) {
  await apiRequest(`/suppliers/${id}`, { method: 'DELETE' })
  await loadSuppliers()
}

async function addCustomer() {
  await apiRequest('/customers', {
    method: 'POST',
    body: customerForm.value
  })
  customerForm.value = { name: '', contact: '' }
  await loadCustomers()
}
async function deleteCustomer(id) {
  await apiRequest(`/customers/${id}`, { method: 'DELETE' })
  await loadCustomers()
}
</script>

<template>
  <div class="dashboard">
    <NavBar />
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
</template>
