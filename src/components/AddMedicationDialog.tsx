import { useState } from 'react'
import { X, Camera, Volume2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useAppStore } from '@/lib/store'

interface AddMedicationDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export default function AddMedicationDialog({ open, onOpenChange }: AddMedicationDialogProps) {
  const { addMedication, voiceEnabled } = useAppStore()
  
  const [name, setName] = useState('')
  const [dosage, setDosage] = useState('')
  const [time, setTime] = useState('08:00')
  const [instructions, setInstructions] = useState('')
  const [image, setImage] = useState<string | undefined>()
  
  const speak = (text: string) => {
    if (!voiceEnabled) return
    if ('speechSynthesis' in window) {
      // 先停止当前正在播放的语音
      speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'zh-CN'
      utterance.rate = 0.85  // 稍微慢一点，更适合老年人
      utterance.volume = 1   // 最大音量
      speechSynthesis.speak(utterance)
    }
  }
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!name || !dosage) {
      speak('请填写药物名称和剂量')
      return
    }
    
    addMedication({
      name,
      dosage,
      time,
      instructions,
      image,
    })
    
    speak(`${name}添加成功`)
    
    // 重置表单
    setName('')
    setDosage('')
    setTime('08:00')
    setInstructions('')
    setImage(undefined)
    
    onOpenChange(false)
  }
  
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setImage(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }
  
  if (!open) return null
  
  const handleClose = () => {
    onOpenChange(false)
  }
  
  return (
    <div 
      className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          handleClose()
        }
      }}
    >
      <Card 
        className="w-full max-w-2xl max-h-[90vh] overflow-y-auto animate-slide-in"
        onClick={(e) => e.stopPropagation()}
      >
        <CardHeader className="sticky top-0 bg-card z-10 border-b">
          <div className="flex items-center justify-between">
            <CardTitle className="text-2xl">添加新药物</CardTitle>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleClose}
              className="rounded-full hover:bg-muted transition-colors"
              type="button"
            >
              <X className="w-6 h-6" />
              <span className="sr-only">关闭</span>
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 药物名称 */}
            <div>
              <label className="block text-lg font-semibold mb-3">
                药物名称 <span className="text-destructive">*</span>
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="例如：降压药"
                className="w-full px-4 py-4 text-lg border-2 border-input rounded-xl focus:outline-none focus:ring-4 focus:ring-ring focus:border-primary transition-all"
                required
              />
            </div>
            
            {/* 剂量 */}
            <div>
              <label className="block text-lg font-semibold mb-3">
                剂量 <span className="text-destructive">*</span>
              </label>
              <input
                type="text"
                value={dosage}
                onChange={(e) => setDosage(e.target.value)}
                placeholder="例如：1片、2粒、5ml"
                className="w-full px-4 py-4 text-lg border-2 border-input rounded-xl focus:outline-none focus:ring-4 focus:ring-ring focus:border-primary transition-all"
                required
              />
            </div>
            
            {/* 服用时间 */}
            <div>
              <label className="block text-lg font-semibold mb-3">
                服用时间
              </label>
              <input
                type="time"
                value={time}
                onChange={(e) => setTime(e.target.value)}
                className="w-full px-4 py-4 text-lg border-2 border-input rounded-xl focus:outline-none focus:ring-4 focus:ring-ring focus:border-primary transition-all"
              />
            </div>
            
            {/* 服用说明 */}
            <div>
              <label className="block text-lg font-semibold mb-3">
                服用说明
              </label>
              <textarea
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
                placeholder="例如：早餐后服用、空腹服用等"
                rows={3}
                className="w-full px-4 py-4 text-lg border-2 border-input rounded-xl focus:outline-none focus:ring-4 focus:ring-ring focus:border-primary transition-all resize-none"
              />
            </div>
            
            {/* 药物照片 */}
            <div>
              <label className="block text-lg font-semibold mb-3">
                药物照片（可选）
              </label>
              
              {image ? (
                <div className="relative">
                  <img
                    src={image}
                    alt="药物照片"
                    className="w-full h-48 object-cover rounded-xl border-2 border-border"
                  />
                  <Button
                    type="button"
                    variant="destructive"
                    size="sm"
                    onClick={() => setImage(undefined)}
                    className="absolute top-2 right-2"
                  >
                    删除
                  </Button>
                </div>
              ) : (
                <label className="block">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                  <div className="border-2 border-dashed border-border rounded-xl p-8 text-center cursor-pointer hover:border-primary hover:bg-primary/5 transition-all">
                    <Camera className="w-12 h-12 mx-auto mb-3 text-muted-foreground" />
                    <p className="text-lg text-muted-foreground">
                      点击拍照或上传照片
                    </p>
                  </div>
                </label>
              )}
            </div>
            
            {/* 语音提示 */}
            <div className="bg-muted/50 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <Volume2 className="w-6 h-6 text-primary mt-1 flex-shrink-0" />
                <div>
                  <p className="text-base font-medium mb-1">温馨提示</p>
                  <p className="text-sm text-muted-foreground">
                    添加完成后，系统会在设定时间提醒您服药。您也可以随时点击"语音播报"按钮听取药物信息。
                  </p>
                </div>
              </div>
            </div>
            
            {/* 提交按钮 */}
            <div className="flex gap-4 pt-4">
              <Button
                type="button"
                variant="outline"
                size="xl"
                onClick={() => onOpenChange(false)}
                className="flex-1"
              >
                取消
              </Button>
              <Button
                type="submit"
                size="xl"
                variant="success"
                className="flex-1"
              >
                确认添加
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
