<template>
    <div class="about-container view">
        <div class="about-header">
            <div class="about-title">
                <div class="title-icon">
                    <InfoCircleFilledIcon size="40"/>
                </div>
                <div>
                    <h1>关于</h1>
                    <p>关于本项目</p>
                </div>
            </div>
        </div>
        <div class="about-body">
            <Markdown :markdown="markdown"></Markdown>
        </div>
    </div>
</template>
<script setup>
import { ref, reactive, onMounted } from "vue";
import { InfoCircleFilledIcon } from "tdesign-icons-vue-next";
import Markdown from '@/components/Markdown.vue'
import request from "@/utils/request";

// variables
const markdown = ref("")

// functions
const loadMarkdown = async () => {
    const response = await fetch(
        'https://raw.githubusercontent.com/XilyFeAAAA/WeeLink/refs/heads/main/README.md'
    )
    markdown.value = await response.text()
}
onMounted(async () => {
    await loadMarkdown()
});
</script>
<style lang="scss" scoped>
.about-header {
    margin-bottom: 24px;
    .about-title {
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

.about-body {
    background-color: #fff;
    padding: 32px 64px;
}
</style>