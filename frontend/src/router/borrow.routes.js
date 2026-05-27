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
        path: '/my-circulations',
        name: 'MemberCirculation',
        component: () => import('@/features/borrow/pages/member-circulation/MemberCirculation.vue'),
        meta: { requiresAuth: true, roles: ['MEMBER'] }
    },
    {
        path: '/borrows/add',
        name: 'AddBorrowPage',
        component: () => import('@/features/borrow/pages/AddBorrow.vue'),
        meta: { requiresAuth: true, permissions: [] }
    },
    {
        path: '/circulation',
        name: 'Shelf Circulation',
        component: () => import('@/features/borrow/pages/Circulation.vue'),
        meta: { requiresAuth: true, roles: ['ADMIN', 'SUPER ADMIN', 'FRONT DESK STAFF'] }
    },
    {
        path: '/overdue-letters',
        name: 'OverdueLetters',
        component: () => import('@/features/borrow/pages/OverdueLetters.vue'),
        meta: { requiresAuth: true, roles: ['ADMIN', 'SUPER ADMIN', 'STACK STAFF'] }
    },
]

