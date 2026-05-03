import React, { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import { getStats } from '../api/client'

const COLORS = ['#3D5A2E','#5C8A3C','#7DB55A','#C8A84B','#A0522D','#6B8E6B','#8FBC8F','#4A7C59','#2E5B3D','#9CB08A']

function StatCard({ label, value, sub, icon }) {
  return (
    <div style={{
      background: 'white',
      borderRadius: 'var(--radius-lg)',
      padding: '24px 28px',
      boxShadow: 'var(--shadow-sm)',
      border: '1px solid var(--sand)',
    }}>
      <div style={{ fontSize: 28, marginBottom: 10 }}>{icon}</div>
      <div style={{ fontSize: 32, fontFamily: 'Playfair Display, serif', fontWeight: 700, color: 'var(--soil)', lineHeight: 1 }}>
        {value}
      </div>
      <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-mid)', marginTop: 6 }}>{label}</div>
      {sub && <div style={{ fontSize: 11, color: 'var(--text-light)', marginTop: 3 }}>{sub}</div>}
    </div>
  )
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: 'white', border: '1px solid var(--sand)',
      borderRadius: 10, padding: '10px 14px',
      boxShadow: 'var(--shadow-md)', fontSize: 13,
    }}>
      <div style={{ fontWeight: 600, textTransform: 'capitalize', marginBottom: 2 }}>{payload[0].payload.crop}</div>
      <div style={{ color: 'var(--leaf)' }}>{payload[0].value} predictions</div>
    </div>
  )
}

export default function Stats() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch(() => setError('Failed to load stats.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div style={{ padding: '40px 48px', color: 'var(--text-light)' }}>Loading stats...</div>
  )
  if (error) return (
    <div style={{ padding: '40px 48px', color: 'var(--rust)' }}>{error}</div>
  )

  const pieData = stats.top_crops.slice(0, 6).map(c => ({ name: c.crop, value: c.count }))

  return (
    <div style={{ padding: '40px 48px' }}>
      <div className="fade-up" style={{ marginBottom: 36 }}>
        <h1 style={{ fontSize: 36, color: 'var(--soil)', marginBottom: 8 }}>Statistics</h1>
        <p style={{ color: 'var(--text-light)', fontSize: 15 }}>Aggregate analytics across all predictions.</p>
      </div>

      {/* Stat cards */}
      <div className="fade-up delay-1" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20, marginBottom: 36 }}>
        <StatCard
          icon="🌾" label="Total Predictions"
          value={stats.total_predictions.toLocaleString()}
          sub="Logged to PostgreSQL"
        />
        <StatCard
          icon="🎯" label="Avg Confidence"
          value={`${(stats.avg_confidence * 100).toFixed(1)}%`}
          sub="Across all predictions"
        />
        <StatCard
          icon="🌿" label="Unique Crops"
          value={stats.top_crops.length}
          sub="Distinct crops recommended"
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: 24 }}>
        {/* Bar chart */}
        <div className="fade-up delay-2" style={{
          background: 'white',
          borderRadius: 'var(--radius-lg)',
          padding: '28px 24px',
          boxShadow: 'var(--shadow-sm)',
          border: '1px solid var(--sand)',
        }}>
          <h3 style={{ fontSize: 14, fontFamily: 'DM Sans', fontWeight: 500, color: 'var(--text-mid)', marginBottom: 24, letterSpacing: '0.5px' }}>
            Top Crops by Prediction Count
          </h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={stats.top_crops} margin={{ top: 0, right: 0, left: -20, bottom: 40 }}>
              <XAxis
                dataKey="crop"
                tick={{ fontSize: 11, fill: 'var(--text-light)' }}
                angle={-35}
                textAnchor="end"
                interval={0}
              />
              <YAxis tick={{ fontSize: 11, fill: 'var(--text-light)' }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                {stats.top_crops.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie chart */}
        <div className="fade-up delay-3" style={{
          background: 'white',
          borderRadius: 'var(--radius-lg)',
          padding: '28px 24px',
          boxShadow: 'var(--shadow-sm)',
          border: '1px solid var(--sand)',
        }}>
          <h3 style={{ fontSize: 14, fontFamily: 'DM Sans', fontWeight: 500, color: 'var(--text-mid)', marginBottom: 24 }}>
            Distribution (Top 6)
          </h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%" cy="45%"
                innerRadius={55} outerRadius={90}
                paddingAngle={3}
                dataKey="value"
              >
                {pieData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i]} />
                ))}
              </Pie>
              <Tooltip formatter={(v, n) => [v, n]} />
              <Legend
                formatter={v => <span style={{ fontSize: 11, textTransform: 'capitalize', color: 'var(--text-mid)' }}>{v}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Full top crops table */}
      <div className="fade-up delay-4" style={{
        marginTop: 24,
        background: 'white',
        borderRadius: 'var(--radius-lg)',
        padding: '24px 28px',
        boxShadow: 'var(--shadow-sm)',
        border: '1px solid var(--sand)',
      }}>
        <h3 style={{ fontSize: 14, fontFamily: 'DM Sans', fontWeight: 500, color: 'var(--text-mid)', marginBottom: 20 }}>
          All Crops Ranking
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 12 }}>
          {stats.top_crops.map((c, i) => (
            <div key={c.crop} style={{
              display: 'flex', alignItems: 'center', gap: 10,
              padding: '10px 14px',
              borderRadius: 10,
              background: 'var(--cream)',
              border: '1px solid var(--sand)',
            }}>
              <span style={{
                width: 24, height: 24, borderRadius: '50%',
                background: COLORS[i % COLORS.length],
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 10, fontWeight: 700, color: 'white', flexShrink: 0,
              }}>
                {i + 1}
              </span>
              <span style={{ fontSize: 13, textTransform: 'capitalize', fontWeight: 500, color: 'var(--text-mid)' }}>
                {c.crop}
              </span>
              <span style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--text-light)' }}>
                {c.count}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}