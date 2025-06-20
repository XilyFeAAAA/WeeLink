<template>
    <div class="markdown-body" v-html="renderedHtml"></div>
</template>
<script setup>
import { computed } from "vue";
import { marked } from "marked";
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';

const props = defineProps({
    markdown: {
        type: String,
        required: true,
    },
});

const renderedHtml = computed(() => {
    if (!props.markdown) return "";

    // 配置marked使用highlight.js进行语法高亮
    marked.setOptions({
        highlight: function (code, lang) {
            if (lang && hljs.getLanguage(lang)) {
                try {
                    return hljs.highlight(code, { language: lang }).value;
                } catch (e) {
                    console.error(e);
                }
            }
            return hljs.highlightAuto(code).value;
        },
        gfm: true, 
        breaks: true,
        headerIds: true,
        mangle: false,
    });

    return marked(props.markdown);
});
</script>
<style lang="scss">
.markdown-body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.5;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
    line-height: 1.25;
}

.markdown-body h1 {
    font-size: 2em;
    border-bottom: 1px solid rgba(208, 208, 208);
    padding-bottom: 0.3em;
}

.markdown-body h2 {
    font-size: 1.5em;
    border-bottom: 1px solid rgba(208, 208, 208);
    padding-bottom: 0.3em;
}

.markdown-body p {
    margin-top: 0;
    margin-bottom: 16px;
}

.markdown-body code {
    padding: 0.2em 0.4em;
    margin: 0;
    background-color: rgba(245, 240, 255);
    border-radius: 3px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 85%;
}

.markdown-body pre {
    padding: 16px;
    overflow: auto;
    font-size: 85%;
    line-height: 1.45;
    background-color: rgba(238, 242, 246);
    border-radius: 3px;
    margin-bottom: 16px;
}

.markdown-body pre code {
    background-color: transparent;
    padding: 0;
}

.markdown-body ul,
.markdown-body ol {
    padding-left: 2em;
    margin-bottom: 16px;
}


.markdown-body img {
    max-width: 100%;
    margin: 8px 0;
    box-sizing: border-box;
    background-color: rgba(249,250,252);
    border-radius: 3px;
}

.markdown-body blockquote {
    padding: 0 1em;
    border-left: 0.25em solid rgba(208, 208, 208);
    margin-bottom: 16px;
}

.markdown-body a {
    color: rgba(30,136,229);
    text-decoration: none;
}

.markdown-body a:hover {
    text-decoration: underline;
}

.markdown-body table {
    border-spacing: 0;
    border-collapse: collapse;
    width: 100%;
    overflow: auto;
    margin-bottom: 16px;
}

.markdown-body table th,
.markdown-body table td {
    padding: 6px 13px;
    border: 1px solid rgba(249,250,252);
}

.markdown-body table tr {
    background-color: var(--v-theme-surface);
    border-top: 1px solid rgba(208, 208, 208);
}

.markdown-body table tr:nth-child(2n) {
    background-color: rgba(249,250,252);
}

.markdown-body hr {
    height: 0.25em;
    padding: 0;
    margin: 24px 0;
    background-color: rgba(238, 242, 246);
    border: 0;
}
</style>