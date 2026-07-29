import { memo } from 'react'
import { NavLink } from 'react-router-dom'
import { FolderKanban, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUiStore } from '@/stores/uiStore'

const navItems = [
  { to: '/projects', label: 'Projects', icon: FolderKanban },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export const Sidebar = memo(function Sidebar() {
  const sidebarOpen = useUiStore((s) => s.sidebarOpen)
  const toggleSidebar = useUiStore((s) => s.toggleSidebar)

  return (
    <>
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-neutral-950/60 lg:hidden"
          onClick={toggleSidebar}
        />
      )}

      <aside
        className={cn(
          'fixed left-0 top-14 z-40 flex h-[calc(100vh-56px)] w-60 flex-col border-r border-border bg-neutral-100 transition-transform duration-200',
          'lg:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <nav className="flex-1 space-y-1 px-3 py-4">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => {
                if (window.innerWidth < 1024) toggleSidebar()
              }}
              className={({ isActive }) =>
                cn(
                  'flex h-10 items-center gap-2 rounded-md px-3 text-sm font-medium transition-colors',
                  isActive
                    ? 'border-l-2 border-primary-500 bg-primary-500/10 pl-[10px] text-primary-500'
                    : 'text-neutral-700 hover:bg-neutral-200 hover:text-neutral-800',
                )
              }
            >
              <item.icon className="h-5 w-5" aria-hidden="true" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-border px-4 py-3">
          <p className="text-xs text-neutral-500">Legacy2Next v0.1.0</p>
        </div>
      </aside>
    </>
  )
})
