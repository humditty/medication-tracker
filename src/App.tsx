import { useState } from 'react'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { 
  Pill, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Camera, 
  History, 
  Users, 
  Bell,
  Volume2,
  VolumeX,
  Calendar,
  TrendingUp,
  AlertCircle,
  Plus,
  Trash2,
  Download,
  Upload,
  Home
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useAppStore } from '@/lib/store'
import MedicationList from '@/components/MedicationList'
import AddMedicationDialog from '@/components/AddMedicationDialog'
import HistoryView from '@/components/HistoryView'
import FamilyMonitor from '@/components/FamilyMonitor'

type ViewType = 'home' | 'history' | 'family'
type ModeType = 'elder' | 'family'

export default function App() {
  const [currentView, setCurrentView] = useState<ViewType>('home')
  const [currentMode, setCurrentMode] = useState<ModeType>('elder')
  const [showAddDialog, setShowAddDialog] = useState(false)
  
  const { medications, getTodayRecords, getCompletionRate, exportData, importData, voiceEnabled, toggleVoice } = useAppStore()
  
  const todayRecords = getTodayRecords()
  const weeklyCompletionRate = getCompletionRate(7)
  
  const takenCount = todayRecords.filter(r => r.status === 'taken').length
  const missedCount = todayRecords.filter(r => r.status === 'missed').length
  const pendingCount = medications.length - takenCount - missedCount
  
  // 计算今日完成率（基于今日药物总数）
  const todayCompletionRate = medications.length > 0 
    ? Math.round((takenCount / medications.length) * 100)
    : 0
  
  const speak = (text: string) => {
    if (!voiceEnabled) return  // 语音关闭时不播报
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'zh-CN'
      utterance.rate = 0.9
      utterance.pitch = 1
      speechSynthesis.speak(utterance)
    }
  }
  
  // 导出数据
  const handleExportData = () => {
    const data = exportData()
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `用药记录备份_${format(new Date(), 'yyyy-MM-dd')}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    speak('数据已导出，请妥善保存备份文件')
  }
  
  // 导入数据
  const handleImportData = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target?.result as string
        const success = importData(content)
        if (success) {
          speak('数据导入成功')
          alert('数据导入成功！')
        } else {
          speak('数据导入失败，请检查文件格式')
          alert('数据导入失败，请检查文件格式')
        }
      }
      reader.readAsText(file)
    }
  }
  
  const handleSpeakTodayStatus = () => {
    const dateStr = format(new Date(), 'M月d日', { locale: zhCN })
    const message = `今天是${dateStr}，您今天已经服用了${takenCount}种药物，还有${pendingCount}种药物待服用。今日完成率为${todayCompletionRate}%，近7天完成率为${weeklyCompletionRate}%。`
    speak(message)
  }
  
  // 老人模式 - 简化界面
  const renderElderMode = () => (
    <div className="space-y-8 animate-slide-in elder-mode">
      {/* 日期和问候 - 超大显示 */}
      <Card className="bg-gradient-to-br from-primary/10 to-primary/5 border-primary/30 shadow-medium">
        <CardContent className="p-10">
          <div className="text-center">
            <p className="text-2xl text-muted-foreground mb-3">
              {format(new Date(), 'EEEE', { locale: zhCN })}
            </p>
            <h1 className="text-6xl font-bold mb-4 text-primary">
              {format(new Date(), 'M月d日', { locale: zhCN })}
            </h1>
            <p className="text-2xl text-muted-foreground">
              现在是 {format(new Date(), 'HH:mm')}
            </p>
          </div>
        </CardContent>
      </Card>
      
      {/* 今日状态 - 超大卡片 */}
      <div className="grid grid-cols-1 gap-6">
        <Card className="border-success/40 bg-success/5">
          <CardContent className="p-8">
            <div className="flex items-center justify-center gap-6">
              <div className="icon-circle bg-success/20">
                <CheckCircle2 className="w-12 h-12 text-success" />
              </div>
              <div className="text-center">
                <p className="text-2xl text-muted-foreground mb-2">已服用</p>
                <p className="text-7xl font-bold text-success">{takenCount}</p>
                <p className="text-xl text-muted-foreground mt-2">种药物</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-warning/40 bg-warning/5">
          <CardContent className="p-8">
            <div className="flex items-center justify-center gap-6">
              <div className="icon-circle bg-warning/20">
                <Clock className="w-12 h-12 text-warning" />
              </div>
              <div className="text-center">
                <p className="text-2xl text-muted-foreground mb-2">待服用</p>
                <p className="text-7xl font-bold text-warning">{pendingCount}</p>
                <p className="text-xl text-muted-foreground mt-2">种药物</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* 快速操作 - 超大按钮 */}
      <div className="grid grid-cols-1 gap-4">
        <Button
          size="xl"
          variant="default"
          onClick={handleSpeakTodayStatus}
          className="btn-elder gap-4"
        >
          <Volume2 className="w-10 h-10" />
          <span>播报今日状态</span>
        </Button>
        
        <Button
          size="xl"
          variant="success"
          onClick={() => setShowAddDialog(true)}
          className="btn-elder gap-4"
        >
          <Plus className="w-10 h-10" />
          <span>添加新药物</span>
        </Button>
        
        <Button
          size="xl"
          variant="outline"
          onClick={() => setCurrentView('history')}
          className="btn-elder gap-4"
        >
          <History className="w-10 h-10" />
          <span>查看历史记录</span>
        </Button>
      </div>
      
      {/* 今日用药列表 */}
      <MedicationList mode="elder" />
    </div>
  )
  
  // 家属模式 - 完整功能
  const renderFamilyMode = () => (
    <div className="space-y-6 animate-slide-in family-mode">
      {/* 日期和问候 */}
      <Card className="bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20">
        <CardContent className="p-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-lg text-muted-foreground mb-2">
                {format(new Date(), 'EEEE', { locale: zhCN })}
              </p>
              <h1 className="text-4xl font-bold mb-2">
                {format(new Date(), 'M月d日', { locale: zhCN })}
              </h1>
              <p className="text-xl text-muted-foreground">
                今天是用药的好日子
              </p>
            </div>
            <Button
              size="xl"
              variant="default"
              onClick={handleSpeakTodayStatus}
              className="gap-3"
            >
              <Volume2 className="w-8 h-8" />
              <span className="text-xl">播报今日状态</span>
            </Button>
          </div>
        </CardContent>
      </Card>
      
      {/* 今日统计 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-success/30 bg-success/5">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-success/20 flex items-center justify-center">
                <CheckCircle2 className="w-8 h-8 text-success" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">已服用</p>
                <p className="text-4xl font-bold text-success">{takenCount}</p>
                <p className="text-sm text-muted-foreground">种药物</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-warning/30 bg-warning/5">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-warning/20 flex items-center justify-center">
                <Clock className="w-8 h-8 text-warning" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">待服用</p>
                <p className="text-4xl font-bold text-warning">{pendingCount}</p>
                <p className="text-sm text-muted-foreground">种药物</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-primary/30 bg-primary/5">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
                <TrendingUp className="w-8 h-8 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">完成率</p>
                <p className="text-4xl font-bold text-primary">{todayCompletionRate}%</p>
                <p className="text-sm text-muted-foreground">今日</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* 快速操作 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <Bell className="w-6 h-6 text-primary" />
            <span>快速操作</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <Button
              size="xl"
              variant="success"
              onClick={() => setShowAddDialog(true)}
              className="h-24 text-xl gap-3"
            >
              <Plus className="w-8 h-8" />
              <span>添加药物</span>
            </Button>
            
            <Button
              size="xl"
              variant="outline"
              onClick={() => setCurrentView('history')}
              className="h-24 text-xl gap-3"
            >
              <History className="w-8 h-8" />
              <span>查看历史</span>
            </Button>
          </div>
          
          {/* 数据备份 */}
          <div className="grid grid-cols-2 gap-4 pt-4 border-t">
            <Button
              size="lg"
              variant="secondary"
              onClick={handleExportData}
              className="h-16 gap-2"
            >
              <Download className="w-5 h-5" />
              <span>导出备份</span>
            </Button>
            
            <label className="cursor-pointer">
              <input
                type="file"
                accept=".json"
                onChange={handleImportData}
                className="hidden"
              />
              <Button
                size="lg"
                variant="secondary"
                className="h-16 gap-2 w-full"
                asChild
              >
                <span>
                  <Upload className="w-5 h-5" />
                  <span>导入备份</span>
                </span>
              </Button>
            </label>
          </div>
        </CardContent>
      </Card>
      
      {/* 今日用药列表 */}
      <MedicationList mode="family" />
    </div>
  )
  
  return (
    <div className="min-h-screen bg-background">
      {/* 顶部导航 */}
      <header className="sticky top-0 z-50 bg-card/90 backdrop-blur-lg border-b shadow-soft">
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-col gap-4">
            {/* 标题栏 */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-gradient-primary flex items-center justify-center">
                  <Pill className="w-7 h-7 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold">用药助手</h1>
                  <p className="text-sm text-muted-foreground">关爱老人健康</p>
                </div>
              </div>
              
              {/* 语音开关 */}
              <Button
                variant={voiceEnabled ? 'default' : 'outline'}
                size="lg"
                onClick={toggleVoice}
                className="gap-2"
                title={voiceEnabled ? '点击关闭语音' : '点击开启语音'}
              >
                {voiceEnabled ? (
                  <>
                    <Volume2 className="w-5 h-5" />
                    <span className="hidden sm:inline">语音开</span>
                  </>
                ) : (
                  <>
                    <VolumeX className="w-5 h-5" />
                    <span className="hidden sm:inline">语音关</span>
                  </>
                )}
              </Button>
            </div>
            
            {/* 模式切换标签 */}
            <div className="flex items-center gap-2 bg-secondary/50 p-1.5 rounded-2xl">
              <button
                onClick={() => {
                  setCurrentMode('elder')
                  setCurrentView('home')
                  speak('已切换到老人模式')
                }}
                className={`mode-tab flex-1 flex items-center justify-center gap-2 ${
                  currentMode === 'elder' ? 'active' : 'inactive'
                }`}
              >
                <Home className="w-5 h-5" />
                <span>老人模式</span>
              </button>
              <button
                onClick={() => {
                  setCurrentMode('family')
                  setCurrentView('home')
                  speak('已切换到家属模式')
                }}
                className={`mode-tab flex-1 flex items-center justify-center gap-2 ${
                  currentMode === 'family' ? 'active' : 'inactive'
                }`}
              >
                <Users className="w-5 h-5" />
                <span>家属模式</span>
              </button>
            </div>
            
            {/* 子导航 - 仅在家属模式显示 */}
            {currentMode === 'family' && (
              <nav className="flex gap-2">
                <Button
                  variant={currentView === 'home' ? 'default' : 'ghost'}
                  size="lg"
                  onClick={() => setCurrentView('home')}
                  className="gap-2 flex-1"
                >
                  <Calendar className="w-5 h-5" />
                  <span>今日</span>
                </Button>
                
                <Button
                  variant={currentView === 'history' ? 'default' : 'ghost'}
                  size="lg"
                  onClick={() => setCurrentView('history')}
                  className="gap-2 flex-1"
                >
                  <History className="w-5 h-5" />
                  <span>历史</span>
                </Button>
                
                <Button
                  variant={currentView === 'family' ? 'default' : 'ghost'}
                  size="lg"
                  onClick={() => setCurrentView('family')}
                  className="gap-2 flex-1"
                >
                  <Users className="w-5 h-5" />
                  <span>监控</span>
                </Button>
              </nav>
            )}
          </div>
        </div>
      </header>
      
      {/* 主内容区 */}
      <main className="container mx-auto px-4 py-8 max-w-5xl">
        {currentMode === 'elder' && currentView === 'home' && renderElderMode()}
        {currentMode === 'family' && currentView === 'home' && renderFamilyMode()}
        {currentMode === 'family' && currentView === 'history' && <HistoryView />}
        {currentMode === 'family' && currentView === 'family' && <FamilyMonitor />}
      </main>
      
      {/* 添加药物对话框 */}
      <AddMedicationDialog 
        open={showAddDialog} 
        onOpenChange={setShowAddDialog} 
      />
    </div>
  )
}
