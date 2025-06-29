<template>
    <div class="log-container view">
        <div class="log-main">
            <div class="filter">
                <div class="filter-header">过滤器</div>
                <div class="filter-block">
                    <div class="filter-title">
                        <h1>日志级别</h1>
                        <p>显示要显示日志的级别</p>
                    </div>
                    <div class="filter-body">
                        <div class="filter-item">
                            <div class="log-info">
                                <p class="log-level info">INFO</p>
                                <p class="log-count">总计 {{ logs.filter(log => log.level == "INFO").length}} 条记录</p>
                            </div>
                            <label class="switch">
                                <input type="checkbox" v-model="filters.info"/>
                                <span class="slider"></span>
                            </label>
                        </div>
                        <div class="filter-item">
                            <div class="log-info">
                                <p class="log-level success">SUCCESS</p>
                                <p class="log-count">总计 {{ logs.filter(log => log.level == "SUCCESS").length}} 条记录</p>
                            </div>
                            <label class="switch">
                                <input type="checkbox" v-model="filters.success"/>
                                <span class="slider"></span>
                            </label>
                        </div>
                        <div class="filter-item">
                            <div class="log-info">
                                <p class="log-level error">ERROR</p>
                                <p class="log-count">总计 {{ logs.filter(log => log.level == "ERROR").length}} 条记录</p>
                            </div>
                            <label class="switch">
                                <input type="checkbox" v-model="filters.error"/>
                                <span class="slider"></span>
                            </label>
                        </div>
                        <div class="filter-item">
                            <div class="log-info">
                                <p class="log-level warning">WARNING</p>
                                <p class="log-count">总计 {{ logs.filter(log => log.level == "WARNING").length}} 条记录</p>
                            </div>
                            <label class="switch">
                                <input type="checkbox" v-model="filters.warning"/>
                                <span class="slider"></span>
                            </label>
                        </div>
                        <div class="filter-item">
                            <div class="log-info">
                                <p class="log-level debug">DEBUG</p>
                                <p class="log-count">总计 {{ logs.filter(log => log.level == "DEBUG").length}} 条记录</p>
                            </div>
                            <label class="switch">
                                <input type="checkbox" v-model="filters.debug"/>
                                <span class="slider"></span>
                            </label>
                        </div>
                    </div>
                </div>
                <div class="filter-block">
                    <div class="filter-title">
                        <h1>关键词搜索</h1>
                        <p>在当前日志中搜索</p>
                    </div>
                    <div class="filter-body">
                        <t-tag-input v-model="keywords" placeholder="输入关键词" clearable />
                    </div>
                </div>  
                
            </div>
            <div class="logs">
                <div v-for="(log, index) in filteredLogs" class="log-entry">
                    <div class="log-header">
                        <div class="log-info">
                            <span class="log-level" :class="`${log.level.toLowerCase()}`">{{ log.level }}</span>
                            <span class="timestamp">{{ timestamp_format(log.time) }}</span>
                            <span class="module">{{ log.function }}</span>
                        </div>
                        <div class="log-number">
                            <span class="line-number">{{ index }}</span>
                        </div>
                    </div>
                    <div class="log-content">
                        {{ log.message }}
                    </div>
                    
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, computed, reactive  } from "vue";
import { useLogStore } from "@/store/log";
import { storeToRefs } from "pinia";
import { timestamp_format } from '@/utils/time'

// variables
const logStore = useLogStore();
const keywords = ref([])
const filters = reactive({
    info: true,
    error: true,
    debug: true,
    success: true,
    warning: true
});

const { logs } = storeToRefs(logStore);

// computed
const filteredLogs = computed(() => {
    const levelMap = {
        success: filters.success,
        debug: filters.debug,
        info: filters.info,
        error: filters.error,
        warning: filters.warning
    };
    return logs.value.filter(log => levelMap[log.level.toLowerCase()] && keywords.value.every(keyword => log.message.includes(keyword)));
});


