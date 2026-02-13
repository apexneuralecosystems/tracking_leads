import { Routes, Route, Link } from 'react-router-dom'
import LeadsList from './pages/LeadsList'
import CreateLead from './pages/CreateLead'
import LeadDetail from './pages/LeadDetail'

function App() {
  return (
    <>
      <header className="app-header">
        <div className="container">
          <Link to="/" className="link" style={{ fontSize: 24, fontWeight: 600 }}>
            ApexNeural — Lead Tracking
          </Link>
          <nav>
            <Link to="/" className="nav-link">Leads</Link>
            <Link to="/create" className="nav-link">Create Lead</Link>
          </nav>
        </div>
      </header>
      <main className="container" style={{ paddingTop: 32, paddingBottom: 64 }}>
        <Routes>
          <Route path="/" element={<LeadsList />} />
          <Route path="/create" element={<CreateLead />} />
          <Route path="/leads/:id" element={<LeadDetail />} />
        </Routes>
      </main>
    </>
  )
}

export default App
