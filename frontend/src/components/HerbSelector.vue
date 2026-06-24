<template>
  <div class="herb-selector">
    <el-select
      v-model="selectedHerbId"
      filterable
      remote
      :remote-method="searchHerbs"
      :loading="searchLoading"
      placeholder="输入药名或异名搜索"
      :style="{ width: fullWidth ? '100%' : (width || '220px') }"
      @change="onSelect"
      clearable
      :disabled="disabled"
    >
      <el-option
        v-for="h in filteredHerbs"
        :key="h.id"
        :label="h.name"
        :value="h.id"
      >
        <div style="display:flex;justify-content:space-between;align-items:center;width:100%;">
          <span>
            <span style="font-weight:600;">{{ h.name }}</span>
            <span v-if="h.aliases?.length" style="color:#999;font-size:12px;margin-left:4px;">
              ({{ h.aliases.join('、') }})
            </span>
          </span>
          <span style="font-size:12px;color:#8B4513;">
            {{ h.dosage_min }}~{{ h.dosage_max }}g
          </span>
        </div>
      </el-option>
    </el-select>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/utils/api'

const props = withDefaults(defineProps<{
  modelValue?: number | null
  disabled?: boolean
  fullWidth?: boolean
  width?: string
  excludeIds?: number[]  // 已选药材ID，排除已选项
}>(), {
  modelValue: null,
  disabled: false,
  fullWidth: false,
  width: '220px',
  excludeIds: () => [],
})

const emit = defineEmits<{
  (e: 'update:modelValue', val: number | null): void
  (e: 'select', herb: any): void
}>()

const selectedHerbId = ref<number | null>(props.modelValue)
const allHerbs = ref<any[]>([])
const filteredHerbs = ref<any[]>([])
const searchLoading = ref(false)

async function loadAllHerbs() {
  try {
    allHerbs.value = (await api.get('/herbs') as any) || []
    filteredHerbs.value = allHerbs.value.filter((h: any) => !props.excludeIds.includes(h.id))
  } catch {}
}

function searchHerbs(query: string) {
  if (!query) {
    filteredHerbs.value = allHerbs.value.filter((h: any) => !props.excludeIds.includes(h.id))
    return
  }
  const q = query.toLowerCase()
  filteredHerbs.value = allHerbs.value.filter((h: any) => {
    if (props.excludeIds.includes(h.id)) return false
    // 搜索正名
    if (h.name.toLowerCase().includes(q)) return true
    // 搜索异名
    if (h.aliases?.some((a: string) => a.toLowerCase().includes(q))) return true
    // 搜索功效
    if (h.efficacy?.toLowerCase().includes(q)) return true
    // 搜索分类
    if (h.category?.toLowerCase().includes(q)) return true
    return false
  })
}

function onSelect(herbId: number | null) {
  emit('update:modelValue', herbId)
  if (herbId) {
    const herb = allHerbs.value.find((h: any) => h.id === herbId)
    emit('select', herb || null)
  } else {
    emit('select', null)
  }
}

// 监听外部 excludeIds 变化
import { watch } from 'vue'
watch(() => props.excludeIds, () => {
  filteredHerbs.value = allHerbs.value.filter((h: any) => !props.excludeIds.includes(h.id))
}, { deep: true })

watch(() => props.modelValue, (val) => {
  selectedHerbId.value = val
})

onMounted(loadAllHerbs)
</script>
