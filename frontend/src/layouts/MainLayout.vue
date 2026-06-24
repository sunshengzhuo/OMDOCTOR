<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapsed ? '64px' : '210px'" class="sidebar">
      <div class="sidebar-logo" @click="$router.push('/dashboard')">
        <span class="logo-icon">🌿</span>
        <span v-show="!isCollapsed" class="logo-text">中医诊所管理</span>
      </div>

      <el-menu
        :default-active="currentRoute"
        :collapse="isCollapsed"
        :collapse-transition="false"
        background-color="#2C1810"
        text-color="#E8D5C4"
        active-text-color="#D4A574"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>
        <el-menu-item index="/statistics">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>统计报表</template>
        </el-menu-item>

        <el-sub-menu index="patient-group">
          <template #title>
            <el-icon><User /></el-icon>
            <span>病号管理</span>
          </template>
          <el-menu-item index="/patients">患者列表</el-menu-item>
          <el-menu-item index="/constitution">体质辨识</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="herb-group">
          <template #title>
            <el-icon><FirstAidKit /></el-icon>
            <span>药品管理</span>
          </template>
          <el-menu-item index="/herbs">药材字典</el-menu-item>
          <el-menu-item index="/herbs/inventory">库存管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="prescription-group">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>处方管理</span>
          </template>
          <el-menu-item index="/prescriptions">处方列表</el-menu-item>
          <el-menu-item index="/classic-formulas">经典方库</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/knowledge">
          <el-icon><Search /></el-icon>
          <template #title>知识检索</template>
        </el-menu-item>

        <el-menu-item index="/book-library">
          <el-icon><Reading /></el-icon>
          <template #title>医籍文库</template>
        </el-menu-item>

        <el-menu-item index="/diagnosis">
          <el-icon><ChatDotRound /></el-icon>
          <template #title>智能问诊</template>
        </el-menu-item>

        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-toggle" @click="isCollapsed = !isCollapsed">
        <el-icon :size="16">
          <Fold v-if="!isCollapsed" />
          <Expand v-else />
        </el-icon>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="main-container">
      <el-header class="main-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentPageTitle">{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tag type="info" size="small">v0.1.0</el-tag>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  HomeFilled, User, FirstAidKit, Document, Search,
  ChatDotRound, Setting, Fold, Expand, TrendCharts, Box, Notebook, DataAnalysis, Reading,
} from '@element-plus/icons-vue'

const route = useRoute()
const isCollapsed = ref(false)

const currentRoute = computed(() => route.path)
const currentPageTitle = computed(() => (route.meta.title as string) || '')
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
}

.sidebar {
  background-color: #2C1810;
  overflow-y: auto;
  overflow-x: hidden;
  transition: width 0.2s;
  display: flex;
  flex-direction: column;

  .sidebar-logo {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 16px 8px;
    cursor: pointer;
    border-bottom: 1px solid rgba(232, 213, 196, 0.1);

    .logo-icon {
      font-size: 28px;
    }

    .logo-text {
      color: #E8D5C4;
      font-size: 16px;
      font-weight: 600;
      margin-left: 8px;
      white-space: nowrap;
    }
  }

  .el-menu {
    border-right: none;
    flex: 1;
  }

  .sidebar-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 12px;
    cursor: pointer;
    color: #E8D5C4;
    border-top: 1px solid rgba(232, 213, 196, 0.1);

    &:hover {
      color: #D4A574;
    }
  }
}

.main-container {
  background-color: #F5F0EB;
}

.main-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e8e0d8;
  padding: 0 20px;
  height: 48px;
}

.main-content {
  padding: 20px;
  overflow-y: auto;
}
</style>
