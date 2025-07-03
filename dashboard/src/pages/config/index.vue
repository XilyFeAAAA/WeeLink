<template>
    <div class="config-container view">
        <div class="config-body">
            <form>
                <div v-for="(group,  gindex) in scheme" :key="gindex" class="config-group">
                    <h1>{{ group.title }} <span>({{ group.desc}})</span></h1>
                    <div class="items">
                        <template v-for="(item, iindex) in group.items" :key="iindex">
                            <div class="config-item">
                                <div class="config-info">
                                    <div class="config-title">
                                        {{ item.label }} <span>({{ item.key }})</span>
                                    </div>
                                    <div class="config-desc">
                                        {{ item.desc }}
                                    </div>
                                </div>
                                <div class="config-type">
                                    <span>{{ item.type }}</span>
                                </div>
                                <div class="config-input">
                                    <input v-if="item.type=='input'" class="wl-input" v-model="formData[item.key]"></input>
                                    <t-switch v-else-if="item.type=='bool'" size="large" formData[item.key]/>
                                    <t-select
                                        v-else-if="item.type=='select'"
                                        v-model="formData[item.key]"
                                        :options="item.options"
                                        :popup-props="{ overlayClassName: 'tdesign-demo-select__overlay-option' }"
                                    />
                                </div>
                            </div>
                            <div v-if="iindex!=group.items.length-1" class="divider"></div>
                        </template>
                    </div>
                </div>
            </form>
        </div>
        <div class="update-btn" @click.stop="uploadConfig">
            <BackupFilledIcon />
        </div>
    </div>
</template>
<script setup>
import { ref, onMounted } from "vue";
import { MessagePlugin } from 'tdesign-vue-next';
import { BackupFilledIcon } from "tdesign-icons-vue-next";
import request from "@/utils/request";
// variables
const formData = ref({});
const scheme = ref();
// functions
const getConfig = async () => {
    const resp = await request.get("/config");
    formData.value = resp.data.data;
    scheme.value = resp.data.scheme;
};
const uploadConfig = async () => {
    const resp = await request.post("/config/update", {
        config: formData.value
    })
    if (resp.status === 200){
        MessagePlugin.success('配置更新成功，请重启WeeLink应用新配置')
    }
}
onMounted(async () => {
    await getConfig();
});
</script>
<style lang="scss" scoped>
.view {
    overflow: auto;
}
.config-body {
    background-color: #fff;
    padding: 24px;
    border-radius: 4px;

    .config-group {
        h1 {
            font-size: 18px;
            margin-bottom: 12px;
            span {
                font-size: 14px;
                color: rgba(0, 0, 0, 0.87);
                opacity: 0.7;
            }
        }
        .divider {
            margin: 10px 0;
            width: 100%;
            height: 1px;
            background-color: rgba(0, 0, 0, 0.3);
        }
        .config-item {
            display: flex;
            align-items: center;
            margin: 4px 0;
            padding: 8px 20px;
            border-radius: 4px;
            transition: 0.2s ease-in-out;
            .config-info {
                width: 50%;
                color: rgba(0, 0, 0, 0.87);
                font-size: 14px;
                font-weight: 600;
                span {
                    font-size: 12px;
                    font-weight: 400;
                    opacity: 0.7;
                }
                .config-desc {
                    margin-top: 4px;
                    font-size: 13px;
                    font-weight: 400;
                    opacity: 0.6;
                }
            }
            .config-type {
                flex: 1;
                text-align: right;
                span {
                    padding: 3px 8px;
                    font-size: 11px;
                    text-align: center;
                    color: #fff;
                    border-radius: 4px;
                    background-color: #1e88e5;
                }
            }
            .config-input {
                width: 45%;
                padding: 0 32px;
                input {
                    max-width: 420px;
                }
            }
            &:hover {
                background-color: rgba(0, 0, 0, 0.03);
            }
        }
    }
}
.update-btn {
    position: fixed;
    display: flex;
    justify-content: center;
    align-items: center;
    right: 64px;
    bottom: 64px;
    padding: 20px;
    border: 2px solid #fff;
    font-size: 25px;
    cursor: pointer;
    overflow: hidden;
    transition: all 0.3s;
    border-radius: 50%;
    background-color: #ecd448;

    &:before {
        content: "";
        position: absolute;
        width: 100px;
        height: 120%;
        background-color: #ff6700;
        top: 50%;
        transform: skewX(30deg) translate(-150%, -50%);
        transition: all 0.5s;
    }

    &:hover {
        background-color: #4cc9f0;
        color: #fff;
        box-shadow: 0 2px 0 2px #0d3b66;
    }

    &:hover::before {
        transform: skewX(30deg) translate(150%, -50%);
        transition-delay: 0.1s;
    }

    &:active {
        transform: scale(0.9);
    }
}
</style>