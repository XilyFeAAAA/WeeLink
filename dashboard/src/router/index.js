import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

const routes = [
    {
        path: '/',
        component: DefaultLayout,
        children: [
            {
                path: '/',
                redirect: '/dashboard'
            },
            {
                path: '/dashboard',
                component: () => import('@/pages/dashboard/index.vue'),
                name: 'dashboard'
            },
            {
                path: '/chat',
                component: () => import('@/pages/chat/index.vue'),
                name: 'chat'
            },
            {
                path: '/adapter',
                component: () => import('@/pages/adapter/index.vue'),
                name: 'adapter'
            },
                        {
                path: '/plugin',
                component: () => import('@/pages/plugin/index.vue'),
                name: 'plugin'
            },
            {
                path: '/log',
                component: () => import('@/pages/log/index.vue'),
                name: 'log',
                meta: { keepAlive: true }
            },
            {
                path: '/about',
                component: () => import('@/pages/about/index.vue'),
                name: 'about'
            }
        ]
    },
    {
        path: '/login',
        component: () => import('@/pages/login/index.vue'),
        name: 'login'
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    const auth = useAuthStore()

    const publicPages = ['/login']
    const authRequired = !publicPages.includes(to.path)

    if (authRequired && !auth.token) {
        return next('/login')
    }

    next()
})

export default router