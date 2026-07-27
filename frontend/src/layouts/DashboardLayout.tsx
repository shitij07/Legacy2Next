import { Outlet } from 'react-router-dom'
import { Sidebar } from '@/components/layout/Sidebar'
import { Header } from '@/components/layout/Header'

export function DashboardLayout() {
  return (
    <div className="min-h-screen bg-neutral-50">
      <Header />
      <Sidebar />

      <main className="pt-14 lg:ml-60">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
