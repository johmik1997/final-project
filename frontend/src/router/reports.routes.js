export default [
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/features/reports/pages/Reports.vue'),
    meta: {
      requiresAuth: true,
      roles: [
        'MEMBER',
        'ADMIN',
        'SUPER ADMIN',
        'STACK STAFF',
        'TECHNICAL STAFF',
        'FRONT DESK STAFF',
        'DEPARTMENT HEAD',
      ],
    },
  },
];
