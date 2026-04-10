import { useState, useEffect } from 'react';
import { Brain, TrendingUp, Target, BarChart3, Image as ImageIcon, Settings2, ChevronDown, ChevronUp } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const API_URL = 'http://localhost:5000';

const CHART_CONFIGS = [
  { key: 'train/box_loss', label: 'Box Loss', color: '#f43f5e', desc: 'Bounding box regression loss' },
  { key: 'train/cls_loss', label: 'Class Loss', color: '#f59e0b', desc: 'Classification loss' },
  { key: 'metrics/mAP50(B)', label: 'mAP@50', color: '#10b981', desc: 'Mean Average Precision at IoU 0.5' },
  { key: 'metrics/mAP50-95(B)', label: 'mAP@50-95', color: '#6366f1', desc: 'Mean Average Precision at IoU 0.5-0.95' },
  { key: 'metrics/precision(B)', label: 'Precision', color: '#a78bfa', desc: 'Detection precision' },
  { key: 'metrics/recall(B)', label: 'Recall', color: '#38bdf8', desc: 'Detection recall' },
];

const MODEL_IMAGES = [
  { file: 'confusion_matrix.png', label: 'Confusion Matrix', desc: 'Shows how well the model classifies each PPE type' },
  { file: 'BoxPR_curve.png', label: 'Precision-Recall Curve', desc: 'Trade-off between precision and recall' },
  { file: 'BoxF1_curve.png', label: 'F1 Score Curve', desc: 'Harmonic mean of precision and recall' },
  { file: 'results.png', label: 'Training Results', desc: 'All training metrics over epochs' },
  { file: 'val_batch0_pred.jpg', label: 'Sample Predictions', desc: 'Model predictions on validation images' },
  { file: 'confusion_matrix_normalized.png', label: 'Normalized Confusion Matrix', desc: 'Percentage-based confusion matrix' },
];

