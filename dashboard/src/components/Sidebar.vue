<template>
    <div class="aside" :class="{ collapsed: isCollapsed }">
        <div class="aside-header">
            <a href="#" class="logo">
                <img 
                    style="height:30px;margin-right:15px"
                    src="@/assets/images/designer-icon-w.svg"
                >
                <span>Nexus</span>
            </a>
            <button class="toggle-btn" @click="onCollapse">
                <ChevronLeftDoubleSIcon size="20"/>
            </button>
        </div>
        <div class="aside-menu">
            <ul>
                <li v-for="(menu, index) in menus" :key=index>
                    <a 
                        @click="onRouting(menu.route)"
                        :class="{ active: isActiveRoute(menu.route) }"
                    >
                        <div class="menu-icon">
                            <component :is="menu.icon" size="20"/>
                        </div>
                        <div class="menu-name">
                            {{ menu.title }}
                        </div>
                    </a>
                </li>
            </ul>
        </div>
        <div class="aside-footer">
            <a href="#" class="team-selector">
                <div class="team-icon">
                    <i class='bx bxs-diamond'></i>
                </div>
                <div class="team-info">
                    <span>Team</span><br>
                    <strong>Marketing</strong>
                </div>
                <i class='bx bx-unfold'></i>
            </a>
            <button class="upgrade-btn">Upgrade Plan</button>
            <p class="copyright">&copy; 2023 Nexus.io, Inc.</p>
        </div>
    </div>
</template>
<script setup>
    import { ref } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
    import { 
        ChevronLeftDoubleSIcon,
        Dashboard1FilledIcon,
        ChatMessageFilledIcon,
        ExtensionFilledIcon,
        Functions1Icon,
        LayersFilledIcon,
        StoreFilledIcon,
        SystemSettingFilledIcon,
        TerminalRectangleFilledIcon,
        DataBaseFilledIcon,
        InfoCircleFilledIcon
    } from "tdesign-icons-vue-next"

    // variables
    const route = useRoute()
    const router = useRouter()
    const menus = ref([
        {
            title: "仪表盘",
            icon: Dashboard1FilledIcon,
            route: "/dashboard"
        },
        {
            title: "会话",
            icon: ChatMessageFilledIcon,
            route: "/chat"
        },
        {
            title: "适配器",
            icon: LayersFilledIcon,
            route: "/adapter"
        },
        {
            title: "数据库",
            icon: DataBaseFilledIcon,
            route: "/database"
        },
        {
            title: "MCP",
            icon: Functions1Icon,
            route: "/mcp"
        },
        {
            title: "插件管理",
            icon: ExtensionFilledIcon,
            route: "/plugin"
        },
        {
            title: "插件平台",
            icon: StoreFilledIcon,
            route: "/store"
        },
        {
            title: "配置文件",
            icon: SystemSettingFilledIcon,
            route: "/config"
        },
        {
            title: "终端",
            icon: TerminalRectangleFilledIcon,
            route: "/terminal"
        },
        {
            title: "关于",
            icon: InfoCircleFilledIcon,
            route: "/about"
        }
    ])
    const isCollapsed = ref(false)

    // functions
    const onRouting = (menuRoute) => {
        console.log(menuRoute)
        router.replace(menuRoute)
    }
    const onCollapse = () => {
        isCollapsed.value = !isCollapsed.value
    }
    const isActiveRoute = (menuRoute) => {
        if (route.path === menuRoute) return true
        if (route.path.startsWith(menuRoute + '/')) return true
        return false
    }

</script>
<style lang="scss" scoped>
    .aside {
        display: flex;
        flex-direction: column;
        height: 100vh;
        width: var(--sidebar-width);
        background-color: var(--sidebar-bg);
        transition: all 0.3s ease-in-out;
        user-select: none;
        .aside-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 24px;
            height: var(--header-height);
            border-bottom: 1px solid var(--border-color);
            
            .logo {
                display: flex;
                align-items: center;
                text-decoration: none;
                color: var(--accent-color);
                font-weight: 500;
                font-size: 28px;
            }

            .toggle-btn {
                background: none;
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 4px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--secondary-text);
            }

        }

        .aside-menu {
            padding: 8px 16px;
            flex-grow: 1;
            flex-grow: 1;
            overflow-y: auto;

            ul {
                list-style: none;

                li {
                    margin: 5px 0;
                    border-radius: 10px;
                    a {
                        display: flex;
                        justify-content: flex-start;
                        padding: 10px 12px;
                        border-radius: 8px;
                        text-decoration: none;
                        transition: background-color 0.2s, color 0.2s;
                        line-height: 1;
                        vertical-align: middle;
                        cursor: pointer;
                        
                        .menu-icon {
                            color: #7A7A7A;
                            transition: 0.4s ease-in-out color;
                        }

                        .menu-name {
                            flex: 1;
                            display: flex;
                            align-items: center;
                            margin-left: 25px;
                            white-space: nowrap;
                            overflow: hidden;
                            text-overflow: ellipsis;
                            color: rgba(0, 0, 0, 0.87);
                            font-size: 14px;
                        }

                        &:hover {
                        background-color: var(--btn-hover-color);
                    }

                        &.active {
                            background-color: var(--btn-active-color);
                            color: var(--primary-text);
                        }
                    }

                    
                }
            }
        
            
        }
        
        .aside-footer {
            padding: 24px;
            margin-top: auto;

            .team-selector {
                display: flex;
                align-items: center;
                background-color: var(--bg-color);
                border-radius: var(--border-radius);
                padding: 12px;
                text-decoration: none;
                color: var(--primary-text);
            }

            .team-icon {
                width: 40px;
                height: 40px;
                border-radius: 8px;
                background-color: #17D8A7;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                margin-right: 12px;
            }
            .team-info { line-height: 1.2; }
            .team-info span { 
                font-size: 12px; 
                color: var(--secondary-text); 
            }
            .team-selector i.bx-unfold { 
                margin-left: auto; 
                color: var(--secondary-text); 
            }

            .upgrade-btn {
                width: 100%;
                padding: 10px 0;
                margin-top: 16px;
                border: 1px solid var(--border-color);
                background-color: white;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
            }

            .copyright {
                font-size: 12px;
                color: var(--secondary-text);
                text-align: center;
                margin-top: 20px;
            }
        }

        &.collapsed {
            width: 80px;

            .logo,
            .menu-name,
            .team-info,
            .team-selector,
            .upgrade-btn,
            .copyright {
                display: none !important;
                opacity: 0 !important;
            }

            li {
                margin:  0;

                a {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 0px;

                    .menu-icon {
                        color: #000 !important;
                    }
                }
            }

            .team-selector {
                justify-content: center;
            }

            .toggle-btn i {
                transform: rotate(180deg);
            }
        }
    }
</style>