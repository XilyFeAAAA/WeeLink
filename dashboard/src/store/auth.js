import { defineStore } from 'pinia'
import router from '@/router'
import request from '@/utils/request'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('token') || '',
        username: localStorage.getItem('username') || '',
    }),

    actions: {
        async login(username, password) {
            try {
                const res = await request.post('/auth/login', { username, password })
                this.token = res.data.token
                this.username = username
                localStorage.setItem('token', this.token)
                localStorage.setItem('username', username)
                router.push('/')
            } catch (error) {
                console.error('登录失败', error)
                throw error
            }
        },

        logout() {
            this.token = ''
            this.username = ''
            localStorage.removeItem('token')
            localStorage.removeItem('username')
            router.push('/login')
        }
    }
})
