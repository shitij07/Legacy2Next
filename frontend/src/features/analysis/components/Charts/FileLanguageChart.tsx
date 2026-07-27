import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { LanguageCount } from '@/lib/types'

interface FileLanguageChartProps {
  data: LanguageCount[]
}

export function FileLanguageChart({ data }: FileLanguageChartProps) {
  if (data.length === 0) return null

  const sorted = [...data].sort((a, b) => b.count - a.count).slice(0, 10)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Languages</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={sorted} layout="vertical" margin={{ left: 80, right: 8, top: 4, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--color-border)" />
            <XAxis type="number" tick={{ fontSize: 12, fill: 'var(--color-neutral-600)' }} />
            <YAxis
              type="category"
              dataKey="language"
              tick={{ fontSize: 12, fill: 'var(--color-neutral-600)' }}
              width={70}
            />
            <Tooltip
              contentStyle={{
                background: 'var(--color-neutral-100)',
                border: '1px solid var(--color-border)',
                borderRadius: 6,
                fontSize: 13,
              }}
            />
            <Bar dataKey="count" fill="var(--color-primary-500)" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
