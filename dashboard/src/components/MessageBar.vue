<template>
    <v-chart :option="option" autoresize />
</template>

<script setup>
const option = {
    title: { text: "每周订阅增长" },
    tooltip: {},
    xAxis: {
        type: "category",
        data: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    },
    yAxis: { type: "value" },
    series: [
        {
            type: "bar",
            data: [1200, 1800, 3874, 950, 2300, 1600, 2900],
            itemStyle: {
                color: (params) =>
                    params.dataIndex === 2 ? "#8B5CF6" : "#CBD5E1",
            },
        },
    ],
};
</script>
