<template>
    <router-view></router-view>
</template>


<script setup>
import { useLogStore } from '@/store/log'
import { onMounted, onUnmounted } from 'vue'

// variables
const logStore = useLogStore()

// functions
onMounted(async () => {
    await logStore.getTodayLogs()
    await logStore.connectSSE()
})

onUnmounted(() => {
    logStore.disconnectSSE()
})
</script>

<style scoped>
</style>
