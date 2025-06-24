<template>
    <div class="header-container">
        <div class="search-bar">
            <SearchIcon />
            <input type="text" placeholder="Search" />
            <span class="shortcut">⌘ + F</span>
        </div>
        <div class="tool-bar">
            <div class="tools">
                <t-button theme="default" variant="text">
                    <LogoGithubFilledIcon size="20" />
                </t-button>
                <t-button theme="default" variant="text">
                    <Download2FilledIcon size="20" />
                </t-button>
                <t-button theme="default" variant="text" @click="onRestart">
                    <RocketFilledIcon size="20" />
                </t-button>
            </div>
            <div class="divider"></div>
            <t-dropdown
                :options="options"
                trigger="click"
                :minColumnWidth="150"
            >
                <div class="profile">
                    <div class="user-img">
                        <img src="@/assets/images/avatar.png" alt="" />
                    </div>
                    <div class="user-info">
                        <div class="username">XilyFeAAAA</div>
                        <div class="expire">2025.10.26</div>
                    </div>
                </div>
            </t-dropdown>
        </div>
    </div>
    <t-dialog
        :visible="visibleModal"
        :closeBtn="false"
        mode="modal"
        :on-confirm="() => onConfirm()"
    >
        <template #body>
            <div class="reset-container">
                <div class="reset-header">
                    <img src="@/assets/images/logo-icon.png" />
                    <div class="reset-info">
                        <div class="reset-title">WeeLink</div>
                        <div class="reset-desc">修改账户</div>
                    </div>
                </div>
                <div class="reset-body">
                    <t-form
                        ref="formRef"
                        :data="formData"
                        :label-width="0"
                        @submit="onSubmit"
                    >
                        <t-form-item name="account">
                            <t-input
                                v-model="formData.current_pwd"
                                type="password"
                                size="large"
                                placeholder="当前密码"
                            >
                                <template #prefix-icon>
                                    <LockOnIcon />
                                </template>
                            </t-input>
                        </t-form-item>

                        <t-form-item name="password">
                            <t-input
                                v-model="formData.new_pwd"
                                type="password"
                                size="large"
                                placeholder="新密码"
                            >
                                <template #prefix-icon>
                                    <RotateLockedIcon />
                                </template>
                            </t-input>
                        </t-form-item>
                        <div class="tip">密码长度至少 8 位</div>
                    </t-form>
                </div>
            </div>
        </template>
    </t-dialog>
</template>
<script setup>
import { ref } from "vue";
import { useAuthStore } from "@/store/auth";
import {
    SearchIcon,
    LogoGithubFilledIcon,
    Download2FilledIcon,
    LockOnIcon,
    RocketFilledIcon,
    RotateLockedIcon,
} from "tdesign-icons-vue-next";
import { LoadingPlugin } from "tdesign-vue-next";
import request from "@/utils/request";

// variables
const formRef = ref(null);
const authStore = useAuthStore();
const formData = ref({});
const visibleModal = ref(false);
const options = [
    {
        content: "修改密码",
        value: 1,
        onClick: () => {
            visibleModal.value = !visibleModal.value;
        },
    },
    {
        content: "退出账户",
        value: 2,
        onClick: () => authStore.logout(),
    },
];

// functions

const onRestart = async () => {
    LoadingPlugin(true);
    try{
        await request.post("/system/restart")
    }finally{
        LoadingPlugin(false);
    }
};
const onSubmit = async () => {
    await request.post("/auth/reset-pwd", {
        current_password: formData.value.current_pwd,
        new_password: formData.value.new_pwd,
    });
};
const onConfirm = () => {
    if (formRef.value) {
        formRef.value.submit();
    }
    visibleModal.value = !visibleModal.value;
};
</script>
<style lang="scss" scoped>
.header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 16px;
    height: 100%;
    width: 100%;

    .search-bar {
        display: flex;
        align-items: center;
        background-color: white;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 8px 16px;
        width: 320px;

        i {
            color: var(--secondary-text);
            font-size: 20px;
        }

        input {
            border: none;
            outline: none;
            margin-left: 12px;
            font-size: 14px;
            flex-grow: 1;
            background: transparent;
        }

        .shortcut {
            color: var(--primary-text);
            font-size: 14px;
        }
    }

    .tool-bar {
        display: flex;
        align-items: center;
        .tools {
            display: flex;
            align-items: center;

            .icon-button {
                display: flex;
                align-items: center;
            }
        }
        .divider {
            margin: 0 6px;
            width: 1px;
            height: 30px;
            background-color: rgba(0, 0, 0, 0.2);
        }
        .profile {
            display: flex;
            align-items: center;
            padding: 2px 16px;
            border-radius: 6px;
            cursor: pointer;
            transition: 0.2s ease-in-out;
            &:hover {
                background-color: #f4f6f8;
            }
            .user-img {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 40px;
                width: 40px;
                background-color: #f4f6f8;
                border-radius: 50%;
                overflow: hidden;

                img {
                    widows: 70%;
                    height: 70%;
                }
            }

            .user-info {
                margin-left: 12px;
                .username {
                    font-size: 14px;
                }
                .expire {
                    font-size: 12px;
                    color: var(--tertiary-text);
                }
            }
        }
    }
}
.reset-container {
    .reset-header {
        display: flex;
        justify-content: center;
        align-items: center;
        img {
            height: 100px;
            width: 100px;
        }
        .reset-info {
            margin-left: 5px;
            .reset-title {
                font-size: 32px;
                font-weight: 600;
                color: #181818;
            }
            .reset-desc {
                margin-top: 12px;
                font-size: 15px;
                color: #000000aa;
            }
        }
    }
    .reset-body {
        margin-top: 32px;
    }
}
.tip {
    padding-left: 16px;
    font-size: 12px;
    color: rgba(0, 0, 0, 0.57);
}
</style>