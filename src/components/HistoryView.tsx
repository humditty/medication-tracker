import { useState } from 'react'
import { format, subDays } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { CheckCircle2, XCircle, Clock, Calendar, TrendingUp, Volume2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useAppStore } from '@/lib/store'

export default function HistoryView() {
  const { medications, getHistory, getCompletionRate } = useAppStore()
  const [selectedDays, setSelectedDays] = useState(7)
  
  const history = getHistory(selectedDays)
  const completionRate = getCompletionRate(selectedDays)
  
  const speak = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'zh-CN'
      utterance.rate = 0.9
      speechSynthesis.speak(utterance)
    }
  }
  
  const handleSpeakSummary = () => {
    const daysText = selectedDays === 7 ? '近7天' : `近${selectedDays}天`
    const message = `${daysText}的用药完成率为${completionRate}%。共记录${history.length}次用药，其中服用${history.filter(r => r.status === 'taken').length}次，未服用${history.filter(r => r.status === 'missed').length}次。`
    speak(message)
  }
  
  // 按日期分组
  const groupedByDate = history.reduce((acc, record) => {
    if (!acc[record.date]) {
      acc[record.date] = []
    }
    acc[record.date].push(record)
    return acc
  }, {} as Record<string, typeof history>)
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'taken':
        return <CheckCircle2 className="w-6 h-6 text-success" />
      case 'missed':
        return <XCircle className="w-6 h-6 text-destructive" />
      default:
        return <Clock className="w-6 h-6 text-warning" />
    }
  }
  
  const getStatusText = (status: string) => {
    switch (status) {
      case 'taken':
        return '已服用'
      case 'missed':
        return '未服用'
      default:
        return '待服用'
    }
  }
  
  const getMedicationName = (medicationId: string) => {
    const med = medications.find(m => m.id === medicationId)
    return med?.name || '未知药物'
  }
  
  return (
    <div className="space-y-6 animate-slide-in">
      {/* 统计卡片 */}
      <Card className="bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20">
        <CardContent className="p-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-lg text-muted-foreground mb-2">
                {selectedDays === 7 ? '近7天' : `近${selectedDays}天`}用药完成率
              </p>
              <div className="flex items-baseline gap-3">
                <h1 className="text-6xl font-bold text-primary">{completionRate}%</h1>
                <TrendingUp className="w-8 h-8 text-success" />
              </div>
            </div>
            <Button
              size="xl"
              variant="default"
              onClick={handleSpeakSummary}
              className="gap-3"
            >
              <Volume2 className="w-8 h-8" />
              <span className="text-xl">播报统计</span>
            </Button>
          </div>
        </CardContent>
      </Card>
      
      {/* 时间范围选择 */}
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-3">
            <Button
              variant={selectedDays === 7 ? 'default' : 'outline'}
              size="lg"
              onClick={() => setSelectedDays(7)}
              className="flex-1"
            >
              近7天
            </Button>
            <Button
              variant={selectedDays === 14 ? 'default' : 'outline'}
              size="lg"
              onClick={() => setSelectedDays(14)}
              className="flex-1"
            >
              近14天
            </Button>
            <Button
              variant={selectedDays === 30 ? 'default' : 'outline'}
              size="lg"
              onClick={() => setSelectedDays(30)}
              className="flex-1"
            >
              近30天
            </Button>
          </div>
        </CardContent>
      </Card>
      
      {/* 历史记录列表 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-3 text-2xl">
            <Calendar className="w-7 h-7 text-primary" />
            <span>用药历史</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {Object.keys(groupedByDate).length === 0 ? (
            <div className="text-center py-12">
              <Clock className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
              <p className="text-xl text-muted-foreground">暂无历史记录</p>
            </div>
          ) : (
            <div className="space-y-6">
              {Object.entries(groupedByDate)
                .sort(([a], [b]) => b.localeCompare(a))
                .map(([date, records]) => (
                  <div key={date} className="space-y-3">
                    <h3 className="text-xl font-semibold flex items-center gap-2">
                      <Calendar className="w-5 h-5 text-primary" />
                      {format(new Date(date), 'M月d日 EEEE', { locale: zhCN })}
                    </h3>
                    
                    <div className="space-y-3">
                      {records.map((record) => (
                        <div
                          key={record.id}
                          className="medication-item"
                        >
                          <div className="flex items-center gap-4 flex-1">
                            {getStatusIcon(record.status)}
                            <div className="flex-1">
                              <p className="text-lg font-medium">
                                {getMedicationName(record.medicationId)}
                              </p>
                              <p className="text-sm text-muted-foreground">
                                {record.time}
                              </p>
                            </div>
                          </div>
                          <Badge
                            variant={
                              record.status === 'taken'
                                ? 'success'
                                : record.status === 'missed'
                                ? 'destructive'
                                : 'warning'
                            }
                            className="text-base px-4 py-2"
                          >
                            {getStatusText(record.status)}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
