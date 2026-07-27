import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@/index.css'
import '@/styles/globals.css'
import { useUiStore } from '@/stores/uiStore'
import { App } from '@/App'

const theme = useUiStore.getState().theme
if (theme === 'dark') {
  document.documentElement.classList.add('dark')
} else {
  document.documentElement.classList.remove('dark')
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
