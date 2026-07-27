import { useNavigate } from 'react-router-dom'

export function NotFoundPage() {
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen items-center justify-center bg-neutral-50 p-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-neutral-900">404</h1>
        <p className="mt-2 text-sm text-neutral-600">Page not found.</p>
        <button
          onClick={() => navigate('/projects')}
          className="mt-4 rounded-md bg-primary-500 px-4 py-2 text-sm font-medium text-white hover:bg-primary-600"
        >
          Back to Projects
        </button>
      </div>
    </div>
  )
}
