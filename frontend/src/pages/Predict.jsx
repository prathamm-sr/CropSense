import React, { useState } from 'react'
import { predictCrop } from '../api/client'

"fields"
const FIELDS = [
  { key: 'N',           label: 'Nitrogen (N)',     unit: 'kg/ha', min: 0,   max: 140, step: 1,   default: 90,    desc: 'Ratio of Nitrogen content in soil' },
  { key: 'P',           label: 'Phosphorous (P)',  unit: 'kg/ha', min: 5,   max: 145, step: 1,   default: 42,    desc: 'Ratio of Phosphorous content in soil' },
  { key: 'K',           label: 'Potassium (K)',    unit: 'kg/ha', min: 5,   max: 205, step: 1,   default: 43,    desc: 'Ratio of Potassium content in soil' },
  { key: 'temperature', label: 'Temperature',      unit: '°C',    min: 8,   max: 44,  step: 0.1, default: 20.87, desc: 'Ambient temperature' },
  { key: 'humidity',    label: 'Humidity',         unit: '%',     min: 14,  max: 100, step: 0.1, default: 82.0,  desc: 'Relative humidity' },
  { key: 'ph',          label: 'Soil pH',          unit: 'pH',    min: 3.5, max: 9.5, step: 0.1, default: 6.5,   desc: 'Acidity / alkalinity of soil' },
  { key: 'rainfall',    label: 'Rainfall',         unit: 'mm',    min: 20,  max: 300, step: 1,   default: 202.9, desc: 'Annual rainfall' },
]

const CROP_EMOJI = {
  rice: '🌾', maize: '🌽', chickpea: '🫘', kidneybeans: '🫘', pigeonpeas: '🌿',
  mothbeans: '🌱', mungbean: '🌱', blackgram: '🫘', lentil: '🫘', pomegranate: '🍈',
  banana: '🍌', mango: '🥭', grapes: '🍇', watermelon: '🍉', muskmelon: '🍈',
  apple: '🍎', orange: '🍊', papaya: '🍈', coconut: '🥥', cotton: '☁️',
  jute: '🌿', coffee: '☕',
}

