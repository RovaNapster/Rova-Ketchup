import React, { useState, useEffect, useMemo } from 'react';
import TrendChart from './TrendChart';

const Tracker = () => {
  const [logs, setLogs] = useState([]);
  const [mood, setMood] = useState(7);
  const [spotting, setSpotting] = useState(false);
  const [isPressed, setIsPressed] = useState(false);

  useEffect(() => {
    const savedLogs = localStorage.getItem('rovaLogs');
    if (savedLogs) setLogs(JSON.parse(savedLogs));
  }, []);

  // Memoize analysen för att förhindra lagg vid 120Hz scrolling
  const analysis = useMemo(() => {
    if (logs.length < 3) return null;
    const recent = logs.slice(-14);
    const spottingDays = recent.filter(l => l.spotting).length;
    const avgMood = recent.reduce((a, b) => a + b.mood, 0) / recent.length;
    
    return {
      status: avgMood < 4 ? "Kritisk" : spottingDays > 4 ? "Adaption" : "Optimal",
      color: avgMood < 4 ? "#ff4d4d" : spottingDays > 4 ? "#ffa500" : "#00ff88",
      advice: avgMood < 4 ? "Varning: Sänkt dagsform detekterad." : "Systemet körs inom normalvärden."
    };
  }, [logs]);

  const handleLog = () => {
    const entry = {
      date: new Date().toLocaleDateString('sv-SE', { day: 'numeric', month: 'short' }),
      mood: parseInt(mood),
      spotting,
      timestamp: new Date().toISOString()
    };
    setLogs(prev => [...prev, entry]);
    localStorage.setItem('rovaLogs', JSON.stringify([...logs, entry]));
    
    // Trigger haptic feel (simulerad via animation)
    setIsPressed(true);
    setTimeout(() => setIsPressed(false), 200);
  };

  return (
    <div style={{ 
      backgroundColor: '#000', color: '#fff', minHeight: '100vh', 
      padding: '20px', fontFamily: 'Inter, sans-serif',
      WebkitFontSmoothing: 'antialiased' 
    }}>
      {/* GLASSMORPHISM HEADER */}
      <div style={{
        padding: '20px', borderRadius: '24px', 
        background: 'rgba(214, 40, 40, 0.1)',
        backdropFilter: 'blur(20px)', border: '1px solid rgba(214, 40, 40, 0.2)',
        marginBottom: '30px', textAlign: 'center'
      }}>
        <h1 style={{ margin: 0, fontSize: '32px', fontWeight: '900', letterSpacing: '-1px' }}>
          ROVA <span style={{ color: '#d62828' }}>ULTRA</span>
        </h1>
      </div>

      {/* ULTRA-RESPONSIVE BUTTON */}
      <button 
        onClick={handleLog}
        style={{
          width: '100%', padding: '25px', borderRadius: '20px',
          backgroundColor: isPressed ? '#9a1a1a' : '#d62828',
          color: '#fff', border: 'none', fontWeight: '800', fontSize: '20px',
          transform: isPressed ? 'scale(0.96)' : 'scale(1)',
          transition: 'all 0.1s cubic-bezier(0, 0, 0, 1)', // Snabb transition för 120Hz
          boxShadow: isPressed ? 'none' : '0 10px 40px rgba(214, 40, 40, 0.4)',
          marginBottom: '30px'
        }}
      >
        LOGGA DOS ⚡
      </button>

      {/* DYNAMISK ANALYS */}
      {analysis && (
        <div style={{
          padding: '20px', borderRadius: '20px', borderLeft: `6px solid ${analysis.color}`,
          background: '#111', marginBottom: '20px', transition: 'all 0.5s ease'
        }}>
          <div style={{ color: analysis.color, fontWeight: 'bold', fontSize: '12px' }}>STATUS: {analysis.status.toUpperCase()}</div>
          <div style={{ fontSize: '16px', marginTop: '5px' }}>{analysis.advice}</div>
        </div>
      )}

      {/* PRO-CHART CONTAINER */}
      <div style={{ 
        background: '#0a0a0a', borderRadius: '24px', padding: '20px',
        border: '1px solid #1a1a1a'
      }}>
        <TrendChart dataLogs={logs} />
      </div>
    </div>
  );
};

export default Tracker;
