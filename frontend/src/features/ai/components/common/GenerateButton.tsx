import { Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface GenerateButtonProps {
  onClick: () => void
  isLoading: boolean
  label?: string
}

export function GenerateButton({ onClick, isLoading, label = 'Generate' }: GenerateButtonProps) {
  return (
    <Button
      onClick={onClick}
      isLoading={isLoading}
      disabled={isLoading}
      aria-label={isLoading ? 'Generating...' : label}
    >
      <Sparkles className="h-4 w-4" aria-hidden="true" />
      {label}
    </Button>
  )
}
