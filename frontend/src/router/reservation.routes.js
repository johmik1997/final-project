export default [
  {
    path: '/reservations',
    name: 'Reservations',
    component: () => import('@/features/reservation/pages/Reservation.vue'),
    meta: { requiresAuth: true, roles: ['MEMBER'] },
  },
  {
    path: '/member-reservation',
    name: 'Member Reservation',
    component: () => import('@/features/reservation/pages/member-reservation/MemberReservation.vue'),
    meta: { requiresAuth: true, roles: ['MEMBER'] },
  },
];
