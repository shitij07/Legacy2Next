import { RouterProvider } from 'react-router-dom'
import { RootLayout } from '@/layouts/RootLayout'
import { AuthInitializer } from '@/components/auth/AuthInitializer'
import { router } from '@/routes'

export function App() {
  return (
    <RootLayout>
      <AuthInitializer>
        <RouterProvider router={router} />
      </AuthInitializer>
    </RootLayout>
  )
}
