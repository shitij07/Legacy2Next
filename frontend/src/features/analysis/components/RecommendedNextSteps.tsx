import { Upload, BarChart3, FileText, Brain } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const steps = [
  {
    icon: Upload,
    label: 'Upload Codebase',
    description: 'Start by uploading your legacy codebase as a ZIP file.',
  },
  {
    icon: BarChart3,
    label: 'Run Analysis',
    description: 'Analyse the uploaded codebase to detect technologies and dependencies.',
  },
  {
    icon: Brain,
    label: 'AI Insights',
    description: 'Generate AI-powered summaries and architecture recommendations.',
  },
  {
    icon: FileText,
    label: 'Review Report',
    description: 'Review the detailed migration report and plan your next steps.',
  },
]

export function RecommendedNextSteps() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recommended Next Steps</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 sm:grid-cols-2">
          {steps.map((step) => {
            const Icon = step.icon
            return (
              <div key={step.label} className="flex items-start gap-3 rounded-lg border border-border p-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary-500/10">
                  <Icon className="h-4 w-4 text-primary-500" aria-hidden="true" />
                </div>
                <div>
                  <p className="text-sm font-medium text-neutral-900">{step.label}</p>
                  <p className="mt-0.5 text-xs text-neutral-600">{step.description}</p>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
