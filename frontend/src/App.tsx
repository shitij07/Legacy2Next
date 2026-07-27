import { RouterProvider } from 'react-router-dom'
import { RootLayout } from '@/layouts/RootLayout'
import { router } from '@/routes'

export function App() {
  return (
    <RootLayout>
      <RouterProvider router={router} />
    </RootLayout>
  )
}
