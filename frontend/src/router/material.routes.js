export default [
  { 
    path: '/material', 
    name: 'Material', 
    component: () => import('@/features/material/pages/Material.vue'), 
    meta: { requiresAuth: true, permissions: [] } 
  },
  {
    path: '/material/:materialId',
    name: 'Material Detail',
    component: () => import('@/features/material/pages/MaterialDetail.vue'),
    meta: { requiresAuth: true, permissions: [] }
  },
  {
    path: '/material/:materialId/read',
    name: 'Material Reader',
    component: () => import('@/features/material/pages/MaterialReader.vue'),
    meta: { requiresAuth: true, permissions: [] }
  },
  { 
    path: '/edit_material/:materialUuid', 
    name: 'edit material', 
    component: () => import('@/features/material/pages/EditMaterial.vue'), 
    meta: { requiresAuth: true, permissions: [] } 
  },
  { 
    path: '/materialForm', 
    name: 'Material Form', 
    component: () => import('@/features/material/pages/AddMaterial.mdl.vue'), 
    meta: { requiresAuth: true, permissions: [] } 
  },
]
