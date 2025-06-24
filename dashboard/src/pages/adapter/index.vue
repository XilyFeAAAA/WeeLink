<template>
    <div class="adapter-container view">
        <div class="adapter-header">
            <div class="adapter-title">
                <div class="title-icon">
                    <LayersFilledIcon size="40"/>
                </div>
                <div>
                    <h1>适配器</h1>
                    <p>管理不同适配器，连接到不同的微信协议</p>
                </div>
            </div>
        </div>
        <div class="adapter-tool">
            <div class="search-bar">
                <SearchIcon />
                <input type="text" placeholder="Search" />
            </div>

            <div class="switcher">
                <button
                    :class="{ active: align === 'grid' }"
                    @click="align = 'grid'"
                >
                    <GridViewIcon size="20" />
                </button>
                <button
                    :class="{ active: align === 'list' }"
                    @click="align = 'list'"
                >
                    <ViewListIcon size="20" />
                </button>
            </div>
        </div>
        <div class="adapter-main">
            <div class="grid-container" v-if="align == 'grid'">
                <div class="card" v-for="adapter in adapterList" :key="adapter.id">
                    <div class="card-header">
                        <div class="card-title">
                            {{ adapter.name }}
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="card-item">
                            <QuoteFilledIcon />
                            <span>{{ adapter.desc }}</span>
                        </div>
                        <div class="card-item">
                            <GitBranchFilledIcon />
                            <span>{{ adapter.version }} 版本</span>
                        </div>
                        <div class="card-item">
                            <ScreencastFilledIcon />
                            <span>{{ adapter.platform }} 设备</span>
                        </div>
                    </div>
                    <div class="card-footer">
                        <div class="text-button" @click="getAdapterDocs(adapter.id)">文档</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <t-dialog
        :visible="visibleModal"
        width="55%"
        :footer="false"
        :on-close="onClose"
    >
        <template #body>
            <Markdown :markdown="docs"></Markdown>
        </template>
    </t-dialog>
</template>
<script setup>
import { ref, reactive, onMounted } from "vue";
import {
    SearchIcon,
    ViewListIcon,
    GridViewIcon,
    TagFilledIcon,
    QuoteFilledIcon,
    LayersFilledIcon,
    GitBranchFilledIcon,
    ScreencastFilledIcon
} from "tdesign-icons-vue-next";
import Markdown from '@/components/Markdown.vue'
import request from "@/utils/request";

// variables
const align = ref("grid")
const docs = ref(null)
const visibleModal = ref(false)
const adapterList = ref([])

// functions
const getAdapterDocs = async (adapter_id) => {
    const res = await request.get(`/adapter/docs?adapter_id=${adapter_id}`);
    docs.value = res.data.docs;
    visibleModal.value = true
}
const getAllAdapters = async () => {
    const res = await request.get("/adapter/list");
    adapterList.value = res.data.adapters;
};
const onClose = () => {
    visibleModal.value = false 
}
onMounted(async () => {
    await getAllAdapters();
});
</script>
<style lang="scss" scoped>
.adapter-header {
    .adapter-title {
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

.adapter-tool {
    display: flex;
    align-items: center;
    margin-top: 24px;
    .search-bar {
        flex: 1;
        display: flex;
        align-items: center;
        background-color: white;
        border: 1px solid var(--border-color);
        border-radius: 5px;
        padding: 10px 12px;
        width: 320px;

        input {
            border: none;
            outline: none;
            margin-left: 12px;
            font-size: 15px;
            flex-grow: 1;
            background: transparent;
        }
    }

    .switcher {
        display: flex;
        align-items: center;
        margin-left: 16px;
        padding: 3px;
        background: #fff;
        border: 1px solid #eaeaea;
        border-radius: 5px;
        height: 40px;
        user-select: none;

        button {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 40px;
            height: 32px;
            color: #888;
            border-radius: 5px;
            background-color: #fff;
            cursor: pointer;
            transition: 0.2s ease-in-out;

            &:hover {
                color: #000;
            }

            &.active {
                color: #000;
                background-color: #eaeaea;
            }
        }
    }
}

.adapter-main {
    padding: 16px 0;

    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
        gap: 16px;

        .card {
            .card-header {
                display: flex;
                align-items: center;
                justify-content: space-between;

                .card-title {
                    font-weight: 600;
                    font-size: 16px;
                    color: rgba(0, 0, 0, 0.87);
                }
            }
            .card-body {
                height: 100%;
                padding: 16px 0;

                .card-item {
                    span {
                        margin-left: 12px;
                        font-size: 14px;
                    }
                }

                &.add-adapter {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
            }
        }
    }
}

.adapter-box {
    margin: 24px 0;
    display: flex;
    align-items: center;
    padding: 16px;
    border-radius: 10px;
    border: 1px solid #e7e3e4;

    .adapter-info {
        margin-left: 24px;

        .adapter-name {
            font-size: 16px;
        }

        .adapter-desc {
            margin-top: 2px;
            font-size: 12px;
        }
    }
}

.adapter-config {
    padding: 12px 0;
    border-top: 1px solid #eaeaea;

    h1 {
        font-size: 16px;
        margin-bottom: 12px;
    }
}

.title {
    font-weight: 500;
    font-size: 14px;
}
.describe {
    margin-top: 8px;
    font-size: 12px;
    color: var(--td-text-color-secondary);
}

.v-enter-active,
.v-leave-active {
    transition: opacity 0.5s ease;
}

.v-enter-from,
.v-leave-to {
    opacity: 0;
}
</style>