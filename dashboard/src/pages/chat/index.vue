<template>
    <div class="chat-container view">
        <div class="chat-header">
            <div class="chat-title">
                <div class="title-icon">
                    <ChatMessageFilledIcon size="40"/>
                </div>
                <div>
                    <h1>会话</h1>
                    <p>管理不同账户，连接到不同的适配器</p>
                </div>
            </div>
        </div>
        <div class="chat-tool">
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
        <div class="chat-main">
            <div class="grid-container" v-if="align == 'grid'">
                <div class="card" @click="addBot()">
                    <div class="card-body add-adapter">
                        <PlusIcon size="100" style="color: #666" />
                    </div>
                </div>
                <div class="card" v-for="(bot, index) in botList" :key="index">
                    <div class="card-header">
                        <div class="card-title">
                            {{ bot.alias }}
                        </div>
                        <t-switch
                            v-model="bot.state"
                            size="large"
                            @click.stop="onSwitchBot(bot.id, bot.state)"
                        />
                    </div>
                    <div class="card-body">
                        <div class="adapter">
                            <TagFilledIcon />
                            <span>{{ bot.adapter }} 适配器</span>
                        </div>
                        <div class="desc">
                            <QuoteFilledIcon />
                            <span>{{ bot.desc }}</span>
                        </div>
                    </div>
                    <div class="card-footer">
                        
                        <t-popconfirm theme="default" @confirm="onDeleteBot(bot.id)">
                            <template #content>
                                <p class="title">确认删除会话吗</p>
                                <p class="describe">
                                    会话删除后将无法进行恢复！
                                </p>
                            </template>
                            <div class="text-button">删除</div>
                        </t-popconfirm>
                        <div class="text-button">编辑</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <t-dialog
        :visible="visibleModal"
        header="创建会话"
        mode="modal"
        draggable
        :on-close="onClose"
        :on-confirm="onComfirm"
    >
        <template #body>
            <t-form :data="formData" label-align="top">
                <t-form-item label="机器人名称" name="alias" requiredMark>
                    <t-input v-model="formData.alias"></t-input>
                </t-form-item>
                <t-form-item label="机器人描述" name="desc" requiredMark>
                    <t-input v-model="formData.desc"></t-input>
                </t-form-item>
                <t-form-item label="适配器选择" name="adapter" requiredMark>
                    <t-select
                        v-model="formData.adapter"
                        :options="adapterOptions"
                        placeholder="请选择适配器"
                        style="width: 220px"
                        @change="onChange"
                    />
                </t-form-item>
            </t-form>
            <Transition>
                <div v-if="adapterSeleted">
                    <div class="chat-box">
                        <div class="icon">
                            <TagFilledIcon size="32" />
                        </div>
                        <div class="chat-info">
                            <div class="chat-name">
                                {{ adapterSeleted.name }}
                            </div>
                            <div class="chat-desc">
                                {{ adapterSeleted.desc }}
                            </div>
                        </div>
                    </div>
                    <div class="adapter-config">
                        <h1>适配器配置</h1>
                        <t-form :data="adapter_config" label-align="top">
                            <t-form-item
                                v-for="field in adapterSeleted.fields"
                                :key="field.key"
                                :label="field.label"
                            >
                                <component
                                    :is="getFieldComponent(field)"
                                    v-model="configData[field.key]"
                                    v-bind="getFieldProps(field)"
                                />
                            </t-form-item>
                        </t-form>
                    </div>
                </div>
            </Transition>
        </template>
    </t-dialog>
</template>
<script setup>
import { ref, reactive, onMounted } from "vue";
import {
    SearchIcon,
    ViewListIcon,
    GridViewIcon,
    PlusIcon,
    TagFilledIcon,
    QuoteFilledIcon,
    ChatMessageFilledIcon
} from "tdesign-icons-vue-next";
import request from "@/utils/request";

// variables
const align = ref("grid");
const adapterSeleted = ref(null);
const visibleModal = ref(false);
const formData = ref({});
const configData = ref({});
const adapterOptions = ref([]);
const botList = ref([]);
const adapterList = ref([]);

// functions
const getFieldComponent = (field) => {
    switch (field.type) {
        case "string":
            return "t-input";
        case "boolean":
            return "t-switch";
    }
};
const getFieldProps = (field) => {
    const props = {};
    if (field.placeholder) props.placeholder = field.placeholder;
    if (field.options && field.type === "select") {
        props.options = field.options;
    }
    return props;
};
const onChecking = () => {};
const getAllBots = async () => {
    const res = await request.get("/bot/list");
    botList.value = res.data.bots;
};
const getAllAdapters = async () => {
    const res = await request.get("/adapter/list");
    adapterList.value = res.data.adapters;
    adapterOptions.value = res.data.adapters.map((adapter) => ({
        label: adapter.name,
        value: adapter.id,
        title: adapter.name,
    }));
};
const addBot = async () => {
    await getAllAdapters();
    visibleModal.value = !visibleModal.value;
};
const onChange = async () => {
    if (formData.value.adapter === null) return;
    const res = await request.get(
        `/adapter?adapter_id=${formData.value.adapter}`
    );
    adapterSeleted.value = res.data.adapter;
};
const onReset = () => {
    formData.value = {};
    configData.value = {};
    adapterSeleted.value = null;
};
const onClose = () => {
    visibleModal.value = false;
    onReset();
};
const onComfirm = async () => {
    await request.post("/bot/add", {
        alias: formData.value.alias,
        desc: formData.value.desc,
        state: true,
        adapter_name: adapterSeleted.value.name,
        adapter_id: adapterSeleted.value.id,
        adapter_config: configData.value,
    });
    await getAllBots()
};
const onSwitchBot = async (bot_id, state) => {
    await request.post("/bot/switch", {
        bot_id,
        state
    })
    await getAllBots()
}
const onDeleteBot = async (bot_id) => {
    await request.post(`/bot/del?bot_id=${bot_id}`)
    await getAllBots()
}
onMounted(async () => {
    await getAllBots();
});
</script>
<style lang="scss" scoped>
.chat-header {
    .chat-title {
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

.chat-tool {
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

.chat-main {
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

                .desc,
                .adapter {
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

.chat-box {
    margin: 24px 0;
    display: flex;
    align-items: center;
    padding: 16px;
    border-radius: 10px;
    border: 1px solid #e7e3e4;

    .chat-info {
        margin-left: 24px;

        .chat-name {
            font-size: 16px;
        }

        .chat-desc {
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