<template>
    <div ref="containerRef" class="terminal-container view">
        <div class="terminal"  :style="{ width: terminalWidth, height: terminalHeight }">
            <div class="terminal-header">
                <div class="ellipse red"></div>
                <div class="ellipse yellow"></div>
                <div class="ellipse green"></div>
                终端@WeeLink
            </div>
            <div class="terminal-body">
                <div 
                    v-for="(log, index) in logs" 
                    :key="index" 
                    :class="`log-item log-${log.type || 'info'}`"
                    :style="{ color: getFontColor(log.level)}"
                >
                    <span class="log-time"> [{{ formatTime(log.time) }}] </span>
                    <span class="log-file"> [{{ log.function }}:{{ log.line }}] </span>
                    <span class="log-level"> [{{ log.level }}] </span>
                    <span class="log-content">{{ log.message || JSON.stringify(log) }}</span>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from "vue";
import { useSSEStore } from '@/store/sse'
import { storeToRefs } from 'pinia'

// variables
const sseStore = useSSEStore()
const containerRef = ref(null);
const terminalWidth = ref(null);
const terminalHeight = ref(null)
const { logs } = storeToRefs(sseStore)
let observer = null;

// functions
const formatTime = (timestamp) => {
    const date = timestamp ? new Date(timestamp) : new Date();
    return date.toLocaleTimeString();
};

const getFontColor = (level) => {
    switch (level) {
        case "INFO":
            return "#90D5ED"
        case "SUCCESS":
            return "#4EE390"
        case "WARNING":
            return "#F97538"
        case "ERROR":
            return "#FA342E"
        case "CRITICAL":
            return "#6D3F87"
    }
}

onMounted(() => {
    observer = new ResizeObserver((entries) => {
        const width = entries[0].contentRect.width;
        const height = entries[0].contentRect.height;
        terminalWidth.value = width < 1300 ? `${width * 0.95}px` : "1235px";
        terminalHeight.value = height < 960 ? `${height * 0.7}px` : "672px";
    });

    if (containerRef.value) {
        observer.observe(containerRef.value);
    }
    
});

onBeforeUnmount(() => {
    if (observer && containerRef.value) {
        observer.unobserve(containerRef.value);
    }

});
</script>

<style lang="scss" scoped>
.terminal-container {
    display: flex;
    justify-content: center;
    align-items: center;

    .terminal {
        display: flex;
        flex-direction: column;
        box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.25);
        border-radius: 8px;

        .terminal-header {
            position: relative;
            width: 100%;
            height: 48px;
            line-height: 48px;
            text-align: center;
            background: #F5F5F5;
            box-shadow: 0px 1px 0px #D2D2D2;

            .ellipse {
                position: absolute;
                width: 16px;
                height: 16px;
                top: calc(50% - 6px);
                border-radius: 50%;

                &.red {
                    left: 16px;
                    background-color: #D83B3B;
                }

                &.green {
                    left: 40px;
                    background-color: #E2C423;
                }

                &.yellow {
                    left: 64px;
                    background-color: #03CA0B;
                }
            }
        }

        .terminal-body {
            flex: 1;
            padding: 8px 16px;
            font-family: 'Roboto Mono', monospace;
            font-weight: 500;
            font-size: 12px;
            line-height: 18px;
            overflow-y: auto;
            background-color: #fff;
            color: #1E1E1E;
            
            .log-item {
                margin-bottom: 4px;
                word-break: break-word;
                
                .log-time {
                    color: #888888;
                    margin-right: 8px;
                }
                
                &.log-error .log-content {
                    color: #FF6B6B;
                }
                
                &.log-warning .log-content {
                    color: #FFCC00;
                }
                
                &.log-success .log-content {
                    color: #4CD964;
                }
            }
        }
    }
}
</style>

