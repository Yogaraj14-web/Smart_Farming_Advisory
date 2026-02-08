import { useState } from 'react'
import PredictForm from './components/PredictForm'
import SubmitForm from './components/SubmitForm'
import History from './components/History'
import './App.css'

/**
 * Main App Component
 *
 * This is the main container for the Smart Farming Advisory System frontend.
 * It manages the overall layout and passes data between components.
 */
function App() {
  // State to trigger history refresh when new data is submitted
  const [refreshHistory, setRefreshHistory] = useState(0)

  // Callback to refresh history after submission
  const handleSubmissionSuccess = () => {
    setRefreshHistory(prev => prev + 1)
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🌾 Smart Farming Advisory System</h1>
        <p>AI-powered fertilizer recommendations based on soil and weather data</p>
      </header>

      <main className="main-content">
        <div className="forms-section">
          <div className="form-card">
            <PredictForm />
          </div>

          <div className="form-card">
            <SubmitForm onSuccess={handleSubmissionSuccess} />
          </div>
        </div>

        <div className="history-section">
          <History refreshTrigger={refreshHistory} />
        </div>
      </main>

      <footer className="footer">
        <p>Smart Farming Advisory System © 2024</p>
        <p className="api-status">API: http://localhost:5000</p>
      </footer>
    </div>
  )
}

export default App
