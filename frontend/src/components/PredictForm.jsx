import { useState } from 'react'
import { predictFertilizer } from '../services/api'

/**
 * PredictForm Component
 *
 * This form allows users to input soil and location data
 * to get fertilizer recommendations without saving to database.
 *
 * Calls: POST /predict
 */
function PredictForm() {
  // Form state
  const [formData, setFormData] = useState({
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    leaf_color: '1',
    city: ''
  })

  // UI state
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  // Leaf color options for dropdown
  const leafColorOptions = [
    { value: '0', label: '0 - Yellow (severe nitrogen deficiency)' },
    { value: '1', label: '1 - Pale Green (moderate deficiency)' },
    { value: '2', label: '2 - Light Green (slight deficiency)' },
    { value: '3', label: '3 - Medium Green (healthy)' },
    { value: '4', label: '4 - Dark Green (good)' },
    { value: '5', label: '5 - Dark Green with Spots (possible toxicity)' }
  ]

  /**
   * Handle input changes
   */
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault()

    // Validate required fields
    if (!formData.nitrogen || !formData.phosphorus ||
        !formData.potassium || !formData.city) {
      setError('Please fill in all required fields')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      // Call the prediction API
      const response = await predictFertilizer({
        nitrogen: parseFloat(formData.nitrogen),
        phosphorus: parseFloat(formData.phosphorus),
        potassium: parseFloat(formData.potassium),
        leaf_color: parseInt(formData.leaf_color),
        city: formData.city
      })

      setResult(response)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  /**
   * Clear form and results
   */
  const handleClear = () => {
    setFormData({
      nitrogen: '',
      phosphorus: '',
      potassium: '',
      leaf_color: '1',
      city: ''
    })
    setResult(null)
    setError(null)
  }

  return (
    <div>
      <h2>🔮 Predict Fertilizer</h2>

      <form onSubmit={handleSubmit}>
        {/* Nitrogen Input */}
        <div className="form-group">
          <label htmlFor="nitrogen">Nitrogen (kg/ha) *</label>
          <input
            type="number"
            id="nitrogen"
            name="nitrogen"
            value={formData.nitrogen}
            onChange={handleChange}
            placeholder="e.g., 45.0"
            min="0"
            step="0.1"
            disabled={loading}
            required
          />
        </div>

        {/* Phosphorus Input */}
        <div className="form-group">
          <label htmlFor="phosphorus">Phosphorus (kg/ha) *</label>
          <input
            type="number"
            id="phosphorus"
            name="phosphorus"
            value={formData.phosphorus}
            onChange={handleChange}
            placeholder="e.g., 18.0"
            min="0"
            step="0.1"
            disabled={loading}
            required
          />
        </div>

        {/* Potassium Input */}
        <div className="form-group">
          <label htmlFor="potassium">Potassium (kg/ha) *</label>
          <input
            type="number"
            id="potassium"
            name="potassium"
            value={formData.potassium}
            onChange={handleChange}
            placeholder="e.g., 65.0"
            min="0"
            step="0.1"
            disabled={loading}
            required
          />
        </div>

        {/* Leaf Color Dropdown */}
        <div className="form-group">
          <label htmlFor="leaf_color">Leaf Color *</label>
          <select
            id="leaf_color"
            name="leaf_color"
            value={formData.leaf_color}
            onChange={handleChange}
            disabled={loading}
            required
          >
            {leafColorOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* City Input */}
        <div className="form-group">
          <label htmlFor="city">City *</label>
          <input
            type="text"
            id="city"
            name="city"
            value={formData.city}
            onChange={handleChange}
            placeholder="e.g., Delhi, Mumbai, London"
            disabled={loading}
            required
          />
        </div>

        {/* Buttons */}
        <div>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Processing...' : 'Predict Fertilizer'}
          </button>

          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleClear}
            disabled={loading}
          >
            Clear
          </button>
        </div>
      </form>

      {/* Error Message */}
      {error && (
        <div className="result-area error">
          <p className="result-label">Error</p>
          <p className="result-value">{error}</p>
        </div>
      )}

      {/* Result Display */}
      {result && !error && (
        <div className="result-area">
          <div className="result-item">
            <p className="result-label">Recommended Fertilizer</p>
            <p className="result-value success">{result.recommendation}</p>
          </div>

          <div className="result-item">
            <p className="result-label">Confidence</p>
            <p className="result-value">
              {(result.confidence * 100).toFixed(1)}%
            </p>
          </div>

          {/* Weather Info */}
          <div className="weather-info">
            <div className="weather-item">
              <span className="result-label">Condition:</span>
              <span className="result-value">{result.weather.condition}</span>
            </div>
            <div className="weather-item">
              <span className="result-label">Temperature:</span>
              <span className="result-value">
                {result.weather.temperature_celsius}°C
              </span>
            </div>
            <div className="weather-item">
              <span className="result-label">Humidity:</span>
              <span className="result-value">
                {result.weather.humidity_percent}%
              </span>
            </div>
            <div className="weather-item">
              <span className="result-label">Rain Expected:</span>
              <span className="result-value">
                {result.weather.rain_expected ? 'Yes' : 'No'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PredictForm
