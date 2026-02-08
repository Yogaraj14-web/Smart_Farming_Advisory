import { useState, useEffect } from 'react'
import { getHistory } from '../services/api'

/**
 * History Component
 *
 * Displays a table of past predictions fetched from the database.
 *
 * Calls: GET /history?user_id=1&limit=10
 */
function History({ refreshTrigger = 0 }) {
  // State
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [userId, setUserId] = useState('1')

  /**
   * Fetch history data from API
   */
  const fetchHistory = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await getHistory({
        user_id: parseInt(userId) || 1,
        limit: 10
      })

      setHistory(response.predictions || [])
    } catch (err) {
      setError(err.message)
      setHistory([])
    } finally {
      setLoading(false)
    }
  }

  /**
   * Fetch on mount and when refreshTrigger changes
   */
  useEffect(() => {
    fetchHistory()
  }, [refreshTrigger])

  /**
   * Handle user ID change
   */
  const handleUserIdChange = (e) => {
    setUserId(e.target.value)
  }

  /**
   * Handle refresh button click
   */
  const handleRefresh = () => {
    fetchHistory()
  }

  /**
   * Format date for display
   */
  const formatDate = (dateString) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  /**
   * Get confidence class for styling
   */
  const getConfidenceClass = (confidence) => {
    if (confidence >= 0.8) return 'high'
    if (confidence >= 0.5) return 'medium'
    return 'low'
  }

  return (
    <div>
      <h2>📋 Prediction History</h2>

      {/* User ID filter and refresh */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <div className="form-group" style={{ marginBottom: 0 }}>
          <label htmlFor="history_user_id">User ID</label>
          <input
            type="number"
            id="history_user_id"
            value={userId}
            onChange={handleUserIdChange}
            min="1"
            style={{ width: '100px' }}
          />
        </div>
        <button
          className="btn btn-secondary"
          onClick={handleRefresh}
          style={{ alignSelf: 'flex-end' }}
        >
          Refresh
        </button>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="loading">
          Loading history...
        </div>
      )}

      {/* Error state */}
      {error && !loading && (
        <div className="result-area error">
          <p className="result-label">Error fetching history</p>
          <p className="result-value">{error}</p>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && history.length === 0 && (
        <div className="empty-state">
          <p>No prediction history found.</p>
          <p>Use the "Submit & Save" form to create records.</p>
        </div>
      )}

      {/* History table */}
      {!loading && !error && history.length > 0 && (
        <table className="history-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>City</th>
              <th>Fertilizer</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {history.map((record, index) => (
              <tr key={record.id || index}>
                <td>{formatDate(record.created_at)}</td>
                <td>
                  {record.weather_temp !== undefined
                    ? `${record.weather_temp}°C`
                    : '-'}
                </td>
                <td>{record.recommendation || '-'}</td>
                <td className={`confidence ${getConfidenceClass(record.confidence_score)}`}>
                  {record.confidence_score
                    ? `${(record.confidence_score * 100).toFixed(1)}%`
                    : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default History
