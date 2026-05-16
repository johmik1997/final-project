export default [
  { path: '/roles', name: 'Roles', component: () => import('@/features/roles/pages/Role.vue'), meta: { requiresAuth: true, permissions: [] } },
  { path: '/add_role', name: 'Add Role', component: () => import('@/features/roles/pages/AddRole.vue'), meta: { requiresAuth: true, permissions: [] } },
  { path: '/edit_role/:roleUuid', name: 'Update Role', component: () => import('@/features/roles/pages/EditRole.vue'), meta: { requiresAuth: true, permissions: [] } },
]
