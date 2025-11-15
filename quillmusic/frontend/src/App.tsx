import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'sonner'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import AISongBuilder from './pages/AISongBuilder'
import RenderQueue from './pages/RenderQueue'
import ManualCreator from './pages/ManualCreator'
import InstrumentalStudio from './pages/InstrumentalStudio'

function App() {
  return (
    <div className="dark min-h-screen bg-gray-950">
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/ai-builder" element={<AISongBuilder />} />
          <Route path="/render-queue" element={<RenderQueue />} />
          <Route path="/manual-creator" element={<ManualCreator />} />
          <Route path="/instrumental-studio" element={<InstrumentalStudio />} />
        </Routes>
      </Layout>
      <Toaster />
    </div>
  )
}

export default App
