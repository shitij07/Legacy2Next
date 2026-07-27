import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { cn } from '@/lib/utils'

interface MarkdownRendererProps {
  content: string
  className?: string
}

export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  return (
    <div
      className={cn(
        'prose prose-sm max-w-none dark:prose-invert',
        'prose-headings:text-neutral-900 prose-headings:font-semibold',
        'prose-h1:text-xl prose-h2:text-lg prose-h3:text-base',
        'prose-p:text-neutral-700 prose-p:leading-relaxed',
        'prose-a:text-primary-500 prose-a:no-underline hover:prose-a:underline',
        'prose-strong:text-neutral-900',
        'prose-code:rounded prose-code:bg-neutral-100 prose-code:px-1.5 prose-code:py-0.5 prose-code:text-sm prose-code:font-mono prose-code:text-neutral-800',
        'prose-pre:rounded-lg prose-pre:bg-neutral-100 prose-pre:border prose-pre:border-border',
        'prose-li:text-neutral-700',
        'prose-blockquote:border-l-2 prose-blockquote:border-primary-500 prose-blockquote:pl-4 prose-blockquote:text-neutral-600',
        'prose-hr:border-border',
        className,
      )}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {content}
      </ReactMarkdown>
    </div>
  )
}
