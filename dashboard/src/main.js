import "@/assets/css/index.css";
import "tdesign-vue-next/es/style/index.css";

import router from "./router";
import { createApp } from "vue";
import { use } from "echarts/core";
import App from "./App.vue";
import pinia from './store/index.js'
import ECharts from "vue-echarts";
import TDesign from "tdesign-vue-next";

// chart
import { CanvasRenderer } from "echarts/renderers";
import { LineChart, BarChart, PieChart } from "echarts/charts";

import {
    TitleComponent,
    TooltipComponent,
    GridComponent,
    LegendComponent,
    ToolboxComponent,
    DatasetComponent,
} from "echarts/components";

use([
    CanvasRenderer,
    LineChart,
    BarChart,
    PieChart,
    TitleComponent,
    TooltipComponent,
    GridComponent,
    LegendComponent,
    ToolboxComponent,
    DatasetComponent,
]);

const app = createApp(App);
app.use(pinia);
app.use(router);
app.use(TDesign);
app.component("v-chart", ECharts);
app.mount("#app");
