import { useLocation, Link } from 'react-router-dom'

const labelMap: Record<string, string> = {
  projects: 'Projects',
  settings: 'Settings',
  analysis: 'Analysis',
}

function segmentToLabel(segment: string): string {
  return labelMap[segment] ?? segment.charAt(0).toUpperCase() + segment.slice(1)
}

export function BreadcrumbNav() {
  const { pathname } = useLocation()
  const segments = pathname.split('/').filter(Boolean)

  if (segments.length === 0) return null

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1 text-sm">
      {segments.map((segment, index) => {
        const href = '/' + segments.slice(0, index + 1).join('/')
        const isLast = index === segments.length - 1
        const label = segmentToLabel(segment)

        return (
          <span key={href} className="flex items-center gap-1">
            {index > 0 && <span className="text-neutral-500">/</span>}
            {isLast ? (
              <span className="text-neutral-800" aria-current="page">
                {label}
              </span>
            ) : (
              <Link to={href} className="text-neutral-600 hover:text-neutral-800">
                {label}
              </Link>
            )}
          </span>
        )
      })}
    </nav>
  )
}
