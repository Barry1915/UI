import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/views/PublicHome.vue')
  },
  {
    path: '/admin',
    component: () => import('@/views/admin/AdminLayout.vue'),
    children: [
      { path: '', component: () => import('@/views/admin/Dashboard.vue') },
      { path: 'books', component: () => import('@/views/admin/books/BookList.vue') },
      { path: 'borrow', component: () => import('@/views/admin/circulation/BorrowReturn.vue') },
      { path: 'users', component: () => import('@/views/admin/users/UserList.vue') },
      { path: 'login', component: () => import('@/views/admin/Login.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
