<template>
    <div class="database-container view">
        <div class="database-header">
            <div class="database-title">
                <div class="title-icon">
                    <DataBaseFilledIcon size="40" />
                </div>
                <div>
                    <h1>数据库</h1>
                    <p>管理系统缓存信息和数据库数据</p>
                </div>
            </div>
        </div>
        <div class="database-body">
            <t-tabs :value="value">
                <t-tab-panel value="first" label="Mongodb 数据库">
                    <div class="panel">
                        <div class="filter">
                            <div class="left-filter">
                                <t-select
                                    class="filter-item" 
                                    label="适配器:" 
                                    v-model="adapter"
                                    :options="adapterOptions"
                                />
                                <t-select class="filter-item" label="来源:" v-model="source">
                                    <t-option
                                        key="chatroom"
                                        label="群聊"
                                        value="chatroom"
                                    />
                                    <t-option
                                        key="friend"
                                        label="私聊"
                                        value="friend"
                                    />
                                </t-select>
                                <t-input class="filter-item" v-model="keyword"/>
                                
                            </div>
                            <div class="right-filter">
                                <t-button variant="outline" @click="onReset">
                                    <template #icon><FilterClearIcon /></template>
                                    重置
                                </t-button>
                                <t-button variant="outline" style="margin-left: 16px" @click="getDatabaseData">
                                    <template #icon><SearchIcon /></template>
                                    搜索
                                </t-button>
                            </div>
                        </div>
                        <div class="table">
                            <t-table
                                row-key="index"
                                :data="data"
                                :columns="columns"
                                hover
                                size="small"
                                :height="calculatedHeight"
                                show-header
                                cell-empty-content="-"
                            >
                                <template #operation="{ row }">
                                    <t-button size="small">
                                        <template #icon><DeleteIcon /></template>
                                        删除记录
                                    </t-button>
                                </template>
                            </t-table>
                            <t-pagination
                                style="margin-top: 16px"
                                v-model="pagination.current"
                                v-model:pageSize="pagination.limit"
                                :total="pagination.total"
                                @change="getDatabaseData"
                            />
                        </div>
                    </div>
                </t-tab-panel>
                <t-tab-panel value="second" label="Redis 缓存">
                    <p>
                        {{ `${theme}选项卡2内容` }}
                    </p>
                </t-tab-panel>
            </t-tabs>
        </div>
    </div>
</template>
<script lang="jsx" setup>
import { ref, reactive, onMounted, computed, onBeforeUnmount } from "vue";
import { DataBaseFilledIcon, SearchIcon, FilterClearIcon, DeleteIcon } from "tdesign-icons-vue-next";
import { timestamp_format } from '@/utils/time'
import request from "@/utils/request";

// variables
const data = ref([])
const adapter = ref(null)
const source = ref(null)
const keyword = ref(null)
const winHeight = ref(window.innerHeight)
const value = ref("first");
const adapterOptions = ref([])
const pagination = reactive({
    current: 1,
    limit: 10,
    total: 10,
})
const columns = ref([
    { colKey: "msg_id", title: "消息ID", width: "120"},
    { colKey: "content", title: "消息内容", ellipsis: true },
    { colKey: "adapter_name", title: "适配器", width: "150" },
    { 
        colKey: "source", 
        title: "来源", 
        width: "100",
        cell: (h, { row }) => (
            row.source == "chatroom" ? "群聊" : "私聊"
        )    
    },
    { colKey: "fromname", title: "发送人", width: "150", ellipsis: true},
    { 
        colKey: "create_time", 
        title: "创建时间", 
        width: "160", 
        cell: (h, { row }) => (
            timestamp_format(row.create_time)
        )
    },
    { colKey: 'operation', title: '操作', width: "100"}
]);

const calculatedHeight = computed(() => {
    return Math.max(winHeight.value - 415, 100)
})
// functions
const getDatabaseData = async () => {
    let url = `/db/mongodb?page=${pagination.current}&limit=${pagination.limit}`
    if (adapter.value) {
        url += `&adapter_name=${adapter.value}`
    }
    if (source.value) {
        url += `&source=${source.value}`
    }
    if (keyword.value) {
        url += `&content=${keyword.value}`
    }
    const resp = await request.get(url)
    const db = resp.data.mongodb
    data.value = db.items
    pagination.current = db.page
    pagination.limit = db.limit
    pagination.total = db.total
};
const getAllAdapters = async () => {
    const res = await request.get("/adapter/list");
    adapterOptions.value = res.data.adapters.map((adapter) => ({
        label: adapter.name,
        value: adapter.id,
        title: adapter.name,
    }));
};
const onReset = async () => {
    source.value = null
    adapter.value = null
    keyword.value = null
    await getDatabaseData()
}
const updateHeight = () => {
    winHeight.value = window.innerHeight
}
onMounted(async () => {
    window.addEventListener('resize', updateHeight)
    await getAllAdapters()
    await getDatabaseData()
})
onBeforeUnmount(() => {
    window.removeEventListener('resize', updateHeight)
})
</script>
<style lang="scss">
.database-header {
    margin-bottom: 24px;
    .database-title {
        display: flex;
        align-items: center;

        .title-icon {
            margin-right: 12px;
            color: #5a5a5a;
        }

        h1 {
            font-weight: 700;
            font-size: 24px;
        }
        p {
            // margin-top: 8px;
            font-size: 13px;
        }
    }
}
.database-body {
    background-color: #fff;
    padding: 16px;
    border-radius: 4px;

    .panel {
        padding: 24px 12px 0 12px;

        .filter {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;

            .left-filter {
                display: flex;
                align-items: center;
                .filter-item {
                    width: 180px;
                    margin-right: 20px;
                }
            }
        }
    }
}
.tabs-icon-margin {
    margin-right: 4px;
}
tbody {
    height: 100px;
    overflow: auto;
}
</style>