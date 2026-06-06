import { createRouter, createWebHistory } from 'vue-router'
import { useWhoAmI } from '@/composables/useWhoAmI.js'
import LoginView from '../views/LoginView.vue'
import OrdersView from '../views/OrdersView.vue'
import ProductsView from '../views/ProductsView.vue'
import ContactsView from '../views/ContactsView.vue'
import ReportsView from '../views/ReportsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: LoginView, meta: { guestOnly: true } },
    { path: '/login', redirect: '/' },
    { path: '/orders', component: OrdersView, meta: { requiresAuth: true } },
    { path: '/products', component: ProductsView, meta: { requiresAuth: true } },
    { path: '/contacts', component: ContactsView, meta: { requiresAuth: true } },
    { path: '/reports', component: ReportsView, meta: { requiresAuth: true } },
  ],
})

router.beforeEach(async (to, from) => {
  const { whoAmI, clearUser } = useWhoAmI()

  if (from.meta.guestOnly && to.meta.requiresAuth) {
    clearUser()
  }

  const me = await whoAmI()

  if (to.meta.requiresAuth && !me) {
    return '/'
  }
  if (to.meta.guestOnly && me) {
    return '/orders'
  }
})

export default router
