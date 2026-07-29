import { AuthLayout } from '@/layouts/AuthLayout'
import { GuestRoute } from '@/components/auth/GuestRoute'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { RegisterPage } from '@/features/auth/pages/RegisterPage'

export const authRoutes = {
  element: <GuestRoute />,
  children: [
    {
      element: <AuthLayout />,
      children: [
        { path: 'login', element: <LoginPage /> },
        { path: 'register', element: <RegisterPage /> },
      ],
    },
  ],
}
