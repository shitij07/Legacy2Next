import { DashboardLayout } from '@/layouts/DashboardLayout'
import { SettingsPage } from '@/features/settings/pages/SettingsPage'

export const settingsRoutes = {
  element: <DashboardLayout />,
  children: [
    { path: 'settings', element: <SettingsPage /> },
  ],
}
