const transferRoutes = [
  {
    path: '/transfer-requests',
    name: 'TransferRequests',
    component: () => import('@/features/transfer/pages/TransferRequests.vue'),
    meta: {
      requiresAuth: true,
      roles: ['SUPER ADMIN', 'ADMIN', 'FRONT DESK STAFF', 'FRONTDESK STAFF', 'STACK STAFF'],
    },
  },
];

export default transferRoutes;

// export default [
//   {
//     path: '/returns',
//     name: 'Returns',
//     component: () => import('@/features/returns/pages/Returns.vue'),
//     meta: { requiresAuth: true, roles: ['STACK STAFF', 'ADMIN', 'SUPER ADMIN'] },
//   },
// ];

