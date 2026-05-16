export default [
  { 
    path: '/library', 
    name: 'Library', 
    component: () => import('@/features/library/pages/Library.vue'), 
    meta: { requiresAuth: true, roles: ['MEMBER', 'ADMIN', 'SUPER ADMIN'] } 
  },
  {
    path: '/library-policy',
    name: 'Library Policy',
    component: () => import('@/features/library/pages/LibraryPolicy.vue'),
    meta: { requiresAuth: true, roles: ['SUPER ADMIN'] }
  },
  { 
    path: '/libraryForm', 
    name: 'Library Form', 
    component: () => import('@/features/library/pages/AddLibrary.mdl.vue'), 
    meta: { requiresAuth: true, roles: ['MEMBER', 'ADMIN', 'SUPER ADMIN'] } 
  },
]