export default function Predict() {
  const [values, setValues] = useState(
    Object.fromEntries(FIELDS.map(f => [f.key, f.default]))
  )
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleChange = (key, val) => {
    setValues(v => ({ ...v, [key]: parseFloat(val) }))
  }

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await predictCrop(values)
      setResult(data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to connect to backend. Is it running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '40px 48px', maxWidth: 900 }}>
      {/* Header */}
      <div className="fade-up" style={{ marginBottom: 40 }}>
        <h1 style={{ fontSize: 36, color: 'var(--soil)', marginBottom: 8 }}>
          Crop Recommendation
        </h1>
        <p style={{ color: 'var(--text-light)', fontSize: 15 }}>
          Enter your soil and climate parameters to get an AI-powered crop recommendation.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 40 }}>
        {/* Input form */}
        <div className="fade-up delay-1">
          <div style={{
            background: 'white',
            borderRadius: 'var(--radius-lg)',
            padding: 28,
            boxShadow: 'var(--shadow-md)',
            border: '1px solid var(--sand)',
          }}>
            <h2 style={{ fontSize: 16, fontFamily: 'DM Sans', fontWeight: 500, color: 'var(--moss)', marginBottom: 24, letterSpacing: '0.5px', textTransform: 'uppercase'}}>
              Soil & Climate Parameters
            </h2>

            {FIELDS.map((field, i) => (
              <div key={field.key} style={{ marginBottom: 20 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <label style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-mid)' }}>
                    {field.label}
                  </label>
                  <span style={{
                    fontSize: 13,
                    fontWeight: 600,
                    color: 'var(--leaf)',
                    background: 'rgba(93,138,60,0.1)',
                    padding: '1px 8px',
                    borderRadius: 20,
                  }}>
                    {values[field.key]} {field.unit}
                  </span>
                </div>
                <input
                  type="range"
                  min={field.min}
                  max={field.max}
                  step={field.step}
                  value={values[field.key]}
                  onChange={e => handleChange(field.key, e.target.value)}
                  style={{
                    width: '100%',
                    accentColor: 'var(--leaf)',
                    cursor: 'pointer',
                  }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-light)', marginTop: 2 }}>
                  <span>{field.min}</span>
                  <span style={{ fontSize: 10, color: 'var(--text-light)', fontStyle: 'italic' }}>{field.desc}</span>
                  <span>{field.max}</span>
                </div>
              </div>
            ))}

            <button
              onClick={handleSubmit}
              disabled={loading}
              style={{
                width: '100%',
                marginTop: 8,
                padding: '14px',
                borderRadius: 'var(--radius)',
                background: loading ? 'var(--sand)' : 'var(--moss)',
                color: loading ? 'var(--text-light)' : 'white',
                fontSize: 15,
                fontWeight: 500,
                transition: 'all var(--transition)',
                transform: loading ? 'none' : 'translateY(0)',
                letterSpacing: '0.3px',
              }}
              onMouseEnter={e => { if (!loading) e.target.style.background = 'var(--leaf)' }}
              onMouseLeave={e => { if (!loading) e.target.style.background = 'var(--moss)' }}
            >
              {loading ? '⏳ Analysing soil...' : '🌱 Recommend Crop'}
            </button>
          </div>
        </div>

        {/* Result panel */}
        <div className="fade-up delay-2" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {error && (
            <div style={{
              background: '#FFF5F5',
              border: '1px solid #FED7D7',
              borderRadius: 'var(--radius)',
              padding: '16px 20px',
              color: '#C53030',
              fontSize: 14,
            }}>
              ⚠️ {error}
            </div>
          )}

          {!result && !loading && !error && (
            <div style={{
              background: 'white',
              borderRadius: 'var(--radius-lg)',
              padding: 40,
              boxShadow: 'var(--shadow-sm)',
              border: '1px solid var(--sand)',
              textAlign: 'center',
              color: 'var(--text-light)',
            }}>
              <div style={{ fontSize: 48, marginBottom: 16 }}>🌍</div>
              <p style={{ fontSize: 14 }}>Adjust parameters and click<br /><strong>Recommend Crop</strong> to see results.</p>
            </div>
          )}

          {loading && (
            <div style={{
              background: 'white',
              borderRadius: 'var(--radius-lg)',
              padding: 40,
              boxShadow: 'var(--shadow-sm)',
              border: '1px solid var(--sand)',
              textAlign: 'center',
            }}>
              <div style={{ fontSize: 40, animation: 'spin 1s linear infinite', display: 'inline-block', marginBottom: 16 }}>⚙️</div>
              <p style={{ color: 'var(--text-light)', fontSize: 14 }}>Running ML inference...</p>
            </div>
          )}

          {result && (
            <>
              {/* Top result card */}
              <div className="fade-up" style={{
                background: 'linear-gradient(135deg, var(--moss) 0%, var(--leaf) 100%)',
                borderRadius: 'var(--radius-lg)',
                padding: '28px 32px',
                color: 'white',
                boxShadow: 'var(--shadow-lg)',
                position: 'relative',
                overflow: 'hidden',
              }}>
                <div style={{
                  position: 'absolute', top: -20, right: -20,
                  fontSize: 100, opacity: 0.1, lineHeight: 1,
                }}>
                  {CROP_EMOJI[result.top_crop] || '🌿'}
                </div>
                <div style={{ fontSize: 11, letterSpacing: '2px', textTransform: 'uppercase', opacity: 0.8, marginBottom: 8 }}>
                  Top Recommendation
                </div>
                <div style={{ fontSize: 42, marginBottom: 4 }}>
                  {CROP_EMOJI[result.top_crop] || '🌿'}
                </div>
                <h2 style={{
                  fontSize: 30,
                  fontFamily: 'Playfair Display, serif',
                  textTransform: 'capitalize',
                  marginBottom: 8,
                }}>
                  {result.top_crop}
                </h2>
                <div style={{ fontSize: 14, opacity: 0.9 }}>
                  Confidence: <strong>{(result.confidence * 100).toFixed(1)}%</strong>
                  &nbsp;&nbsp;·&nbsp;&nbsp;Model: {result.model_used}
                </div>
              </div>

              {/* Top-k breakdown */}
              <div style={{
                background: 'white',
                borderRadius: 'var(--radius-lg)',
                padding: '24px 28px',
                boxShadow: 'var(--shadow-sm)',
                border: '1px solid var(--sand)',
              }}>
                <h3 style={{ fontSize: 12, letterSpacing: '1.5px', textTransform: 'uppercase', color: 'var(--text-light)', marginBottom: 16 }}>
                  All Candidates
                </h3>
                {result.top_k.map((item, i) => (
                  <div key={i} style={{ marginBottom: i < result.top_k.length - 1 ? 12 : 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span style={{ fontSize: 13, fontWeight: i === 0 ? 600 : 400, color: i === 0 ? 'var(--moss)' : 'var(--text-mid)', textTransform: 'capitalize', display: 'flex', alignItems: 'center', gap: 6 }}>
                        {CROP_EMOJI[item.crop] || '🌿'} {item.crop}
                      </span>
                      <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-mid)' }}>
                        {(item.probability * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div style={{ height: 6, background: 'var(--sand)', borderRadius: 3, overflow: 'hidden' }}>
                      <div style={{
                        height: '100%',
                        width: `${item.probability * 100}%`,
                        background: i === 0
                          ? 'linear-gradient(90deg, var(--moss), var(--sprout))'
                          : 'var(--sand)',
                        borderRadius: 3,
                        transition: 'width 0.8s cubic-bezier(0.4,0,0.2,1)',
                        backgroundImage: i === 0
                          ? 'linear-gradient(90deg, var(--moss), var(--sprout))'
                          : `linear-gradient(90deg, var(--text-light), var(--sand))`,
                      }} />
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}