import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell, RadialBarChart, RadialBar, Legend } from 'recharts';
import { ShieldAlert, CheckCircle, Activity, TrendingUp, Clock, AlertTriangle } from 'lucide-react';

const API_URL = 'http://localhost:5000';
const COLORS = ['#f43f5e', '#f59e0b', '#6366f1', '#a78bfa'];

export default function Dashboard() {
  const [stats, setStats] = useState([]);
  const [recentLogs, setRecentLogs] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const statsRes = await fetch(`${API_URL}/api/stats`);
        setStats(await statsRes.json());
        
        const logsRes = await fetch(`${API_URL}/api/logs?limit=5`);
        setRecentLogs(await logsRes.json());
      } catch (e) {
        console.error(e);
      }
    };
    
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const totalViolations = stats.reduce((acc, curr) => acc + curr.value, 0);

  // Compliance gauge data
  const complianceRate = totalViolations > 0 ? Math.max(0, 100 - totalViolations * 2) : 100;
  const gaugeData = [{ name: 'Compliance', value: complianceRate, fill: complianceRate > 70 ? '#10b981' : complianceRate > 40 ? '#f59e0b' : '#f43f5e' }];

  const getViolationIcon = (type) => {
    if (type.includes('Hardhat')) return '🪖';
    if (type.includes('Vest')) return '🦺';
    if (type.includes('Mask')) return '😷';
    return '⚠️';
  };

  const getViolationColor = (type) => {
    if (type.includes('Hardhat')) return '#f59e0b';
    if (type.includes('Vest')) return '#f43f5e';
    if (type.includes('Mask')) return '#6366f1';
    return '#f43f5e';
  };

  return (
    <div style={{ animation: 'fadeIn 0.4s ease' }}>
      <div className="top-bar">
        <div>
          <h1>Overview Dashboard</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>
            Real-time safety monitoring analytics
          </p>
        </div>
        <div className="status-pill online">
          <span className="pulse-dot"></span>
          SYSTEM ONLINE
        </div>
      </div>

      {/* Top Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
        <div className="stat-card" style={{ animationDelay: '0.05s' }}>
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, rgba(244, 63, 94, 0.15), rgba(244, 63, 94, 0.05))' }}>
            <ShieldAlert size={24} color="#f43f5e" />
          </div>
          <div>
            <div className="stat-value" style={{ color: '#f43f5e' }}>{totalViolations}</div>
            <div className="stat-label">Total Violations</div>
          </div>
        </div>
        
        {stats.map((s, idx) => (
          <div className="stat-card" key={s.name} style={{ animationDelay: `${(idx + 1) * 0.1}s` }}>
            <div className="stat-icon" style={{ background: `linear-gradient(135deg, ${COLORS[idx]}22, ${COLORS[idx]}08)` }}>
              <AlertTriangle size={22} color={COLORS[idx]} />
            </div>
            <div>
              <div className="stat-value">{s.value}</div>
              <div className="stat-label">{s.name}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Charts & Activity area */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: '1.5rem' }}>
        {/* Bar Chart */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <TrendingUp size={18} color="var(--accent)" />
              Violation Breakdown
            </div>
          </div>
          <div style={{ width: '100%', height: 300 }}>
            {stats.length > 0 ? (
              <ResponsiveContainer>
                <BarChart data={stats} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                  <defs>
                    {stats.map((entry, index) => (
                      <linearGradient id={`barGrad${index}`} key={index} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor={COLORS[index]} stopOpacity={1} />
                        <stop offset="100%" stopColor={COLORS[index]} stopOpacity={0.5} />
                      </linearGradient>
                    ))}
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.07)" />
                  <XAxis dataKey="name" stroke="var(--text-muted)" tick={{ fontSize: 12 }} />
                  <YAxis allowDecimals={false} stroke="var(--text-muted)" tick={{ fontSize: 12 }} />
                  <Tooltip 
                    cursor={{ fill: 'rgba(99,102,241,0.05)' }} 
                    contentStyle={{ backgroundColor: 'var(--bg-card-solid)', border: '1px solid var(--glass-border)', borderRadius: '10px', boxShadow: '0 8px 32px rgba(0,0,0,0.3)' }}
                    itemStyle={{ color: 'var(--text-main)' }}
                    labelStyle={{ color: 'var(--text-muted)', marginBottom: '4px' }}
                  />
                  {stats.map((entry, index) => (
                    <Bar key={index} dataKey="value" fill={`url(#barGrad${index})`} radius={[6, 6, 0, 0]} />
                  ))}
                  <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                    {stats.map((entry, index) => (
                      <Cell key={index} fill={`url(#barGrad${index})`} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', flexDirection: 'column', gap: '10px' }}>
                <TrendingUp size={40} opacity={0.2} />
                <p>Start detecting to see analytics</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Compliance + Recent */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Compliance Gauge */}
          <div className="card" style={{ textAlign: 'center' }}>
            <div className="card-header" style={{ justifyContent: 'center' }}>
              <div className="card-title">
                <CheckCircle size={18} color="#10b981" />
                Safety Score
              </div>
            </div>
            <div style={{ width: '100%', height: 140 }}>
              <ResponsiveContainer>
                <RadialBarChart cx="50%" cy="90%" innerRadius="60%" outerRadius="100%" startAngle={180} endAngle={0} data={gaugeData} barSize={14}>
                  <RadialBar background={{ fill: 'rgba(148,163,184,0.08)' }} clockWise dataKey="value" cornerRadius={10} />
                </RadialBarChart>
              </ResponsiveContainer>
            </div>
            <div style={{ marginTop: '-20px' }}>
              <span style={{ fontSize: '2rem', fontWeight: 800, color: complianceRate > 70 ? '#10b981' : complianceRate > 40 ? '#f59e0b' : '#f43f5e' }}>
                {complianceRate}%
              </span>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>Workplace Compliance</p>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="card" style={{ flex: 1 }}>
            <div className="card-header">
              <div className="card-title">
                <Clock size={18} color="var(--text-muted)" />
                Live Activity
              </div>
            </div>
            <div className="logs-list" style={{ maxHeight: '220px' }}>
              {recentLogs.length > 0 ? recentLogs.map((log) => (
                <div className="log-item" key={log.id} style={{ borderLeftColor: getViolationColor(log.violation_type) }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ fontSize: '1.2rem' }}>{getViolationIcon(log.violation_type)}</span>
                    <div className="log-info">
                      <h4>{log.violation_type}</h4>
                      <p>Person #{log.track_id}</p>
                    </div>
                  </div>
                  <span className="log-time">{log.timestamp?.split(' ')[1] || ''}</span>
                </div>
              )) : (
                <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                  <Activity size={30} opacity={0.15} />
                  <p style={{ marginTop: '8px', fontSize: '0.85rem' }}>No recent activity</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
