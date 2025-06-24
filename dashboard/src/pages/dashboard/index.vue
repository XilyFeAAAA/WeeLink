<template>
    <div class="dashboard-container view">
        <div class="dashboard-header">
            <h1>控制台</h1>
            <div class="dashboard-controls">
                <button class="control-btn"><i class='bx bx-calendar'></i> Oct 18 - Nov 18</button>
                <button class="control-btn">Monthly <i class='bx bx-chevron-down'></i></button>
                <button class="control-btn"><i class='bx bx-filter'></i> Filter</button>
                <button class="control-btn"><i class='bx bx-export'></i> Export</button>
            </div>
        </div>
        <div class="dashboard-grid">
            <!-- Stat Card: Page Views -->
            <t-card bordered hoverShadow class="card">
                <template #header>
                    <div class="card-header">
                        <div class="card-icon">
                            <ChatMessageIcon size="18"/>
                        </div>
                        <div class="card-title">
                            消息数
                        </div>
                    </div>
                </template>
                <div class="card-body">
                    <h2>12,450</h2>
                    <span class="percentage green">15.8%</span>
                </div>
            </t-card>
            <t-card bordered hoverShadow class="card">
                <template #header>
                    <div class="card-header">
                        <div class="card-icon">
                            <LayersFilledIcon size="18"/>
                        </div>
                        <div class="card-title">
                            适配器数
                        </div>
                    </div>
                </template>
                <div class="card-body">
                    <h2>1</h2>
                </div>
            </t-card>
            <t-card bordered hoverShadow class="card">
                <template #header>
                    <div class="card-header">
                        <div class="card-icon">
                            <TimeIcon size="18"/>
                        </div>
                        <div class="card-title">
                            运行时间
                        </div>
                    </div>
                </template>
                <div class="card-body">
                    <h2>11小时15分5秒</h2>
                </div>
            </t-card>

            <t-card bordered hoverShadow class="card sales-overview">
                <template #header>
                    <div class="card-header">
                        <div class="card-icon">
                            <ChatMessageIcon size="18"/>
                        </div>
                        <div class="card-title">
                            消息趋势分析
                        </div>
                    </div>
                </template>
                <div class="card-body chart">
                    <MessageTrend/>
                </div>
            </t-card>

            <t-card bordered hoverShadow class="card">
                <template #header>
                    <div class="card-header">
                        <div class="card-icon">
                            <ChatMessageIcon size="18"/>
                        </div>
                        <div class="card-titl">
                            日均消息统计
                        </div>
                    </div>
                </template>
                <div class="card-body chart">
                    <MessageBar/>
                </div>
            </t-card>

            <t-card bordered hoverShadow class="card">
                <template #header>
                    <div class="card-header">
                        <div class="card-icon">
                            <ChatMessageIcon size="18"/>
                        </div>
                        <div class="card-title">
                            消息数
                        </div>
                    </div>
                </template>
                <div class="card-body">
                    <h2>12,450</h2>
                    <span class="percentage green">15.8%</span>
                </div>
            </t-card>
            <t-card bordered hoverShadow class="card">
                <template #header>
                    <div class="card-header">
                        <div class="card-icon">
                            <ChatMessageIcon size="18"/>
                        </div>
                        <div class="card-title">
                            消息数
                        </div>
                    </div>
                </template>
                <div class="card-body">
                    <h2>12,450</h2>
                    <span class="percentage green">15.8%</span>
                </div>
            </t-card>

        </div>
    </div>
</template>
<script setup>
    import {
        ChatMessageIcon,
        TimeIcon,
        LayersFilledIcon
    } from 'tdesign-icons-vue-next'
    import MessageTrend from '@/components/MessageTrend.vue'
    import MessageBar from '@/components/MessageBar.vue'
</script>
<style lang="scss" scoped>
    .dashboard-container {
        .dashboard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;

            h1 { 
                font-size: 28px; 
            }

            .dashboard-controls { 
                display: flex; 
                gap: 12px; 
            }

            .control-btn {
                background-color: white;
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 8px;
                cursor: pointer;
                color: var(--secondary-text);

                .small { 
                    padding: 6px 12px; 
                    font-size: 13px; 
                }
            }
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;

            .card {
                .card-header {                    
                    display: flex;
                    align-items: center;
                    .card-icon{
                        padding: 4px 6px;
                        border-radius: 8px;
                        color: rgb(131, 131, 131);
                        background-color: rgba(201, 199, 199, .2);
                    }
                    .card-title{
                        margin-left: 16px;
                        font-size: 15px;
                        font-weight: 600;
                    }
                }

                .card-body {
                    display: flex;
                    align-items: center;
                    margin-bottom: 16px;
                    padding: 0 24px;
                    h2 {
                        font-size: 30px;
                        font-weight: 500;
                        margin-right: 16px;
                    }
                    .percentage {
                        font-weight: 600;
                        padding: 1px 10px;
                        border-radius: 8px;
                        font-size: 13px;

                        &.green { background-color: #E2F5EA; color: var(--green); }
                        &.red { background-color: #F8D7DA; color: var(--red); }
                    }

                    &.chart {
                        height: 295px;
                    }
                }
            }
            .sales-overview {
                grid-column: 1 / 3;
            }
        }
    }

</style>