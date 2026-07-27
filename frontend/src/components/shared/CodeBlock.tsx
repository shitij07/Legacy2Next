import { useState } from 'react'
import { Copy, Check } from 'lucide-react'
import { cn } from '@/lib/utils'

interface CodeBlockProps {
  code: string
  language?: string
  className?: string
}

export function CodeBlock({ code, language, className }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={cn('group relative rounded-lg border border-border bg-neutral-100', className)}>
      {language && (
        <div className="flex items-center justify-between border-b border-border px-4 py-2">
          <span className="text-xs font-medium text-neutral-600">{language}</span>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 text-xs text-neutral-500 hover:text-neutral-700"
            aria-label={copied ? 'Copied' : 'Copy code'}
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-success" aria-hidden="true" />
                Copied
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5" aria-hidden="true" />
                Copy
              </>
            )}
          </button>
        </div>
      )}
      <pre className="overflow-x-auto p-4">
        <code className="font-mono text-sm leading-relaxed text-neutral-800">{code}</code>
      </pre>
    </div>
  )
}
