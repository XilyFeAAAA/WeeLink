<template>
    <router-view></router-view>
</template>


<script setup>
import { useSSEStore } from '@/store/sse'
import { onMounted, onUnmounted } from 'vue'

// variables
const sseStore = useSSEStore()

// functions
onMounted(async () => {
    await sseStore.connectSSE()
})

onUnmounted(() => {
    sseStore.disconnectSSE()
})
</script>

<style scoped>
</style>
