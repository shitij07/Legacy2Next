import { MarkdownRenderer } from '@/components/shared/MarkdownRenderer'

interface MarkdownReportProps {
  content: string
}

export function MarkdownReport({ content }: MarkdownReportProps) {
  return (
    <div className="rounded-lg border border-border bg-white p-6">
      <MarkdownRenderer content={content} />
    </div>
  )
}
