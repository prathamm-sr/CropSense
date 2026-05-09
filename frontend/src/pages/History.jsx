import React, { useState, useEffect } from 'react'
import { getHistory, deletePrediction } from '../api/client'

"emojis"
const CROP_EMOJI = {
  rice:'🌾',maize:'🌽',chickpea:'🫘',kidneybeans:'🫘',pigeonpeas:'🌿',
  mothbeans:'🌱',mungbean:'🌱',blackgram:'🫘',lentil:'🫘',pomegranate:'🍈',
  banana:'🍌',mango:'🥭',grapes:'🍇',watermelon:'🍉',muskmelon:'🍈',
  apple:'🍎',orange:'🍊',papaya:'🍈',coconut:'🥥',cotton:'☁️',jute:'🌿',coffee:'☕',
}

function ConfidenceBadge({ value }) {
  const pct = (value * 100).toFixed(1)
  const color = value > 0.8 ? 'var(--leaf)' : value > 0.5 ? 'var(--gold)' : 'var(--rust)'
  return (
    <span style={{
      fontSize: 12, fontWeight: 600, color,
      background: `${color}18`,
      padding: '2px 10px', borderRadius: 20,
    }}>
      {pct}%
    </span>
  )
}

export default function History() {
  const [data, setData] = useState(null)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [cropFilter, setCropFilter] = useState('')
  const [deleting, setDeleting] = useState(null)

  const PAGE_SIZE = 15

  const load = async () => {
    setLoading(true)
    try {
      const res = await getHistory(page, PAGE_SIZE, cropFilter || null)
      setData(res)
    } catch (e) {
      setError('Failed to load history.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [page, cropFilter])

  const handleDelete = async (id) => {
    setDeleting(id)
    try {
      await deletePrediction(id)
      load()
    } catch (e) {
      alert('Delete failed.')
    } finally {
      setDeleting(null)
    }
  }

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 1

  return (
    <div style={{ padding: '40px 48px' }}>
      <div className="fade-up" style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 36, color: 'var(--soil)', marginBottom: 8 }}>Prediction History</h1>
        <p style={{ color: 'var(--text-light)', fontSize: 15 }}>
          All past predictions logged to PostgreSQL.
        </p>
      </div>

      {/* Filter bar */}
      <div className="fade-up delay-1" style={{ display: 'flex', gap: 12, marginBottom: 24, alignItems: 'center' }}>
        <input
          placeholder="Filter by crop name..."
          value={cropFilter}
          onChange={e => { setCropFilter(e.target.value); setPage(1) }}
          style={{
            padding: '10px 16px',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--sand)',
            fontSize: 14,
            width: 220,
            outline: 'none',
            background: 'white',
            color: 'var(--text-dark)',
          }}
        />
        {cropFilter && (
          <button
            onClick={() => { setCropFilter(''); setPage(1) }}
            style={{ padding: '10px 16px', borderRadius: 'var(--radius)', background: 'var(--sand)', fontSize: 13, color: 'var(--text-mid)' }}
          >
            Clear
          </button>
        )}
        {data && (
          <span style={{ marginLeft: 'auto', fontSize: 13, color: 'var(--text-light)' }}>
            {data.total} total records
          </span>
        )}
      </div>

      {/* Table */}
      <div className="fade-up delay-2" style={{
        background: 'white',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-md)',
        border: '1px solid var(--sand)',
        overflow: 'hidden',
      }}>
        {/* Table header */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '2fr 1fr 1fr 1fr 1fr 1fr 1fr 60px',
          padding: '12px 20px',
          background: 'var(--mist)',
          borderBottom: '1px solid var(--sand)',
          fontSize: 11,
          letterSpacing: '1.2px',
          textTransform: 'uppercase',
          color: 'var(--text-light)',
          fontWeight: 500,
        }}>
          <span>Crop</span>
          <span>N</span><span>P</span><span>K</span>
          <span>Temp</span>
          <span>Confidence</span>
          <span>Date</span>
          <span></span>
        </div>

        {loading && (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-light)' }}>
            Loading...
          </div>
        )}

        {error && (
          <div style={{ padding: 20, color: 'var(--rust)', textAlign: 'center' }}>{error}</div>
        )}

        {!loading && data?.items.length === 0 && (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-light)' }}>
            No predictions yet. Go to <strong>Predict</strong> to make your first one.
          </div>
        )}

        {!loading && data?.items.map((item, i) => (
          <div
            key={item.id}
            style={{
              display: 'grid',
              gridTemplateColumns: '2fr 1fr 1fr 1fr 1fr 1fr 1fr 60px',
              padding: '13px 20px',
              borderBottom: i < data.items.length - 1 ? '1px solid var(--sand)' : 'none',
              alignItems: 'center',
              transition: 'background var(--transition)',
              fontSize: 13,
            }}
            onMouseEnter={e => e.currentTarget.style.background = 'var(--cream)'}
            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
          >
            <span style={{ fontWeight: 500, textTransform: 'capitalize', display: 'flex', alignItems: 'center', gap: 6 }}>
              {CROP_EMOJI[item.top_crop] || '🌿'} {item.top_crop}
            </span>
            <span style={{ color: 'var(--text-mid)' }}>{item.input_features.N}</span>
            <span style={{ color: 'var(--text-mid)' }}>{item.input_features.P}</span>
            <span style={{ color: 'var(--text-mid)' }}>{item.input_features.K}</span>
            <span style={{ color: 'var(--text-mid)' }}>{item.input_features.temperature}°C</span>
            <ConfidenceBadge value={item.confidence} />
            <span style={{ color: 'var(--text-light)', fontSize: 12 }}>
              {new Date(item.created_at).toLocaleDateString()}
            </span>
            <button
              onClick={() => handleDelete(item.id)}
              disabled={deleting === item.id}
              style={{
                background: 'none',
                color: deleting === item.id ? 'var(--sand)' : 'var(--text-light)',
                fontSize: 14,
                padding: '4px 8px',
                borderRadius: 6,
                transition: 'color var(--transition)',
              }}
              onMouseEnter={e => e.target.style.color = 'var(--rust)'}
              onMouseLeave={e => e.target.style.color = 'var(--text-light)'}
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', gap: 8, marginTop: 20, justifyContent: 'center' }}>
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            style={{
              padding: '8px 16px', borderRadius: 8,
              background: page === 1 ? 'var(--sand)' : 'var(--moss)',
              color: page === 1 ? 'var(--text-light)' : 'white',
              fontSize: 13,
            }}
          >← Prev</button>
          <span style={{ padding: '8px 16px', fontSize: 13, color: 'var(--text-mid)' }}>
            {page} / {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            style={{
              padding: '8px 16px', borderRadius: 8,
              background: page === totalPages ? 'var(--sand)' : 'var(--moss)',
              color: page === totalPages ? 'var(--text-light)' : 'white',
              fontSize: 13,
            }}
          >Next →</button>
        </div>
      )}
    </div>
  )
}