<template>
    <div class="plugin-container view">
        <div class="plugin-header">
            <div class="plugin-title">
                <div class="title-icon">
                    <ExtensionFilledIcon size="40"/>
                </div>
                <div>
                    <h1>已安装插件</h1>
                    <p>管理已安装的全部插件</p>
                </div>
            </div>
        </div>
        <div class="plugin-tool">
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
        <div class="plugin-main">
            <div class="grid-container" v-if="align == 'grid'">
                <div class="card" v-for="(plugin, index) in pluginList" :key="index">
                    <div class="card-header">
                        <div class="plugin-author">
                            {{ plugin.author }} /
                        </div>
                        <t-switch
                            v-model="plugin.enable"
                            size="large"
                            @click.stop="onSwitchPlugin(plugin.name, plugin.enable)"
                        />
                    </div>
                    <div class="card-body">
                        <div class="plugin-name">
                            {{ plugin.name }}
                        </div>
                        <div class="plugin-version">
                            <GitBranchFilledIcon />
                            <span>{{ plugin.version }}</span>
                        </div>
                        <div class="plugin-desc">
                            <QuoteFilledIcon />
                            <span>{{ plugin.desc }}</span>
                        </div>
                    </div>
                    <div class="card-footer">
                        <div class="text-button">
                            <LogoGithubFilledIcon />
                        </div>
                        <div class="text-button">文档</div>
                        <div class="text-button">配置</div>
                        <div class="text-button">重载</div>
                        <t-popconfirm 
                            v-model="uninstallVisible" 
                            theme="danger" 
                            content="请注意，删除插件无法恢复！"
                            @confirm="onUninstallPlugin(plugin.name)"
                        >
                            <div class="text-button">卸载</div>
                        </t-popconfirm>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <t-dialog
        :visible="visibleModal"
        header="插件配置"
        mode="modal"
        draggable
        :on-close="onClose"
        :on-confirm="onComfirm"
    >
        <template #body>
            <t-form :data="formData" label-align="top">
            </t-form>
        </template>
    </t-dialog>
</template>
<script setup>
import { ref, reactive, onMounted } from "vue";
import {
    SearchIcon,
    ViewListIcon,
    GridViewIcon,
    QuoteFilledIcon,
    ExtensionFilledIcon,
    GitBranchFilledIcon,
    LogoGithubFilledIcon
} from "tdesign-icons-vue-next";
import request from "@/utils/request";

// variables
const formData = ref({})
const schemeData = ref({})
const configData = ref({})
const visibleModal = ref(false)
const uninstallVisible = ref(false)
const align = ref("grid");
const pluginList = ref([]);

// functions
const getAllPlugins = async () => {
    const res = await request.get("/plugin/list");
    pluginList.value = res.data.plugins;
};
const onSwitchPlugin = async (plugin_name, enable) => {
    await request.post("/plugin/switch", {
        plugin_name,
        enable
    })
    await getAllPlugins()
}
const onUninstallPlugin = async (plugin_name) => {
    await request.post(`/plugin/uninstall?plugin_name=${plugin_name}`)
    await getAllPlugins()
}
const onReset = () => {
    formData.value = {};
    adapterSeleted.value = null;
};
const onClose = () => {
    visibleModal.value = false;
    onReset();
};
const onComfirm = async () => {
    
}
onMounted(async () => {
    await getAllPlugins();
});
</script>
<style lang="scss" scoped>
.plugin-header {
    .plugin-title {
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

.plugin-tool {
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

.plugin-main {
    padding: 16px 0;

    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
        gap: 16px;

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;

            .plugin-author {
                tab-size: 11px;
                color: #666;
            }
        }
        
        .card-body {
            .plugin-name {
                margin-bottom: 6px;
                font-weight: 900;
                font-size: 20px;
            }

            .plugin-desc,
            .plugin-version {
                span {
                    margin-left: 12px;
                    font-size: 14px;
                }
            }
        }
    }
}


</style>