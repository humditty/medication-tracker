import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { TrendingUp, CheckCircle2, XCircle, AlertCircle, Volume2, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useAppStore } from '@/lib/store'

export default function FamilyMonitor() {
  const { medications, getTodayRecords, getCompletionRate, getHistory } = useAppStore()
  
  const todayRecords = getTodayRecords()
  const completionRate = getCompletionRate(7)
  const history = getHistory(7)
  
  const takenCount = todayRecords.filter(r => r.status === 'taken').length
  const missedCount = todayRecords.filter(r => r.status === 'missed').length
  const pendingCount = medications.length - takenCount - missedCount
  
  const speak = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'zh-CN'
      utterance.rate = 0.9
      speechSynthesis.speak(utterance)
    }
  }
  
  const handleSpeakReport = () => {
    const dateStr = format(new Date(), 'M月d日', { locale: zhCN })
    const message = `家属监控报告：今天是${dateStr}。老人今天已服用${takenCount}种药物，未服用${missedCount}种，还有${pendingCount}种待服用。近7天完成率为${completionRate}%。`
    speak(message)
  }
  
  // 计算每日完成率
  const dailyStats = Array.from({ length: 7 }, (_, i) => {
    const date = new Date()
    date.setDate(date.getDate() - i)
    const dateStr = date.toISOString().split('T')[0]
    
    const dayRecords = history.filter(r => r.date === dateStr)
    const total = dayRecords.length
    const taken = dayRecords.filter(r => r.status === 'taken').length
    const rate = total > 0 ? Math.round((taken / total) * 100) : 0
    
    return {
      date: dateStr,
      label: format(date, 'M/d', { locale: zhCN }),
      total,
      taken,
      rate,
    }
  }).reverse()
  
  return (
    <div className="space-y-6 animate-slide-in">
      {/* 标题和快速操作 */}
      <Card className="bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20">
        <CardContent className="p-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold mb-2">用药统计分析</h1>
              <p className="text-lg text-muted-foreground">
                {format(new Date(), 'yyyy年M月d日 EEEE', { locale: zhCN })}
              </p>
            </div>
            <Button
              size="xl"
              variant="default"
              onClick={handleSpeakReport}
              className="gap-3"
            >
              <Volume2 className="w-8 h-8" />
              <span className="text-xl">播报报告</span>
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="stat-card border-success/30 bg-success/5">
              <div className="flex items-center gap-4">
                <div className="icon-circle bg-success/20">
                  <CheckCircle2 className="w-10 h-10 text-success" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">今日已服用</p>
                  <p className="text-5xl font-bold text-success">{takenCount}</p>
                  <p className="text-sm text-muted-foreground">种药物</p>
                </div>
              </div>
            </div>
            
            <div className="stat-card border-destructive/30 bg-destructive/5">
              <div className="flex items-center gap-4">
                <div className="icon-circle bg-destructive/20">
                  <XCircle className="w-10 h-10 text-destructive" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">今日未服用</p>
                  <p className="text-5xl font-bold text-destructive">{missedCount}</p>
                  <p className="text-sm text-muted-foreground">种药物</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* 完成率趋势 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-3 text-2xl">
            <TrendingUp className="w-7 h-7 text-primary" />
            <span>近7天完成率趋势</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {dailyStats.map((stat) => (
              <div key={stat.date} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-base font-medium">{stat.label}</span>
                  <span className="text-base font-semibold text-primary">
                    {stat.rate}%
                  </span>
                </div>
                <div className="h-3 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-primary transition-all duration-500"
                    style={{ width: `${stat.rate}%` }}
                  />
                </div>
                <p className="text-sm text-muted-foreground">
                  {stat.taken}/{stat.total} 次用药
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      
      {/* 今日详细记录 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-3 text-2xl">
            <AlertCircle className="w-7 h-7 text-primary" />
            <span>今日详细记录</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {todayRecords.length === 0 ? (
            <div className="text-center py-12">
              <Clock className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
              <p className="text-xl text-muted-foreground">今日暂无记录</p>
            </div>
          ) : (
            <div className="space-y-3">
              {todayRecords.map((record) => {
                const medication = medications.find(m => m.id === record.medicationId)
                
                return (
                  <div
                    key={record.id}
                    className={`medication-item ${record.status}`}
                  >
                    <div className="flex items-center gap-4 flex-1">
                      {record.status === 'taken' ? (
                        <CheckCircle2 className="w-8 h-8 text-success" />
                      ) : record.status === 'missed' ? (
                        <XCircle className="w-8 h-8 text-destructive" />
                      ) : (
                        <Clock className="w-8 h-8 text-warning" />
                      )}
                      <div className="flex-1">
                        <p className="text-lg font-semibold">
                          {medication?.name || '未知药物'}
                        </p>
                        <p className="text-base text-muted-foreground">
                          {medication?.dosage} · {record.time}
                        </p>
                        {medication?.instructions && (
                          <p className="text-sm text-muted-foreground mt-1">
                            {medication.instructions}
                          </p>
                        )}
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
                      {record.status === 'taken'
                        ? '已服用'
                        : record.status === 'missed'
                        ? '未服用'
                        : '待服用'}
                    </Badge>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
      
      {/* 温馨提示 */}
      <Card className="bg-muted/50">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <AlertCircle className="w-6 h-6 text-primary mt-1 flex-shrink-0" />
            <div>
              <h4 className="text-lg font-semibold mb-2">温馨提示</h4>
              <ul className="space-y-2 text-base text-muted-foreground">
                <li>• 建议每天查看老人的用药记录，及时发现问题</li>
                <li>• 可以导出数据备份，防止数据丢失</li>
                <li>• 如果老人忘记服药，请及时提醒</li>
                <li>• 保持规律的用药时间有助于健康</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
