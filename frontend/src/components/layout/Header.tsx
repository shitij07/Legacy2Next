import { Menu } from 'lucide-react'
import { useUiStore } from '@/stores/uiStore'
import { BreadcrumbNav } from './BreadcrumbNav'
import { ThemeToggle } from './ThemeToggle'

export function Header() {
  const toggleSidebar = useUiStore((s) => s.toggleSidebar)

  return (
    <header className="fixed left-0 right-0 top-0 z-20 flex h-14 items-center gap-4 border-b border-border bg-neutral-100 px-4 lg:left-60">
      <button
        onClick={toggleSidebar}
        className="flex h-8 w-8 items-center justify-center rounded-md text-neutral-600 hover:bg-neutral-200 hover:text-neutral-800 lg:hidden"
        aria-label="Toggle sidebar"
      >
        <Menu className="h-4 w-4" aria-hidden="true" />
      </button>

      <BreadcrumbNav />

      <div className="ml-auto flex items-center gap-2">
        <ThemeToggle />
      </div>
    </header>
  )
}
