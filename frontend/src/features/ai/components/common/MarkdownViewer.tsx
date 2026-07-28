import { MarkdownRenderer } from '@/components/shared/MarkdownRenderer'

interface MarkdownViewerProps {
  content: string
}

export function MarkdownViewer({ content }: MarkdownViewerProps) {
  return <MarkdownRenderer content={content} />
}
