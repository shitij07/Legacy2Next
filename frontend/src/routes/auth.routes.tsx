import { AuthLayout } from '@/layouts/AuthLayout'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { RegisterPage } from '@/features/auth/pages/RegisterPage'

export const authRoutes = {
  element: <AuthLayout />,
  children: [
    { path: 'login', element: <LoginPage /> },
    { path: 'register', element: <RegisterPage /> },
  ],
}
