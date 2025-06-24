<template>
    <div class="layout-container">
        <nav class="sidebar">
            <SideBarComponent />
        </nav>
        <main>
            <div class="main-header">
                <HeaderComponent />
            </div>
            <div class="main-view">
                <router-view />
            </div>
        </main>
    </div>
</template>
<script setup>
import SideBarComponent from "@/components/Sidebar.vue";
import HeaderComponent from "@/components/Header.vue";


// functions
const onStickTool = (context) => {
    const label = context.item.label;
    if (label === "scan") {
        visibleModal.value = true;
    } else {
        window.open("https://github.com/XilyFeAAAA/WeeLink", "_blank");
    }
};
</script>
<style lang="scss" scoped>
.layout-container {
    display: flex;
    height: 100vh;
    width: 100vw;

    .sidebar {
        border-right: 1px solid var(--border-color);
        z-index: 100;
    }

    main {
        flex: 1;
        display: flex;
        flex-direction: column;

        .main-header {
            height: var(--header-height);
            width: 100%;
            border-bottom: 1px solid var(--border-color);
            z-index: 100;
            box-shadow: 0 4px 6px -4px rgba(0, 0, 0, 0.1);
        }

        .main-view {
            flex: 1;

            overflow: hidden;
        }
    }
}

.qrcode-container {
    padding: 12px 0;
}
</style>