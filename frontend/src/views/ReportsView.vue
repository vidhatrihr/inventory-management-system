<script setup>
import { ref, onMounted, computed } from 'vue'
import { apiRequest } from '@/utils/api'
import NavBar from '@/components/NavBar.vue'

const products = ref([])

onMounted(async () => {
  const res = await apiRequest('/products')
  const d = await res.json()
  products.value = d.data || []
})

const inventoryValue = computed(() => {
  return products.value.reduce((sum, p) => sum + (p.quantity * p.cost_price), 0)
})

function fmtCurrency(amount) {
  return '₹' + Number(amount).toFixed(2)
}
</script>

<template>
  <div class="dashboard">
    <NavBar />
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
</template>
