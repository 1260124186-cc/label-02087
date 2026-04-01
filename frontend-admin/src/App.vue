<template>
  <header class="app-header">
    <router-link to="/" class="logo">
      <el-icon><Monitor /></el-icon>
      <span>NetDoctor</span>
    </router-link>
  </header>
  <main class="app-main">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </main>
</template>

<script setup>
import { Monitor } from '@element-plus/icons-vue'
</script>

<style scoped>
/* 页面切换过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
