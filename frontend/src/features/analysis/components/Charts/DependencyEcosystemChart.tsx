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
import type { EcosystemBreakdown } from '@/lib/types'

interface DependencyEcosystemChartProps {
  data: EcosystemBreakdown[]
}

export function DependencyEcosystemChart({ data }: DependencyEcosystemChartProps) {
  if (data.length === 0) return null

  return (
    <Card>
      <CardHeader>
        <CardTitle>Dependency Ecosystems</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data} margin={{ left: 8, right: 8, top: 4, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-border)" />
            <XAxis dataKey="ecosystem" tick={{ fontSize: 12, fill: 'var(--color-neutral-600)' }} />
            <YAxis tick={{ fontSize: 12, fill: 'var(--color-neutral-600)' }} />
            <Tooltip
              contentStyle={{
                background: 'var(--color-neutral-100)',
                border: '1px solid var(--color-border)',
                borderRadius: 6,
                fontSize: 13,
              }}
            />
            <Bar dataKey="count" fill="var(--color-success)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
