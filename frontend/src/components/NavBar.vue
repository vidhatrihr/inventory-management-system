<script setup>
import { useRouter, useRoute } from 'vue-router'
import { useWhoAmI } from '@/composables/useWhoAmI'
import { apiRequest } from '@/utils/api'

const router = useRouter()
const route = useRoute()
const { user, clearUser } = useWhoAmI()

async function logout() {
  await apiRequest('/logout', { method: 'POST' })
  clearUser()
  router.push('/login')
}
</script>

<template>
  <div v-if="user">
    <div class="dashboard-header">
      <div>
        <h1>Welcome, {{ user.name }} ({{ user.role }})</h1>
      </div>
      <button @click="logout" class="btn-danger">Sign out</button>
    </div>

    <!-- TABS -->
    <div class="tabs">
      <button class="tab" :class="{active: route.path === '/orders'}" @click="router.push('/orders')">Orders</button>
      <button v-if="user.role === 'admin'" class="tab" :class="{active: route.path === '/products'}" @click="router.push('/products')">Products</button>
      <button v-if="user.role === 'admin'" class="tab" :class="{active: route.path === '/contacts'}" @click="router.push('/contacts')">Contacts</button>
      <button v-if="user.role === 'admin'" class="tab" :class="{active: route.path === '/reports'}" @click="router.push('/reports')">Reports</button>
    </div>
  </div>
</template>
