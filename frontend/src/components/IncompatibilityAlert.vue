<template>
  <el-dialog
    v-model="visible"
    title="⚠️ 配伍禁忌警告"
    width="520px"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <div class="incompatibility-alert">
      <el-alert
        type="error"
        :closable="false"
        show-icon
        title="检测到配伍禁忌冲突"
        style="margin-bottom:16px;"
      />

      <div class="warning-list">
        <div v-for="(w, idx) in warnings" :key="idx" class="warning-item">
          <div class="warning-header">
            <el-tag type="danger" size="small">{{ w.rule_type }}</el-tag>
            <span class="warning-herbs">{{ w.herb_a }} + {{ w.herb_b }}</span>
          </div>
          <div v-if="w.description" class="warning-desc">{{ w.description }}</div>
        </div>
      </div>

      <div v-if="pregnancyWarnings.length > 0" class="pregnancy-section">
        <el-alert type="warning" :closable="false" show-icon title="孕妇禁忌提醒" style="margin-bottom:8px;" />
        <div v-for="(pw, idx) in pregnancyWarnings" :key="idx" class="warning-item">
          <el-tag type="warning" size="small">孕妇慎用</el-tag>
          <span class="warning-herbs">{{ pw }}</span>
        </div>
      </div>

      <div v-if="dosageWarnings.length > 0" class="dosage-section">
        <el-alert type="warning" :closable="false" show-icon title="剂量超限提醒" style="margin-bottom:8px;" />
        <div v-for="(dw, idx) in dosageWarnings" :key="idx" class="warning-item">
          <el-tag type="warning" size="small">超量</el-tag>
          <span class="warning-herbs">{{ dw }}</span>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="onCancel">返回修改</el-button>
      <el-button v-if="allowForce" type="danger" @click="onForceConfirm">
        我已知晓风险，继续
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  modelValue: boolean
  warnings: Array<{ herb_a: string; herb_b: string; rule_type: string; description?: string | null }>
  pregnancyWarnings?: string[]
  dosageWarnings?: string[]
  allowForce?: boolean  // 是否允许强制继续（配伍禁忌不允许，剂量警告可允许）
}>(), {
  pregnancyWarnings: () => [],
  dosageWarnings: () => [],
  allowForce: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void
  (e: 'cancel'): void
  (e: 'force-confirm'): void
}>()

const visible = ref(props.modelValue)

watch(() => props.modelValue, (val) => { visible.value = val })
watch(visible, (val) => { emit('update:modelValue', val) })

function onCancel() {
  visible.value = false
  emit('cancel')
}

function onForceConfirm() {
  visible.value = false
  emit('force-confirm')
}
</script>

<style scoped lang="scss">
.incompatibility-alert {
  .warning-list, .pregnancy-section, .dosage-section {
    margin-top: 8px;
  }

  .warning-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 12px;
    background: #fef0f0;
    border-radius: 6px;
    margin-bottom: 8px;

    .warning-header {
      display: flex;
      align-items: center;
      gap: 8px;
      width: 100%;
    }

    .warning-herbs {
      font-weight: 600;
      color: #c45656;
      font-size: 14px;
    }

    .warning-desc {
      font-size: 12px;
      color: #999;
      margin-top: 4px;
    }
  }
}
</style>
