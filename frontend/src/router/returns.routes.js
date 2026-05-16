export default [
  {
    path: '/returns',
    name: 'Returns',
    component: () => import('@/features/returns/pages/Returns.vue'),
    meta: { requiresAuth: true, roles: ['STACK STAFF', 'ADMIN', 'SUPER ADMIN'] },
  },
];