// functions
const formatTime = (timestamp) => {
    const date = timestamp ? new Date(timestamp) : new Date();
    return date.toLocaleTimeString();
};


</script>

<style lang="scss" scoped>
.log-container {
    display: flex;
    justify-content: center;
    align-items: center;

    .log-main {
        display: flex;
        height: 100%;
        width: 100%;
        overflow: hidden;
        border-radius: 8px;
        box-shadow: 0 6px 12px #0000001a;
        background-color: #fafafa;

        .filter {
            padding: 12px 24px 12px 12px;
            width: 260px;
            height: 100%;
            font-weight: 600;
            background-color: #fafafa;
            overflow-y: auto;
            scrollbar-width: none;
            .filter-header {
                font-size: 14px;
                color: #666;
            }

            .filter-block {
                margin: 20px 0;
                padding: 24px;
                border-radius: 8px;
                background-color: #fff;
                box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);

                .filter-title {
                    h1 {
                        font-size: 15px;
                        color: #232323;
                    }
                    p {
                        margin-top: 8px;
                        font-size: 12px;
                        color: #7e7d7d;
                    }
                }

                .filter-body {
                    margin-top: 40px;

                    .filter-item {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin: 10px 0;
                        .log-level {
                            font-size: 14px;

                            &.error {
                                color: #C2494B;
                            }
                            &.warning {
                                color: #EDC460;
                            }
                            &.info {
                                color: #6291CC;
                            }
                            &.debug {
                                color: #888B90;
                            }
                            &.success {
                                color: #4EE390;
                            }
                        }
                        .log-count {
                            font-size: 12px;
                            color: #86868b;
                            margin: 0;
                        }
                    }
                }
            }
        }

        .logs {
            padding:  12px 32px;
            flex: 1;
            background-color: #fff;
            box-shadow: -12px 0 15px -10px rgba(0, 0, 0, 0.02);
            border-top-left-radius: 8px;
            border-bottom-left-radius: 8px;
            overflow-y: auto;
            .log-entry {
                margin: 12px 0;
                padding: 8px 16px;
                border-radius: 10px;
                border-bottom: 1px solid #f0f0f0;
                font-size: 13px;
                line-height: 1.4;
                box-shadow: 0 1px 3px rgba(0,0,0,0.2);

                .log-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;

                    .log-level {
                        padding: 2px 8px;
                        border-radius: 3px;
                        font-weight: 500;
                        font-size: 11px;
                        margin-right: 12px;
                        min-width: 50px;
                        text-align: center;

                        &.error {
                            background-color: #C2494B;
                            color: #fff;
                        }

                        &.success {
                            background-color: 	#dcfce7;
                            color: #166534;
                        }

                        &.warning {
                            background-color: 	#fef9c3;
                            color: #854d0e;
                        }

                        &.info {
                            color: #fff;
                            background-color: #000;
                        }

                        &.debug {
                            background-color: #e1eaff;
                            color: #1e40af;
                        }
                    }

                    .timestamp {
                        color: #666;
                        font-weight: 600;
                        margin-right: 12px;
                        font-family: 'Courier New', monospace;
                        font-size: 14px;
                    }

                    .module {
                        color: #333;
                        font-weight: 600;
                        margin-right: 12px;
                    }
                }
                
                .log-content {
                    margin: 16px 0 4px 0;
                }
            }
        }
    }
}

/* Toggle Switch Styles */
.switch {
    position: relative;
    display: inline-block;
    width: 38px;
    height: 22px;

    input {
        opacity: 0;
        width: 0;
        height: 0;
    }
}

.slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #151515;
    transition: 0.3s;
    border-radius: 50px;
}

.slider:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: 2px;
    bottom: 2px;
    background-color: white;
    transition: 0.3s;
    border-radius: 50%;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

input:checked + .slider:before {
    transform: translateX(14px);
}

input:not(:checked) + .slider {
    background-color: #e5e5e7;
}
</style>

