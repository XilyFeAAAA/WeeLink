import axios from "axios";
import { useAuthStore } from "@/store/auth";

const request = axios.create({
    baseURL: "http://0.0.0.0:7070/api",
    timeout: 7070,
});

// 请求拦截器
request.interceptors.request.use((config) => {
    const auth = useAuthStore();
    if (auth.token) {
        config.headers.Authorization = `Bearer ${auth.token}`;
    }
    return config;
});

export default request;
