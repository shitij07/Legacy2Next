import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { CategoryCount } from '@/lib/types'

const COLORS = [
  'var(--color-primary-500)',
  'var(--color-blue-500)',
  'var(--color-success)',
  'var(--color-warning)',
  'var(--color-error)',
  'var(--color-purple-500)',
  'var(--color-teal-500)',
]

interface TechnologyChartProps {
  data: CategoryCount[]
}

export function TechnologyChart({ data }: TechnologyChartProps) {
  if (data.length === 0) return null

  return (
    <Card>
      <CardHeader>
        <CardTitle>Technologies by Category</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={data}
              dataKey="count"
              nameKey="category"
              cx="50%"
              cy="50%"
              outerRadius={90}
              innerRadius={40}
              paddingAngle={2}
            >
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: 'var(--color-neutral-100)',
                border: '1px solid var(--color-border)',
                borderRadius: 6,
                fontSize: 13,
              }}
            />
            <Legend
              wrapperStyle={{ fontSize: 12 }}
              formatter={(value: string) => (
                <span style={{ color: 'var(--color-neutral-700)' }}>{value}</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
