<template>
    <div class="login-container">
        <div class="panel">
            <div class="panel-header">
                <img src="@/assets/images/logo-icon.png" />
                <div class="header-title">欢迎回到 WeeLink 👋</div>
                <div class="header-desc">登录以继续</div>
            </div>
            <div class="panel-body">
                <t-form
                    ref="form"
                    :data="formData"
                    label-align="top"
                    @submit="onSubmit"
                >
                    <t-form-item label="用户名" name="username">
                        <t-input
                            v-model="formData.username"
                            clearable
                            placeholder="请输入账户名"
                        >
                            <template #prefix-icon>
                                <User1Icon />
                            </template>
                        </t-input>
                    </t-form-item>

                    <t-form-item label="密码" name="password">
                        <t-input
                            v-model="formData.password"
                            type="password"
                            clearable
                            placeholder="请输入密码"
                        >
                            <template #prefix-icon>
                                <LockOnIcon />
                            </template>
                        </t-input>
                    </t-form-item>

                    <t-form-item style="margin-top: 32px">
                        <t-button theme="primary" type="submit" block
                            >登录</t-button
                        >
                    </t-form-item>
                </t-form>
            </div>
        </div>
    </div>
</template>
<script setup>
    import { ref } from 'vue'
    import { useAuthStore } from '@/store/auth'
    import { User1Icon, LockOnIcon } from 'tdesign-icons-vue-next'
    // variables
    const auth = useAuthStore()
    const form = ref(null)
    const formData = ref({})

    // functions
    const onSubmit = async () => {
        try {
            await auth.login(formData.value.username, formData.value.password)
        } catch (err) {
            alert(err)
        }
    }
</script>
<style lang="scss" scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    width: 100vw;
    background-color: #f9fafb;

    .panel {
        width: 375px;
        padding: 48px 48px 16px 48px;
        background-color: #fff;
        box-shadow: 0 1px 3px 0 #0000001a, 0 1px 2px -1px #0000001a;

        .panel-header {
            text-align: center;

            img {
                width: 64px;
                height: 64px;
            }

            .header-title {
                font-size: 24px;
            }

            .header-desc {
                margin-top: 6px;
                font-size: 14px;
                color: #888888;
            }
        }

        .panel-body {
            padding: 32px 0;
        }
    }
}
</style>