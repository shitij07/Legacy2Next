import { useMemo } from 'react'
import { Copy } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'

interface JsonReportProps {
  content: string
}

export function JsonReport({ content }: JsonReportProps) {
  const formattedJson = useMemo(() => {
    try {
      const parsed = JSON.parse(content)
      return JSON.stringify(parsed, null, 2)
    } catch {
      return content
    }
  }, [content])

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(formattedJson)
      toast.success('Copied to clipboard')
    } catch {
      toast.error('Failed to copy')
    }
  }

  return (
    <div className="rounded-lg border border-border">
      <div className="flex items-center justify-between border-b border-border bg-neutral-50 px-4 py-2">
        <span className="text-xs font-medium text-neutral-600">JSON</span>
        <Button variant="ghost" size="sm" onClick={handleCopy} aria-label="Copy JSON to clipboard">
          <Copy className="h-4 w-4" />
          Copy
        </Button>
      </div>
      <pre className="overflow-x-auto p-4 text-sm leading-relaxed">
        <code className="font-mono text-neutral-800">{formattedJson}</code>
      </pre>
    </div>
  )
}
