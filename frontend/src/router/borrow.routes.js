export default [
    {
        path: '/borrows',
        name: 'Borrow',
        component: () => import('@/features/borrow/pages/borrow.vue'),
            meta: { requiresAuth: true, permissions: [] } 

    },
    {
        path: '/my-borrows',
        name: 'MemberBorrow',
        component: () => import('@/features/borrow/pages/member-borrow/MemberBorrow.vue'),
        meta: { requiresAuth: true, roles: ['MEMBER'] }
    },
    {
        path: '/borrows/add',
        name: 'AddBorrowPage',
        component: () => import('@/features/borrow/pages/AddBorrow.vue'),
        meta: { requiresAuth: true, permissions: [] }
    },
]