export default function ModelPerformance() {
  const [metrics, setMetrics] = useState([]);
  const [config, setConfig] = useState(null);
  const [showConfig, setShowConfig] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [loadError, setLoadError] = useState('');

  useEffect(() => {
    const loadData = async () => {
      try {
        console.log('[ModelPerf] Fetching metrics from', `${API_URL}/api/model/metrics`);
        const metricsRes = await fetch(`${API_URL}/api/model/metrics`);
        console.log('[ModelPerf] Metrics status:', metricsRes.status);
        if (metricsRes.ok) {
          const data = await metricsRes.json();
          console.log('[ModelPerf] Metrics rows:', data.length);
          setMetrics(data);
        } else {
          setLoadError(`Metrics API returned ${metricsRes.status}`);
        }
      } catch (e) {
        console.error('[ModelPerf] Fetch error:', e);
        setLoadError(`Fetch failed: ${e.message}`);
      }

      try {
        const configRes = await fetch(`${API_URL}/api/model/config`);
        if (configRes.ok) setConfig(await configRes.json());
      } catch (e) {
        console.error('[ModelPerf] Config fetch error:', e);
      }
    };
    loadData();
  }, []);

  const lastEpoch = metrics.length > 0 ? metrics[metrics.length - 1] : null;

  return (
    <div style={{ animation: 'fadeIn 0.4s ease' }}>
      <div className="top-bar">
        <div>
          <h1>AI Model Performance</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>
            YOLOv8s training analytics — {metrics.length} epochs
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Brain size={20} color="#a78bfa" />
          <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>Custom Trained Model</span>
        </div>
      </div>

      {/* Error Banner */}
      {loadError && (
        <div style={{ background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.2)', borderRadius: '10px', padding: '12px 16px', marginBottom: '1rem', color: '#fb7185', fontSize: '0.85rem', fontWeight: 500 }}>
          ⚠️ {loadError} — Check the browser console (F12) for details.
        </div>
      )}

      {/* Key Metrics Cards */}
      {lastEpoch && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }} className="stats-grid">
          {[
            { label: 'mAP@50', value: `${((lastEpoch['metrics/mAP50(B)'] || 0) * 100).toFixed(1)}%`, color: '#10b981', icon: <Target size={22} /> },
            { label: 'mAP@50-95', value: `${((lastEpoch['metrics/mAP50-95(B)'] || 0) * 100).toFixed(1)}%`, color: '#6366f1', icon: <BarChart3 size={22} /> },
            { label: 'Precision', value: `${((lastEpoch['metrics/precision(B)'] || 0) * 100).toFixed(1)}%`, color: '#a78bfa', icon: <TrendingUp size={22} /> },
            { label: 'Recall', value: `${((lastEpoch['metrics/recall(B)'] || 0) * 100).toFixed(1)}%`, color: '#38bdf8', icon: <TrendingUp size={22} /> },
          ].map((m, i) => (
            <div className="stat-card" key={i} style={{ animationDelay: `${i * 0.1}s` }}>
              <div className="stat-icon" style={{ background: `linear-gradient(135deg, ${m.color}22, ${m.color}08)` }}>
                {m.icon}
              </div>
              <div>
                <div className="stat-value" style={{ color: m.color }}>{m.value}</div>
                <div className="stat-label">{m.label}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Training Curves */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }} className="charts-grid">
        {CHART_CONFIGS.map(chart => (
          <div className="card" key={chart.key}>
            <div className="card-header">
              <div className="card-title" style={{ fontSize: '0.85rem' }}>
                <div style={{ width: '10px', height: '10px', borderRadius: '3px', background: chart.color }} />
                {chart.label}
              </div>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: '10px' }}>{chart.desc}</p>
            <div style={{ width: '100%', height: 180 }}>
              {metrics.length > 0 ? (
                <ResponsiveContainer>
                  <LineChart data={metrics}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.07)" />
                    <XAxis dataKey="epoch" stroke="var(--text-muted)" tick={{ fontSize: 10 }} />
                    <YAxis stroke="var(--text-muted)" tick={{ fontSize: 10 }} />
                    <Tooltip
                      contentStyle={{ backgroundColor: 'var(--bg-card-solid)', border: '1px solid var(--glass-border)', borderRadius: '8px', boxShadow: '0 8px 32px rgba(0,0,0,0.3)' }}
                      itemStyle={{ color: 'var(--text-main)' }}
                      labelStyle={{ color: 'var(--text-muted)', marginBottom: '4px' }}
                    />
                    <Line type="monotone" dataKey={chart.key} stroke={chart.color} strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  {loadError ? `Error: ${loadError}` : 'Loading metrics...'}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Training Artifacts (Images) */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <div className="card-title"><ImageIcon size={18} color="#a78bfa" /> Training Artifacts</div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }} className="artifacts-grid">
          {MODEL_IMAGES.map(img => (
            <div key={img.file} onClick={() => setSelectedImage(img)}
              style={{
                borderRadius: '10px', overflow: 'hidden', cursor: 'pointer',
                border: '1px solid var(--glass-border)', transition: 'transform 0.2s, box-shadow 0.2s',
                background: '#0a0e17',
              }}
              onMouseEnter={e => { e.currentTarget.style.transform = 'scale(1.02)'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.3)'; }}
              onMouseLeave={e => { e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.boxShadow = 'none'; }}
            >
              <img src={`${API_URL}/model_assets/${img.file}`} alt={img.label}
                style={{ width: '100%', height: '160px', objectFit: 'contain', display: 'block' }} />
              <div style={{ padding: '10px 12px' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, marginBottom: '2px' }}>{img.label}</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{img.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Training Config */}
      {config && (
        <div className="card">
          <div className="card-header" style={{ cursor: 'pointer' }} onClick={() => setShowConfig(!showConfig)}>
            <div className="card-title"><Settings2 size={18} color="var(--text-muted)" /> Training Configuration</div>
            {showConfig ? <ChevronUp size={18} color="var(--text-muted)" /> : <ChevronDown size={18} color="var(--text-muted)" />}
          </div>
          {showConfig && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', animation: 'fadeIn 0.3s ease' }} className="config-grid">
              {Object.entries(config).filter(([k]) => !k.startsWith('project') && !k.startsWith('name') && !k.startsWith('save_dir')).map(([key, value]) => (
                <div key={key} style={{
                  padding: '10px 12px', borderRadius: '8px',
                  background: 'rgba(255,255,255,0.02)', border: '1px solid var(--glass-border)',
                }}>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '3px' }}>{key}</div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 500, wordBreak: 'break-all' }}>{String(value)}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Lightbox */}
      {selectedImage && (
        <div onClick={() => setSelectedImage(null)} style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(8px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999,
          cursor: 'pointer', animation: 'fadeIn 0.2s ease',
        }}>
          <div style={{ maxWidth: '90vw', maxHeight: '90vh', position: 'relative' }}
            onClick={e => e.stopPropagation()}>
            <img src={`${API_URL}/model_assets/${selectedImage.file}`} alt={selectedImage.label}
              style={{ maxWidth: '100%', maxHeight: '85vh', borderRadius: '12px', boxShadow: '0 24px 48px rgba(0,0,0,0.5)' }} />
            <div style={{ textAlign: 'center', marginTop: '12px', color: '#e2e8f0', fontWeight: 600 }}>
              {selectedImage.label}
            </div>
            <button onClick={() => setSelectedImage(null)}
              style={{ position: 'absolute', top: '-12px', right: '-12px', background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(148,163,184,0.2)', borderRadius: '50%', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: '#e2e8f0' }}>
              ✕
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
