interface PromptHeaderProps {
  title: string
  description?: string
}

export function PromptHeader({ title, description }: PromptHeaderProps) {
  return (
    <div>
      <h3 className="text-base font-semibold text-neutral-900">{title}</h3>
      {description && <p className="mt-1 text-sm text-neutral-600">{description}</p>}
    </div>
  )
}
