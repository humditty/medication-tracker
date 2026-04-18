import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface Medication {
  id: string
  name: string
  dosage: string
  time: string
  instructions: string
  image?: string
}

export interface MedicationRecord {
  id: string
  medicationId: string
  date: string
  time: string
  status: 'taken' | 'missed' | 'pending'
  notes?: string
  photoData?: string  // 服药时的照片（base64）
}

interface AppState {
  medications: Medication[]
  records: MedicationRecord[]
  voiceEnabled: boolean  // 语音开关
  addMedication: (medication: Omit<Medication, 'id'>) => void
  removeMedication: (id: string) => void
  updateMedication: (id: string, updates: Partial<Medication>) => void
  recordTaken: (medicationId: string, date: string, time: string, photoData?: string) => void
  recordMissed: (medicationId: string, date: string, time: string) => void
  undoRecord: (medicationId: string, date: string) => void  // 撤回用药记录
  toggleVoice: () => void  // 切换语音开关
  getTodayRecords: () => MedicationRecord[]
  getHistory: (days?: number) => MedicationRecord[]
  getCompletionRate: (days?: number) => number
  exportData: () => string
  importData: (data: string) => boolean
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      medications: [
        {
          id: '1',
          name: '降压药',
          dosage: '1片',
          time: '08:00',
          instructions: '早餐后服用',
        },
        {
          id: '2',
          name: '钙片',
          dosage: '2片',
          time: '12:00',
          instructions: '午餐后服用',
        },
        {
          id: '3',
          name: '维生素D',
          dosage: '1粒',
          time: '20:00',
          instructions: '晚餐后服用',
        },
      ],
      records: [],
      voiceEnabled: true,  // 默认开启语音
      
      toggleVoice: () =>
        set((state) => ({
          voiceEnabled: !state.voiceEnabled,
        })),
      
      addMedication: (medication) =>
        set((state) => ({
          medications: [
            ...state.medications,
            { ...medication, id: Date.now().toString() },
          ],
        })),
      
      removeMedication: (id) =>
        set((state) => ({
          medications: state.medications.filter((m) => m.id !== id),
        })),
      
      updateMedication: (id, updates) =>
        set((state) => ({
          medications: state.medications.map((m) =>
            m.id === id ? { ...m, ...updates } : m
          ),
        })),
      
      recordTaken: (medicationId, date, time, photoData) =>
        set((state) => {
          const existingRecord = state.records.find(
            (r) => r.medicationId === medicationId && r.date === date
          )
          
          if (existingRecord) {
            return {
              records: state.records.map((r) =>
                r.medicationId === medicationId && r.date === date
                  ? { ...r, status: 'taken', time, photoData }
                  : r
              ),
            }
          }
          
          return {
            records: [
              ...state.records,
              {
                id: Date.now().toString(),
                medicationId,
                date,
                time,
                status: 'taken',
                photoData,
              },
            ],
          }
        }),
      
      recordMissed: (medicationId, date, time) =>
        set((state) => {
          const existingRecord = state.records.find(
            (r) => r.medicationId === medicationId && r.date === date
          )
          
          if (existingRecord) {
            return {
              records: state.records.map((r) =>
                r.medicationId === medicationId && r.date === date
                  ? { ...r, status: 'missed', time }
                  : r
              ),
            }
          }
          
          return {
            records: [
              ...state.records,
              {
                id: Date.now().toString(),
                medicationId,
                date,
                time,
                status: 'missed',
              },
            ],
          }
        }),
      
      // 撤回用药记录（重置为待服用状态）
      undoRecord: (medicationId, date) =>
        set((state) => ({
          records: state.records.filter(
            (r) => !(r.medicationId === medicationId && r.date === date)
          ),
        })),
      
      getTodayRecords: () => {
        const today = new Date().toISOString().split('T')[0]
        return get().records.filter((r) => r.date === today)
      },
      
      getHistory: (days = 7) => {
        const cutoffDate = new Date()
        cutoffDate.setDate(cutoffDate.getDate() - days)
        const cutoffStr = cutoffDate.toISOString().split('T')[0]
        
        return get().records
          .filter((r) => r.date >= cutoffStr)
          .sort((a, b) => b.date.localeCompare(a.date) || b.time.localeCompare(a.time))
      },
      
      getCompletionRate: (days = 7) => {
        const history = get().getHistory(days)
        if (history.length === 0) return 0
        
        const takenCount = history.filter((r) => r.status === 'taken').length
        return Math.round((takenCount / history.length) * 100)
      },
      
      // 导出数据为 JSON 字符串
      exportData: () => {
        const state = get()
        const data = {
          medications: state.medications,
          records: state.records,
          exportDate: new Date().toISOString(),
          version: '1.0',
        }
        return JSON.stringify(data, null, 2)
      },
      
      // 从 JSON 字符串导入数据
      importData: (data: string) => {
        try {
          const parsed = JSON.parse(data)
          if (parsed.medications && parsed.records) {
            set({
              medications: parsed.medications,
              records: parsed.records,
            })
            return true
          }
          return false
        } catch (error) {
          console.error('导入数据失败:', error)
          return false
        }
      },
    }),
    {
      name: 'medication-storage',
    }
  )
)
