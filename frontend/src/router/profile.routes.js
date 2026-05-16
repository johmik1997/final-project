export default [
  { path: '/profile', name: 'profile', component: () => import('@/features/profile/pages/profile.vue'), meta: { requiresAuth: true, permissions: [] } },
]
