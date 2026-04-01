<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')

async function login() {
  error.value = ''
  try {
    const res = await fetch('http://localhost:5000/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email: email.value, password: password.value })
    })
    const data = await res.json()
    if (!res.ok) {
      error.value = data.message || 'Login failed'
      return
    }
    router.push('/dashboard')
  } catch (err) {
    error.value = 'Network error'
  }
}
</script>

<template>
  <div class="page-center">
    <div class="card">
      <h1>Welcome back</h1>
      <p>Log in to manage your inventory</p>

      <form @submit.prevent="login">
        <div class="form-group">
          <label>Email</label>
          <input type="email" v-model="email" required />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input type="password" v-model="password" required />
        </div>
        <button type="submit" class="btn-primary">Log in</button>
      </form>
      
      <p v-if="error" class="error-msg">{{ error }}</p>

    </div>
  </div>
</template>
