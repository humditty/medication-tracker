import { useState, useRef } from 'react'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { X, Camera, CheckCircle2, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useAppStore } from '@/lib/store'

interface TakeMedicationDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  medicationName: string
  medicationDosage: string
  onConfirm: (photoData: string | null) => void
}

export default function TakeMedicationDialog({
  open,
  onOpenChange,
  medicationName,
  medicationDosage,
  onConfirm,
}: TakeMedicationDialogProps) {
  const { voiceEnabled } = useAppStore()
  const [photo, setPhoto] = useState<string | null>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isCameraActive, setIsCameraActive] = useState(false)
  const [stream, setStream] = useState<MediaStream | null>(null)

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

  const startCamera = async () => {
    try {
      speak('摄像头已打开，请对准药物和水杯')
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
      })
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
        setIsCameraActive(true)
      }
    } catch (error) {
      console.error('无法访问摄像头:', error)
      speak('无法访问摄像头，请检查权限设置')
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop())
      setStream(null)
      setIsCameraActive(false)
    }
  }

  const takePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current
      const canvas = canvasRef.current
      const context = canvas.getContext('2d')

      if (context) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        context.drawImage(video, 0, 0)
        const photoData = canvas.toDataURL('image/jpeg', 0.8)
        setPhoto(photoData)
        stopCamera()
        speak('照片拍摄成功！请确认是否服药')
      }
    }
  }

  const handleConfirm = () => {
    speak(`${medicationName}已记录为服用，做得很好！`)
    onConfirm(photo)
    setPhoto(null)
    stopCamera()
    onOpenChange(false)
  }

  const handleCancel = () => {
    speak('已取消')
    stopCamera()
    setPhoto(null)
    onOpenChange(false)
  }

  // 清理
  if (!open) {
    stopCamera()
  }

  return (
    <div 
      className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4"
      onClick={(e) => {
        // 点击背景时关闭
        if (e.target === e.currentTarget) {
          handleCancel()
        }
      }}
      onKeyDown={(e) => {
        // 按 ESC 键关闭
        if (e.key === 'Escape') {
          handleCancel()
        }
      }}
    >
      <Card 
        className="w-full max-w-2xl max-h-[90vh] overflow-y-auto animate-slide-in"
        onClick={(e) => e.stopPropagation()}
      >
        <CardHeader className="sticky top-0 bg-card z-10 border-b">
          <div className="flex items-center justify-between">
            <CardTitle className="text-2xl">确认服药</CardTitle>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => {
                console.log('关闭按钮被点击')
                handleCancel()
              }}
              className="rounded-full hover:bg-muted transition-colors"
              type="button"
            >
              <X className="w-6 h-6" />
              <span className="sr-only">关闭</span>
            </Button>
          </div>
        </CardHeader>

        <CardContent className="p-6 space-y-6">
          {/* 药物信息 */}
          <div className="bg-primary/5 rounded-xl p-6 border-2 border-primary/20">
            <h3 className="text-2xl font-bold mb-2">{medicationName}</h3>
            <p className="text-lg text-muted-foreground">{medicationDosage}</p>
            <p className="text-sm text-muted-foreground mt-2">
              时间：{format(new Date(), 'yyyy年M月d日 HH:mm', { locale: zhCN })}
            </p>
          </div>

          {/* 提示信息 */}
          <div className="bg-warning/10 rounded-xl p-4 border-2 border-warning/30">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-6 h-6 text-warning mt-1 flex-shrink-0" />
              <div>
                <p className="text-base font-semibold mb-1">重要提示</p>
                <p className="text-sm text-muted-foreground">
                  为了确保用药安全，请拍摄您正在服药的照片。照片中应包含：
                </p>
                <ul className="text-sm text-muted-foreground mt-2 space-y-1 ml-4">
                  <li>• 药物和手（显示您正在拿药）</li>
                  <li>• 水杯（显示准备服药）</li>
                  <li>• 您的面部（可选，但推荐）</li>
                </ul>
              </div>
            </div>
          </div>

          {/* 拍照区域 */}
          {!photo ? (
            <div className="space-y-4">
              {!isCameraActive ? (
                <Button
                  size="xl"
                  variant="default"
                  onClick={startCamera}
                  className="w-full h-32 gap-3 text-xl"
                >
                  <Camera className="w-8 h-8" />
                  打开摄像头拍照
                </Button>
              ) : (
                <div className="space-y-4">
                  <div className="relative rounded-xl overflow-hidden border-2 border-border bg-black">
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      className="w-full h-64 object-cover"
                    />
                    <canvas ref={canvasRef} className="hidden" />
                  </div>
                  <div className="flex gap-3">
                    <Button
                      size="xl"
                      variant="outline"
                      onClick={stopCamera}
                      className="flex-1"
                    >
                      取消
                    </Button>
                    <Button
                      size="xl"
                      variant="success"
                      onClick={takePhoto}
                      className="flex-1 gap-2"
                    >
                      <Camera className="w-6 h-6" />
                      拍摄照片
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              <div className="relative rounded-xl overflow-hidden border-2 border-success">
                <img
                  src={photo}
                  alt="服药照片"
                  className="w-full h-64 object-cover"
                />
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
                  <p className="text-white text-sm">
                    {format(new Date(), 'yyyy-MM-dd HH:mm:ss')}
                  </p>
                </div>
              </div>
              <div className="flex gap-3">
                <Button
                  size="xl"
                  variant="outline"
                  onClick={() => {
                    setPhoto(null)
                    startCamera()
                  }}
                  className="flex-1"
                >
                  重新拍摄
                </Button>
                <Button
                  size="xl"
                  variant="success"
                  onClick={handleConfirm}
                  className="flex-1 gap-2"
                >
                  <CheckCircle2 className="w-6 h-6" />
                  确认服药
                </Button>
              </div>
            </div>
          )}

          {/* 跳过选项 */}
          <div className="pt-4 border-t">
            <Button
              variant="ghost"
              size="lg"
              onClick={() => {
                speak('已跳过拍照，仅记录时间')
                onConfirm(null)
                setPhoto(null)
                stopCamera()
                onOpenChange(false)
              }}
              className="w-full text-muted-foreground"
            >
              跳过拍照（不推荐）
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
