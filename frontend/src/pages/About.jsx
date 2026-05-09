import React from 'react'

const STACK = [
  { layer: 'ML Core',       tech: 'scikit-learn · XGBoost · SHAP',          icon: '🧠', color: '#3D5A2E' },
  { layer: 'ML Service',    tech: 'FastAPI · Pydantic · Prometheus',          icon: '⚙️', color: '#5C8A3C' },
  { layer: 'Backend API',   tech: 'FastAPI · SQLAlchemy · asyncpg',           icon: '🔌', color: '#7DB55A' },
  { layer: 'Database',      tech: 'PostgreSQL · Neon · Alembic migrations',   icon: '🗄️', color: '#C8A84B' },
  { layer: 'Frontend',      tech: 'React · Vite · Recharts',                  icon: '🖥️', color: '#A0522D' },
  { layer: 'DevOps',        tech: 'Docker · Docker Compose · GitHub Actions', icon: '🐳', color: '#4A7C59' },
]

"model performance metrics"

const METRICS = [
  { label: 'Accuracy',    value: '~99.3%' },
  { label: 'F1 Macro',    value: '~99.3%' },
  { label: 'ROC-AUC',     value: '~99.9%' },
  { label: 'Crop Classes',value: '22' },
  { label: 'Models Trained', value: '5' },
  { label: 'Eval Metrics', value: '13' },
]

export default function About() {
  return (
    <div style={{ padding: '40px 48px', maxWidth: 820 }}>
      <div className="fade-up" style={{ marginBottom: 40 }}>
        <h1 style={{ fontSize: 36, color: 'var(--soil)', marginBottom: 8 }}>About CropSense</h1>
        <p style={{ color: 'var(--text-light)', fontSize: 15, lineHeight: 1.7 }}>
          An end-to-end precision agriculture system combining machine learning, 
          microservice architecture, and modern DevOps practices.
        </p>
      </div>

      {/* Hero description */}
      <div className="fade-up delay-1" style={{
        background: 'linear-gradient(135deg, var(--soil) 0%, var(--moss) 100%)',
        borderRadius: 'var(--radius-lg)',
        padding: '32px 36px',
        color: 'white',
        marginBottom: 32,
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{ position: 'absolute', right: 20, top: 20, fontSize: 80, opacity: 0.08 }}>🌾</div>
        <h2 style={{ fontSize: 22, marginBottom: 12 }}>What does it do?</h2>
        <p style={{ opacity: 0.88, lineHeight: 1.75, fontSize: 14, maxWidth: 580 }}>
          Given seven soil and climate parameters — Nitrogen, Phosphorous, Potassium, 
          temperature, humidity, pH, and rainfall — CropSense predicts the optimal crop 
          to grow from 22 possibilities. Every prediction is logged to a cloud PostgreSQL 
          database with full history and analytics.
        </p>
      </div>

      {/* ML Metrics */}
      <div className="fade-up delay-2" style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, color: 'var(--soil)', marginBottom: 16 }}>Model Performance</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
          {METRICS.map(m => (
            <div key={m.label} style={{
              background: 'white',
              borderRadius: 'var(--radius)',
              padding: '18px 20px',
              border: '1px solid var(--sand)',
              boxShadow: 'var(--shadow-sm)',
              textAlign: 'center',
            }}>
              <div style={{ fontSize: 24, fontFamily: 'Playfair Display, serif', fontWeight: 700, color: 'var(--leaf)' }}>
                {m.value}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-light)', marginTop: 4 }}>{m.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Tech stack */}
      <div className="fade-up delay-3" style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, color: 'var(--soil)', marginBottom: 16 }}>Tech Stack</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {STACK.map((s, i) => (
            <div key={s.layer} className={`fade-up delay-${Math.min(i + 1, 5)}`} style={{
              display: 'flex',
              alignItems: 'center',
              gap: 16,
              background: 'white',
              borderRadius: 'var(--radius)',
              padding: '14px 20px',
              border: '1px solid var(--sand)',
              boxShadow: 'var(--shadow-sm)',
            }}>
              <div style={{
                width: 38, height: 38, borderRadius: 10,
                background: `${s.color}18`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 18, flexShrink: 0,
              }}>
                {s.icon}
              </div>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-dark)' }}>{s.layer}</div>
                <div style={{ fontSize: 12, color: 'var(--text-light)', marginTop: 1 }}>{s.tech}</div>
              </div>
              <div style={{
                marginLeft: 'auto',
                width: 8, height: 8, borderRadius: '50%',
                background: s.color,
              }} />
            </div>
          ))}
        </div>
      </div>

      {/* Roadmap */}
      <div className="fade-up delay-4" style={{
        background: 'white',
        borderRadius: 'var(--radius-lg)',
        padding: '24px 28px',
        border: '1px solid var(--sand)',
        boxShadow: 'var(--shadow-sm)',
      }}>
        <h2 style={{ fontSize: 18, color: 'var(--soil)', marginBottom: 16 }}>Project Roadmap</h2>
        {[
          { phase: 'Phase 1', label: 'ML Pipeline',              done: true  },
          { phase: 'Phase 2', label: 'FastAPI ML Microservice',  done: true  },
          { phase: 'Phase 3', label: 'Backend + PostgreSQL',     done: true  },
          { phase: 'Phase 4', label: 'React Frontend',           done: true  },
          { phase: 'Phase 5', label: 'Docker Compose',           done: false },
          { phase: 'Phase 6', label: 'Prometheus + Grafana',     done: false },
          { phase: 'Phase 7', label: 'GitHub Actions CI/CD',     done: false },
          { phase: 'Phase 8', label: 'Cloud Deploy',             done: false },
        ].map(item => (
          <div key={item.phase} style={{
            display: 'flex', alignItems: 'center', gap: 12,
            padding: '8px 0',
            borderBottom: '1px solid var(--sand)',
          }}>
            <span style={{
              fontSize: 14,
              color: item.done ? 'var(--leaf)' : 'var(--sand)',
            }}>
              {item.done ? '✅' : '⬜'}
            </span>
            <span style={{ fontSize: 11, color: 'var(--text-light)', width: 65 }}>{item.phase}</span>
            <span style={{ fontSize: 13, color: item.done ? 'var(--text-dark)' : 'var(--text-light)', fontWeight: item.done ? 500 : 400 }}>
              {item.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}