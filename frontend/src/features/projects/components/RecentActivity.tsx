import { Clock } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function RecentActivity() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-neutral-200">
            <Clock className="h-5 w-5 text-neutral-400" aria-hidden="true" />
          </div>
          <p className="text-sm font-medium text-neutral-700">No recent activity</p>
          <p className="mt-1 text-xs text-neutral-500">
            Activity will appear once you upload and analyse a codebase.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
