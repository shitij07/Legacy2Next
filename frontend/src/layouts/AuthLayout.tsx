import { Outlet } from 'react-router-dom'

export function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-neutral-50 px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="text-xl font-semibold text-neutral-900">Legacy2Next</h1>
          <p className="mt-1 text-sm text-neutral-600">
            AI-Assisted Legacy Software Intelligence
          </p>
        </div>
        <Outlet />
      </div>
    </div>
  )
}
