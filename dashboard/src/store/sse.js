import { defineStore } from 'pinia'
import { MessagePlugin } from 'tdesign-vue-next';


export const useSSEStore = defineStore('sse', {
    state: () => ({
        token: localStorage.getItem('token') || '',
        logs: [],
        isConnected: false,
        abortContrroller: null
    }),

    actions: {
        async connectSSE() {
            try {
                this.abortController = new AbortController()
                const response = await fetch('http://0.0.0.0:7070/api/stream', {
                    method: 'GET',
                    headers: {
                        'Accept': 'text/event-stream',
                        'Cache-Control': 'no-cache',
                        'Authorization': `Bearer ${this.token}`,
                        'Content-Type': 'text/plain'
                    },
                    signal: this.abortController.signal
                })

                if (!response.ok) {
                    throw new Error(`网络连接出错! 状态码: ${response.status}`)
                }

                this.isConnected = true
                const reader = response.body.getReader()
                const decoder = new TextDecoder()
                let buffer = ""


                while (true) {
                    const { done, value } = await reader.read()
                    if (done) break

                    buffer += decoder.decode(value, { stream: true })


                    let parts = buffer.split("\n\n")
                    buffer = parts.pop();

                    for (let chunk of parts) {
                        let eventType = "";
                        let dataStr = "";
                        const lines = chunk.split("\n")
                        for (let line of lines) {
                            if (line.startsWith("event:")) {
                                eventType = line.slice(6).trim();
                            } else if (line.startsWith("data:")) {
                                dataStr += line.slice(5).trim();
                            }
                        }
                        let payload;
                        try {
                            payload = JSON.parse(dataStr);
                        } catch (e) {
                            payload = dataStr;  // 如果不是 JSON，就当作纯文本
                        }

                        switch (eventType) {
                            case "heartbeat":
                                console.log("[HEARTBEAT]", payload);
                                break;
                            case "log":
                                this.logs.push(payload)
                                break;
                            case "error":
                                MessagePlugin.error(payload.message);
                                break;
                            case "connected":
                                console.log("[CONNECTED]", payload.message);
                                break;
                            case "disconnected":
                                console.log("[DISCONNECTED]", payload.message);
                                controller.abort();
                                break;
                            default:
                                console.warn("[UNKNOWN EVENT]", eventType, payload);
                        }
                    }
                }
            } catch (err) {
                if (err.name === 'AbortError') {
                    console.log('SSE流连接终止')
                } else {
                    console.error('SSE流错误:', err)
                }
            } finally {
                this.isConnected = false
            }
        },
        disconnectSSE() {
            if (this.abortController) {
                this.abortController.abort()
                this.abortController = null
            }
        },
        reconnectSSE() {
            disconnectSSE()
            setTimeout(() => {
                connectSSE()
            }, 1000)
        }
    }
})
