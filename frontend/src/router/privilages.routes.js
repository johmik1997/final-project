export default [
  { path: '/privileges', name: 'Privileges', component: () => import('@/features/privilages/pages/Privileges.vue'), meta: { requiresAuth: true, permissions: [] } },
  { path: '/add_privilege', name: 'Add Privileges', component: () => import('@/features/privilages/pages/AddPrivilege.vue'), meta: { requiresAuth: true, permissions: [] } },
  { path: '/edit_privilege/:privilegeUuid', name: 'Update Privileges', component: () => import('@/features/privilages/pages/EditPrivilege.vue'), meta: { requiresAuth: true, permissions: [] } },
]
