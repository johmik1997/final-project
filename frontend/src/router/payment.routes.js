export default [
  {
    path: '/fine-payments',
    name: 'FinePayments',
    component: () => import('@/features/payment/pages/FinePayments.vue'),
    meta: { requiresAuth: true, roles: ['MEMBER', 'ADMIN', 'SUPER ADMIN'] },
  },
];
