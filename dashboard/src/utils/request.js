import axios from "axios";
import { NotifyPlugin } from 'tdesign-vue-next';
import { useAuthStore } from "@/store/auth";

const request = axios.create({
    baseURL: "http://127.0.0.1:7070/api"
});

// 请求拦截器
request.interceptors.request.use((config) => {
    const auth = useAuthStore();
    if (auth.token) {
        config.headers.Authorization = `Bearer ${auth.token}`;
    }
    return config;
});

// 响应拦截器
request.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        // 错误处理
        let message = "请求失败";
        
        if (error.response) {
            // 服务器返回了错误状态码
            const status = error.response.status;
            switch (status) {
                case 400:
                    message = "请求参数错误";
                    break;
                case 401:
                    message = "未授权，请重新登录";
                    break;
                case 403:
                    message = "拒绝访问";
                    break;
                case 404:
                    message = "请求的资源不存在";
                    break;
                case 500:
                    message = "服务器内部错误";
                    break;
                default:
                    message = `请求错误(${status})`;
            }
        } else if (error.request) {
            message = "网络异常，服务器未响应";
        } else {
            message = error.message;
        }
        
        NotifyPlugin('error', { title: '系统错误', message })
        
        return Promise.reject(error);
    }
);

export default request;
