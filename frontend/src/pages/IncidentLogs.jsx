import { useState, useEffect } from 'react';
import { Database, Download, Search, Image as ImageIcon, FileText, Eye } from 'lucide-react';

const API_URL = 'http://localhost:5000';

export default function IncidentLogs() {
  const [logs, setLogs] = useState([]);
  const [search, setSearch] = useState('');

  const fetchLogs = async () => {
    try {
      const res = await fetch(`${API_URL}/api/logs/all`);
      setLogs(await res.json());
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleExportCSV = () => {
    const headers = ['ID', 'Timestamp', 'Track ID', 'Violation Type', 'Snapshot File'];
    const csvContent = [
      headers.join(','),
      ...logs.map(l => `${l.id},${l.timestamp},${l.track_id},${l.violation_type},${l.image_path || 'None'}`)
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `safety_logs_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  const filteredLogs = logs.filter(log => 
    log.violation_type.toLowerCase().includes(search.toLowerCase()) || 
    log.timestamp.includes(search) ||
    (log.track_id && log.track_id.toString().includes(search))
  );

  const getViolationBadge = (type) => {
    if (type.includes('Hardhat')) return { bg: 'rgba(245, 158, 11, 0.12)', color: '#fbbf24', border: 'rgba(245, 158, 11, 0.2)' };
    if (type.includes('Vest')) return { bg: 'rgba(244, 63, 94, 0.12)', color: '#fb7185', border: 'rgba(244, 63, 94, 0.2)' };
    return { bg: 'rgba(99, 102, 241, 0.12)', color: '#a5b4fc', border: 'rgba(99, 102, 241, 0.2)' };
  };

  return (
    <div style={{ animation: 'fadeIn 0.4s ease' }}>
      <div className="top-bar">
        <div>
          <h1>Incident Evidence Vault</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>
            {logs.length} total incidents recorded
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn-primary" onClick={handleExportCSV}>
            <Download size={16} />
            Export CSV
          </button>
        </div>
      </div>

      <div className="card">
        {/* Search */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px', background: 'rgba(255,255,255,0.02)', padding: '10px 16px', borderRadius: '10px', border: '1px solid var(--glass-border)', transition: 'border-color 0.3s' }}>
          <Search size={16} color="var(--text-muted)" />
          <input 
            type="text" 
            placeholder="Search by date, violation type, or Track ID..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ background: 'transparent', border: 'none', color: 'var(--text-main)', width: '100%', outline: 'none', fontSize: '0.85rem' }}
          />
          {search && (
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
              {filteredLogs.length} results
            </span>
          )}
        </div>

        {/* Table */}
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: '0 4px', textAlign: 'left' }}>
            <thead>
              <tr style={{ color: 'var(--text-muted)' }}>
                <th style={{ padding: '10px 12px', fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Evidence</th>
                <th style={{ padding: '10px 12px', fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>ID</th>
                <th style={{ padding: '10px 12px', fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Timestamp</th>
                <th style={{ padding: '10px 12px', fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Person</th>
                <th style={{ padding: '10px 12px', fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Violation</th>
                <th style={{ padding: '10px 12px', fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.map((log, idx) => {
                const badge = getViolationBadge(log.violation_type);
                return (
                  <tr key={log.id} style={{ 
                    background: 'rgba(255,255,255,0.015)', 
                    borderRadius: '8px',
                    animation: `slideIn 0.3s ease forwards`,
                    animationDelay: `${idx * 0.03}s`,
                    opacity: 0
                  }}>
                    <td style={{ padding: '10px 12px' }}>
                      {log.image_path ? (
                        <div style={{ 
                          width: '100px', height: '56px', borderRadius: '8px', overflow: 'hidden', 
                          border: '1px solid var(--glass-border)',
                          cursor: 'pointer',
                          transition: 'transform 0.2s, box-shadow 0.2s',
                          position: 'relative'
                        }}
                        onClick={() => window.open(`${API_URL}/snapshots/${log.image_path}`, '_blank')}
                        onMouseEnter={e => { e.currentTarget.style.transform = 'scale(1.05)'; e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)'; }}
                        onMouseLeave={e => { e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.boxShadow = 'none'; }}
                        >
                          <img 
                            src={`${API_URL}/snapshots/${log.image_path}`} 
                            alt="Evidence" 
                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                          />
                        </div>
                      ) : (
                        <div style={{ width: '100px', height: '56px', borderRadius: '8px', border: '1px dashed var(--glass-border)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#334155' }}>
                          <ImageIcon size={18} />
                        </div>
                      )}
                    </td>
                    <td style={{ padding: '10px 12px', fontVariantNumeric: 'tabular-nums', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      #{log.id}
                    </td>
                    <td style={{ padding: '10px 12px', fontSize: '0.85rem', fontVariantNumeric: 'tabular-nums' }}>
                      {log.timestamp}
                    </td>
                    <td style={{ padding: '10px 12px' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.85rem' }}>#{log.track_id}</span>
                    </td>
                    <td style={{ padding: '10px 12px' }}>
                      <span style={{ 
                        background: badge.bg, color: badge.color, 
                        padding: '5px 14px', borderRadius: '999px', 
                        fontSize: '0.78rem', fontWeight: 600,
                        border: `1px solid ${badge.border}`
                      }}>
                        {log.violation_type}
                      </span>
                    </td>
                    <td style={{ padding: '10px 12px' }}>
                      {log.image_path && (
                        <button 
                          onClick={() => window.open(`${API_URL}/snapshots/${log.image_path}`, '_blank')}
                          className="btn-ghost"
                          style={{ padding: '5px 10px', fontSize: '0.75rem' }}
                        >
                          <Eye size={13} /> View
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
              {filteredLogs.length === 0 && (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '60px 20px' }}>
                    <Database size={48} color="var(--text-muted)" opacity={0.12} />
                    <p style={{ color: 'var(--text-muted)', marginTop: '12px', fontSize: '0.9rem' }}>No incidents found</p>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '4px' }}>Violations will appear here when detected</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
