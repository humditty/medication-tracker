import { useState } from 'react'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { CheckCircle2, Clock, XCircle, Volume2, Camera, Pill, Undo2, AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useAppStore } from '@/lib/store'
import TakeMedicationDialog from './TakeMedicationDialog'

interface MedicationListProps {
  mode?: 'elder' | 'family'
}

export default function MedicationList({ mode = 'family' }: MedicationListProps) {
  const { medications, records, recordTaken, recordMissed, undoRecord, voiceEnabled } = useAppStore()
  const [showTakeDialog, setShowTakeDialog] = useState(false)
  const [selectedMedication, setSelectedMedication] = useState<{ id: string; name: string; dosage: string } | null>(null)
  const [showUndoConfirm, setShowUndoConfirm] = useState<string | null>(null) // 存储待撤回的药物ID
  
  const today = new Date().toISOString().split('T')[0]
  const todayRecords = records.filter(r => r.date === today)
  
  const speak = (text: string) => {
    if (!voiceEnabled) return  // 语音关闭时不播报
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'zh-CN'
      utterance.rate = 0.9
      speechSynthesis.speak(utterance)
    }
  }
  
  const handleOpenTakeDialog = (medicationId: string, name: string, dosage: string) => {
    setSelectedMedication({ id: medicationId, name, dosage })
    setShowTakeDialog(true)
    speak(`请拍摄${name}的服药照片`)
  }
  
  const handleConfirmTake = (photoData: string | null) => {
    if (selectedMedication) {
      const now = new Date()
      const timeStr = format(now, 'HH:mm')
      recordTaken(selectedMedication.id, today, timeStr, photoData)
      
      speak(`${selectedMedication.name}已记录为服用`)
      setSelectedMedication(null)
      setShowUndoConfirm(null)
    }
  }
  
  const handleMissMedication = (medicationId: string, name: string) => {
    const now = new Date()
    const timeStr = format(now, 'HH:mm')
    recordMissed(medicationId, today, timeStr)
    
    speak(`${name}已记录为未服用`)
    setShowUndoConfirm(null)
  }
  
  const handleUndoRecord = (medicationId: string, name: string) => {
    undoRecord(medicationId, today)
    setShowUndoConfirm(null)
    speak(`${name}的记录已撤回`)
  }
  
  const getRecordStatus = (medicationId: string) => {
    const record = todayRecords.find(r => r.medicationId === medicationId)
    return record?.status || 'pending'
  }
  
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'taken':
        return (
          <Badge variant="success" className={`gap-2 ${mode === 'elder' ? 'text-xl px-6 py-3' : 'text-base px-4 py-2'}`}>
            <CheckCircle2 className={mode === 'elder' ? 'w-7 h-7' : 'w-5 h-5'} />
            已服用
          </Badge>
        )
      case 'missed':
        return (
          <Badge variant="destructive" className={`gap-2 ${mode === 'elder' ? 'text-xl px-6 py-3' : 'text-base px-4 py-2'}`}>
            <XCircle className={mode === 'elder' ? 'w-7 h-7' : 'w-5 h-5'} />
            未服用
          </Badge>
        )
      default:
        return (
          <Badge variant="warning" className={`gap-2 ${mode === 'elder' ? 'text-xl px-6 py-3' : 'text-base px-4 py-2'}`}>
            <Clock className={mode === 'elder' ? 'w-7 h-7' : 'w-5 h-5'} />
            待服用
          </Badge>
        )
    }
  }
  
  if (medications.length === 0) {
    return (
      <Card>
        <CardContent className={`${mode === 'elder' ? 'p-16' : 'p-12'} text-center`}>
          <div className={`mx-auto mb-6 rounded-full bg-muted flex items-center justify-center ${mode === 'elder' ? 'w-32 h-32' : 'w-24 h-24'}`}>
            <Pill className={mode === 'elder' ? 'w-16 h-16 text-muted-foreground' : 'w-12 h-12 text-muted-foreground'} />
          </div>
          <h3 className={`${mode === 'elder' ? 'text-3xl mb-4' : 'text-2xl mb-3'} font-semibold`}>暂无药物</h3>
          <p className={`${mode === 'elder' ? 'text-xl mb-8' : 'text-lg mb-6'} text-muted-foreground`}>
            点击"添加药物"开始记录您的用药情况
          </p>
        </CardContent>
      </Card>
    )
  }
  
  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className={`flex items-center gap-3 ${mode === 'elder' ? 'text-3xl' : 'text-2xl'}`}>
            <Clock className={mode === 'elder' ? 'w-9 h-9 text-primary' : 'w-7 h-7 text-primary'} />
            <span>{mode === 'elder' ? '今天要吃的药' : '今日用药计划'}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {medications.map((medication) => {
            const status = getRecordStatus(medication.id)
            
            return (
              <div
                key={medication.id}
                className={`medication-item ${status} ${mode === 'elder' ? 'p-6' : ''}`}
              >
                <div className="flex-1">
                  <div className={`flex items-start justify-between ${mode === 'elder' ? 'mb-4' : 'mb-3'}`}>
                    <div>
                      <h4 className={`${mode === 'elder' ? 'text-2xl mb-2' : 'text-xl font-semibold mb-1'}`}>{medication.name}</h4>
                      <p className={`${mode === 'elder' ? 'text-xl' : 'text-base'} text-muted-foreground`}>
                        {medication.dosage} · {medication.time}
                      </p>
                      {medication.instructions && (
                        <p className={`${mode === 'elder' ? 'text-lg mt-2' : 'text-sm mt-1'} text-muted-foreground`}>
                          {medication.instructions}
                        </p>
                      )}
                    </div>
                    {getStatusBadge(status)}
                  </div>
                  
                  {status === 'pending' && (
                    <div className={`flex ${mode === 'elder' ? 'flex-col gap-4' : 'gap-3'}`}>
                      <Button
                        size={mode === 'elder' ? 'xl' : 'lg'}
                        variant="success"
                        onClick={() => handleOpenTakeDialog(medication.id, medication.name, medication.dosage)}
                        className={`${mode === 'elder' ? 'btn-elder w-full gap-4' : 'flex-1 gap-2 text-lg'}`}
                      >
                        <Camera className={mode === 'elder' ? 'w-10 h-10' : 'w-6 h-6'} />
                        {mode === 'elder' ? '拍照确认服药' : '拍照确认服药'}
                      </Button>
                      
                      <Button
                        size={mode === 'elder' ? 'xl' : 'lg'}
                        variant="outline"
                        onClick={() => handleMissMedication(medication.id, medication.name)}
                        className={`${mode === 'elder' ? 'btn-elder w-full gap-4' : 'gap-2'}`}
                      >
                        <XCircle className={mode === 'elder' ? 'w-10 h-10' : 'w-6 h-6'} />
                        {mode === 'elder' ? '今天没吃这个药' : '未服用'}
                      </Button>
                    </div>
                  )}
                  
                  {status !== 'pending' && (
                    <div className="space-y-3">
                      {/* 语音播报 - 仅家属模式 */}
                      {mode === 'family' && (
                        <div className="flex gap-3">
                          <Button
                            size="lg"
                            variant="ghost"
                            onClick={() => speak(`${medication.name}，${medication.dosage}，${medication.time}，${medication.instructions}`)}
                            className="gap-2"
                          >
                            <Volume2 className="w-5 h-5" />
                            语音播报
                          </Button>
                          
                          {medication.image && (
                            <Button
                              size="lg"
                              variant="outline"
                              className="gap-2"
                            >
                              <Camera className="w-5 h-5" />
                              查看照片
                            </Button>
                          )}
                        </div>
                      )}
                      
                      {/* 撤回按钮 - 两种模式都显示 */}
                      {showUndoConfirm === medication.id ? (
                        <div className="bg-warning/10 border-2 border-warning/30 rounded-xl p-4 space-y-3">
                          <div className="flex items-start gap-3">
                            <AlertTriangle className="w-6 h-6 text-warning mt-1 flex-shrink-0" />
                            <div>
                              <p className="text-base font-semibold mb-1">确认撤回？</p>
                              <p className="text-sm text-muted-foreground">
                                撤回后需要重新记录服药状态
                              </p>
                            </div>
                          </div>
                          <div className="flex gap-3">
                            <Button
                              size="lg"
                              variant="outline"
                              onClick={() => setShowUndoConfirm(null)}
                              className="flex-1"
                            >
                              取消
                            </Button>
                            <Button
                              size="lg"
                              variant="warning"
                              onClick={() => handleUndoRecord(medication.id, medication.name)}
                              className="flex-1 gap-2"
                            >
                              <Undo2 className="w-5 h-5" />
                              确认撤回
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <Button
                          size={mode === 'elder' ? 'xl' : 'lg'}
                          variant="secondary"
                          onClick={() => setShowUndoConfirm(medication.id)}
                          className={`${mode === 'elder' ? 'btn-elder w-full gap-4' : 'w-full gap-2'}`}
                        >
                          <Undo2 className={mode === 'elder' ? 'w-8 h-8' : 'w-5 h-5'} />
                          {mode === 'elder' ? '点错了？撤销记录' : '点错了？撤回记录'}
                        </Button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </CardContent>
      </Card>
      
      {/* 拍照确认对话框 */}
      {selectedMedication && (
        <TakeMedicationDialog
          open={showTakeDialog}
          onOpenChange={setShowTakeDialog}
          medicationName={selectedMedication.name}
          medicationDosage={selectedMedication.dosage}
          onConfirm={handleConfirmTake}
        />
      )}
    </>
  )
}
