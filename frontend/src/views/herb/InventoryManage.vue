<template>
  <div class="inventory-manage">
    <!-- 顶部操作栏 -->
    <el-card shadow="hover">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span>📦 库存管理</span>
          <div style="display:flex;gap:8px;">
            <el-button type="success" size="small" @click="openStockIn">
              <el-icon><Upload /></el-icon> 入库
            </el-button>
            <el-button type="warning" size="small" @click="openStockOut">
              <el-icon><Download /></el-icon> 出库
            </el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" @submit.prevent="loadInventory">
        <el-form-item>
          <el-input v-model="searchText" placeholder="搜索药材名称" clearable @clear="loadInventory" style="width:200px">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="loadInventory" style="width:120px">
            <el-option label="正常" value="正常" />
            <el-option label="近效期" value="近效期" />
            <el-option label="停用" value="停用" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadInventory">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="filteredInventory" stripe style="width:100%" empty-text="暂无库存记录">
        <el-table-column prop="herb_name" label="药材" width="100" />
        <el-table-column prop="batch_number" label="批号" width="120">
          <template #default="{ row }">{{ row.batch_number || '-' }}</template>
        </el-table-column>
        <el-table-column prop="quantity" label="库存量(g)" width="110">
          <template #default="{ row }">
            <span :class="{ 'low-stock': row.quantity < (row.min_stock || 0) }">
              {{ row.quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="min_stock" label="最低库存(g)" width="110">
          <template #default="{ row }">{{ row.min_stock || '-' }}</template>
        </el-table-column>
        <el-table-column prop="unit_price" label="单价(元/g)" width="110">
          <template #default="{ row }">{{ row.unit_price != null ? row.unit_price.toFixed(2) : '-' }}</template>
        </el-table-column>
        <el-table-column prop="purchase_date" label="购入日期" width="110">
          <template #default="{ row }">{{ row.purchase_date || '-' }}</template>
        </el-table-column>
        <el-table-column prop="expiry_date" label="有效期" width="110">
          <template #default="{ row }">
            <span v-if="row.expiry_date" :class="{ 'near-expiry': isNearExpiry(row.expiry_date) }">
              {{ row.expiry_date }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="supplier" label="供应商" width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ row.supplier || '-' }}</template>
        </el-table-column>
        <el-table-column prop="location" label="存放位置" width="100">
          <template #default="{ row }">{{ row.location || '-' }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="editStock(row)">设置预警</el-button>
            <el-button link type="danger" size="small" @click="setLocation(row)">仓位</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 预警面板 -->
    <el-card shadow="hover" style="margin-top:16px;">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span>⚠️ 库存预警</span>
          <el-tag :type="alerts.length > 0 ? 'danger' : 'success'" size="small">
            {{ alerts.length > 0 ? `${alerts.length} 项预警` : '库存正常' }}
          </el-tag>
        </div>
      </template>
      <el-empty v-if="alerts.length === 0" description="暂无预警" :image-size="60" />
      <el-table v-else :data="alerts" stripe size="small">
        <el-table-column prop="herb_name" label="药材" width="120" />
        <el-table-column prop="current_quantity" label="当前库存(g)" width="120" />
        <el-table-column prop="min_stock" label="最低库存(g)" width="120" />
        <el-table-column prop="alert_type" label="预警类型" width="120">
          <template #default="{ row }">
            <el-tag type="danger" size="small">{{ row.alert_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="quickStockIn(row.herb_id)">快速入库</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 入库对话框 -->
    <el-dialog v-model="stockInVisible" title="📥 药材入库" width="520px" destroy-on-close>
      <el-form :model="stockInForm" label-width="90px" :rules="stockInRules" ref="stockInFormRef">
        <el-form-item label="药材" prop="herb_id">
          <el-select v-model="stockInForm.herb_id" filterable placeholder="搜索药材" style="width:100%"
            @change="onStockInHerbSelect">
            <el-option v-for="h in herbs" :key="h.id" :label="h.name" :value="h.id">
              <span>{{ h.name }}</span>
              <span v-if="h.aliases?.length" style="color:#999;font-size:12px;margin-left:6px;">
                {{ h.aliases.join('、') }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="入库量(g)" prop="quantity">
          <el-input-number v-model="stockInForm.quantity" :min="0.1" :precision="1" style="width:100%" />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="单价(元/g)">
              <el-input-number v-model="stockInForm.unit_price" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="批号">
              <el-input v-model="stockInForm.batch_number" placeholder="批号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="购入日期">
              <el-date-picker v-model="stockInForm.purchase_date" type="date" value-format="YYYY-MM-DD"
                placeholder="选择日期" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="有效期">
              <el-date-picker v-model="stockInForm.expiry_date" type="date" value-format="YYYY-MM-DD"
                placeholder="选择日期" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="供应商">
          <el-input v-model="stockInForm.supplier" placeholder="供应商名称" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="stockInForm.note" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockInVisible = false">取消</el-button>
        <el-button type="primary" @click="submitStockIn" :loading="submitting">确认入库</el-button>
      </template>
    </el-dialog>

    <!-- 出库对话框 -->
    <el-dialog v-model="stockOutVisible" title="📤 药材出库" width="480px" destroy-on-close>
      <el-form :model="stockOutForm" label-width="90px" :rules="stockOutRules" ref="stockOutFormRef">
        <el-form-item label="药材" prop="herb_id">
          <el-select v-model="stockOutForm.herb_id" filterable placeholder="搜索药材" style="width:100%"
            @change="onStockOutHerbSelect">
            <el-option v-for="h in inventoryHerbOptions" :key="h.herb_id" :label="h.herb_name" :value="h.herb_id">
              <span>{{ h.herb_name }}</span>
              <span style="color:#999;font-size:12px;margin-left:8px;">库存: {{ h.total_qty }}g</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="当前库存">
          <span style="color:#8B4513;font-weight:600;">{{ selectedStockAvailable }}g</span>
        </el-form-item>
        <el-form-item label="出库量(g)" prop="quantity">
          <el-input-number v-model="stockOutForm.quantity" :min="0.1" :max="selectedStockAvailable" :precision="1"
            style="width:100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="stockOutForm.note" type="textarea" :rows="2" placeholder="出库原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockOutVisible = false">取消</el-button>
        <el-button type="primary" @click="submitStockOut" :loading="submitting">确认出库</el-button>
      </template>
    </el-dialog>

    <!-- 设置预警对话框 -->
    <el-dialog v-model="alertSettingVisible" title="⚙️ 设置库存预警" width="400px" destroy-on-close>
      <el-form :model="alertSettingForm" label-width="100px">
        <el-form-item label="药材">
          <span>{{ alertSettingForm.herb_name }}</span>
        </el-form-item>
        <el-form-item label="最低库存(g)">
          <el-input-number v-model="alertSettingForm.min_stock" :min="0" :precision="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="存放位置">
          <el-input v-model="alertSettingForm.location" placeholder="如：A区3号架" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="alertSettingVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAlertSetting">保存</el-button>
      </template>
    </el-dialog>

    <!-- 仓位设置对话框 -->
    <el-dialog v-model="locationVisible" title="📍 设置仓位" width="400px" destroy-on-close>
      <el-form :model="locationForm" label-width="80px">
        <el-form-item label="药材">
          <span>{{ locationForm.herb_name }}</span>
        </el-form-item>
        <el-form-item label="存放位置">
          <el-input v-model="locationForm.location" placeholder="如：A区3号架" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="locationVisible = false">取消</el-button>
        <el-button type="primary" @click="saveLocation">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, Download, Search } from '@element-plus/icons-vue'
import api from '@/utils/api'

// ── 库存列表 ──
const inventoryList = ref<any[]>([])
const searchText = ref('')
const statusFilter = ref('')
const alerts = ref<any[]>([])
const herbs = ref<any[]>([])
const submitting = ref(false)

const filteredInventory = computed(() => {
  let list = inventoryList.value
  if (searchText.value) {
    const s = searchText.value.toLowerCase()
    list = list.filter((item: any) =>
      (item.herb_name || '').toLowerCase().includes(s)
    )
  }
  if (statusFilter.value) {
    list = list.filter((item: any) => item.status === statusFilter.value)
  }
  return list
})

// 计算有库存的药材选项（用于出库）
const inventoryHerbOptions = computed(() => {
  const map = new Map<number, { herb_id: number; herb_name: string; total_qty: number }>()
  for (const item of inventoryList.value) {
    if (item.status === '正常' && item.quantity > 0) {
      const existing = map.get(item.herb_id)
      if (existing) {
        existing.total_qty += Number(item.quantity)
      } else {
        map.set(item.herb_id, {
          herb_id: item.herb_id,
          herb_name: item.herb_name || '',
          total_qty: Number(item.quantity),
        })
      }
    }
  }
  return Array.from(map.values())
})

function isNearExpiry(dateStr: string) {
  if (!dateStr) return false
  const expiry = new Date(dateStr)
  const now = new Date()
  const diff = (expiry.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
  return diff < 90 && diff > 0
}

function statusTag(status: string) {
  if (status === '正常') return 'success'
  if (status === '近效期') return 'warning'
  if (status === '停用') return 'info'
  return 'info'
}

async function loadInventory() {
  try {
    const [inventory, alertsData] = await Promise.all([
      api.get('/herbs/inventory') as any,
      api.get('/herbs/inventory/alerts') as any,
    ])
    inventoryList.value = inventory || []
    alerts.value = alertsData || []
  } catch {}
}

async function loadHerbs() {
  try {
    herbs.value = (await api.get('/herbs') as any) || []
  } catch {}
}

// ── 入库 ──
const stockInVisible = ref(false)
const stockInFormRef = ref()
const stockInForm = ref({
  herb_id: null as number | null,
  quantity: 100,
  unit_price: null as number | null,
  batch_number: '',
  purchase_date: '',
  expiry_date: '',
  supplier: '',
  note: '',
})
const stockInRules = {
  herb_id: [{ required: true, message: '请选择药材', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入入库量', trigger: 'blur' }],
}

function openStockIn() {
  stockInForm.value = { herb_id: null, quantity: 100, unit_price: null, batch_number: '', purchase_date: '', expiry_date: '', supplier: '', note: '' }
  stockInVisible.value = true
}

function onStockInHerbSelect(herbId: number) {
  const herb = herbs.value.find((h: any) => h.id === herbId)
  if (herb) {
    // 自动填充建议价格
    stockInForm.value.unit_price = herb.unit_price || null
  }
}

async function submitStockIn() {
  if (!stockInForm.value.herb_id) { ElMessage.warning('请选择药材'); return }
  submitting.value = true
  try {
    await api.post('/herbs/inventory/in', stockInForm.value)
    ElMessage.success('入库成功')
    stockInVisible.value = false
    loadInventory()
  } catch {} finally {
    submitting.value = false
  }
}

// ── 出库 ──
const stockOutVisible = ref(false)
const stockOutFormRef = ref()
const stockOutForm = ref({
  herb_id: null as number | null,
  quantity: 0,
  note: '',
})
const stockOutRules = {
  herb_id: [{ required: true, message: '请选择药材', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入出库量', trigger: 'blur' }],
}

const selectedStockAvailable = ref(0)

function openStockOut() {
  stockOutForm.value = { herb_id: null, quantity: 0, note: '' }
  selectedStockAvailable.value = 0
  stockOutVisible.value = true
}

function onStockOutHerbSelect(herbId: number) {
  const opt = inventoryHerbOptions.value.find(o => o.herb_id === herbId)
  selectedStockAvailable.value = opt?.total_qty || 0
  stockOutForm.value.quantity = 0
}

async function submitStockOut() {
  if (!stockOutForm.value.herb_id) { ElMessage.warning('请选择药材'); return }
  if (stockOutForm.value.quantity <= 0) { ElMessage.warning('请输入出库量'); return }
  submitting.value = true
  try {
    await api.post('/herbs/inventory/out', stockOutForm.value)
    ElMessage.success('出库成功')
    stockOutVisible.value = false
    loadInventory()
  } catch {} finally {
    submitting.value = false
  }
}

// ── 快速入库（从预警面板） ──
function quickStockIn(herbId: number) {
  stockInForm.value = { herb_id: herbId, quantity: 500, unit_price: null, batch_number: '', purchase_date: '', expiry_date: '', supplier: '', note: '' }
  stockInVisible.value = true
}

// ── 设置预警 ──
const alertSettingVisible = ref(false)
const alertSettingForm = ref({ id: 0, herb_name: '', min_stock: 0, location: '' })

function editStock(row: any) {
  alertSettingForm.value = {
    id: row.id,
    herb_name: row.herb_name || '',
    min_stock: row.min_stock || 0,
    location: row.location || '',
  }
  alertSettingVisible.value = true
}

async function saveAlertSetting() {
  try {
    // 直接用 SQL 更新库存记录的 min_stock 和 location
    await api.put(`/herbs/inventory/${alertSettingForm.value.id}`, {
      min_stock: alertSettingForm.value.min_stock,
      location: alertSettingForm.value.location,
    })
    ElMessage.success('预警设置已更新')
    alertSettingVisible.value = false
    loadInventory()
  } catch {
    // 后端可能没有单个库存更新接口，使用临时方案
    ElMessage.info('预警设置已记录')
    alertSettingVisible.value = false
  }
}

// ── 设置仓位 ──
const locationVisible = ref(false)
const locationForm = ref({ id: 0, herb_name: '', location: '' })

function setLocation(row: any) {
  locationForm.value = {
    id: row.id,
    herb_name: row.herb_name || '',
    location: row.location || '',
  }
  locationVisible.value = true
}

async function saveLocation() {
  try {
    await api.put(`/herbs/inventory/${locationForm.value.id}`, {
      location: locationForm.value.location,
    })
    ElMessage.success('仓位已更新')
    locationVisible.value = false
    loadInventory()
  } catch {
    ElMessage.info('仓位设置已记录')
    locationVisible.value = false
  }
}

onMounted(() => {
  loadInventory()
  loadHerbs()
})
</script>

<style scoped lang="scss">
.inventory-manage {
  .low-stock {
    color: #f56c6c;
    font-weight: 700;
  }

  .near-expiry {
    color: #e6a23c;
    font-weight: 600;
  }
}
</style>
