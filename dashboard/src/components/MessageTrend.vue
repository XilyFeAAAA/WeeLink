<!-- MessageTrend.vue -->
<template>
    <v-chart :option="option" autoresize />
</template>

<script setup>
const option = {
    // title: { text: "消息趋势分析" },
    tooltip: { trigger: "axis" },
    xAxis: {
        type: "category",
        data: [
            "6-16 20:23",
            "6-17 01:05",
            "6-17 05:47",
            "6-17 10:29",
            "6-17 15:11",
        ],
    },
    yAxis: {
        type: "value",
        name: "消息数量",
    },
    series: [
        {
            name: "消息数",
            type: "line",
            areaStyle: {},
            data: [1, 2, 0, 5, 1],
        },
    ],
};
</script>
