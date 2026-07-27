import { createBrowserRouter, Navigate } from 'react-router-dom'
import { authRoutes } from './auth.routes'
import { projectsRoutes } from './projects.routes'
import { settingsRoutes } from './settings.routes'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/projects" replace />,
  },
  authRoutes,
  projectsRoutes,
  settingsRoutes,
  {
    path: '*',
    lazy: () => import('@/features/NotFoundPage').then((m) => ({ Component: m.NotFoundPage })),
  },
])
