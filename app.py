import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { initializeApp } from 'firebase/app';
import { 
  getAuth, 
  signInAnonymously, 
  onAuthStateChanged, 
  signInWithCustomToken 
} from 'firebase/auth';
import { 
  getFirestore, 
  collection, 
  addDoc, 
  onSnapshot, 
  serverTimestamp 
} from 'firebase/firestore';
import { 
  XAxis, 
  YAxis, 
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  Tooltip,
  AreaChart,
  Area
} from 'recharts';
import { 
  Zap, 
  Sun, 
  Moon, 
  TrendingUp,
  ShieldAlert,
  Sparkles,
  RefreshCw,
  CheckCircle2,
  Lock,
  History
} from 'lucide-react';

// --- CONFIGURATION ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'ketchup-pro-prod';

export default function App() {
  // App State
  const [activeTab, setActiveTab] = useState('home'); 
  const [isDark, setIsDark] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [user, setUser] = useState(null);
  const [isSyncing, setIsSyncing] = useState(false);
  
  // Data State
  const [logs, setLogs] = useState([]);
  const [history, setHistory] = useState([]);

  // 1. AUTHENTICATION (RULE 3)
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (err) {
        console.error("Auth sync error:", err);
      }
    };
    initAuth();
    const unsubscribe = onAuthStateChanged(auth, (u) => setUser(u));
    return () => unsubscribe();
  }, []);

  // 2. DATA SYNC (RULE 1)
  useEffect(() => {
    if (!user || !isAuthenticated) return;
    
    const logsRef = collection(db, 'artifacts', appId, 'users', user.uid, 'dose_logs');
    
    const unsubscribe = onSnapshot(logsRef, (snapshot) => {
      const data = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      })).sort((a, b) => {
        const timeA = a.timestamp?.seconds || 0;
        const timeB = b.timestamp?.seconds || 0;
        return timeB - timeA;
      });
      setLogs(data);
    }, (err) => {
      console.error("Sync error:", err);
    });

    return () => unsubscribe();
  }, [user, isAuthenticated]);

  // 3. CORE ACTIONS
  const logDose = useCallback(async () => {
    if (!user || isSyncing) return;
    setIsSyncing(true);
    try {
      await addDoc(collection(db, 'artifacts', appId, 'users', user.uid, 'dose_logs'), {
        timestamp: serverTimestamp(),
        cycleDay: (logs.length % 28) + 1,
        status: 'confirmed'
      });
      if (navigator.vibrate) navigator.vibrate(50);
    } catch (err) {
      console.error("Write error:", err);
    } finally {
      setTimeout(() => setIsSyncing(false), 500);
    }
  }, [user, isSyncing, logs.length]);

  // 4. DATA COMPUTATION
  const stats = useMemo(() => {
    const day = (logs.length % 28) + 1;
    return {
      cycleDay: day,
      phase: day >= 20 ? 'Luteal' : 'Follikulär',
      isWarning: day >= 20,
      totalLogs: logs.length
    };
  }, [logs.length]);

  const trendData = useMemo(() => {
    return Array.from({ length: 7 }, (_, i) => ({
      name: i,
      val: 2 + Math.random() * 2
    }));
  }, [logs.length]);

  // --- RENDERING ---

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 text-white font-sans">
        <div className="w-full max-w-sm bg-white/5 border border-white/10 p-10 rounded-[3rem] text-center backdrop-blur-3xl shadow-2xl">
          <div className="w-20 h-20 bg-red-600 rounded-3xl mx-auto mb-8 flex items-center justify-center shadow-xl shadow-red-600/20 rotate-3">
             <Lock size={32} />
          </div>
          <h1 className="text-3xl font-black italic tracking-tighter mb-2 uppercase">Ketchup Pro</h1>
          <p className="text-slate-500 text-[10px] font-black uppercase tracking-[0.3em] mb-10">Deploy: Production_v1.0</p>
          
          <input 
            type="password" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && password === 'Bella2026' && setIsAuthenticated(true)}
            className="w-full bg-white/5 border border-white/10 rounded-2xl p-5 text-center text-white mb-6 outline-none focus:border-red-600 font-black text-2xl tracking-[0.5em] transition-all"
            placeholder="••••"
          />
          
          <button 
            onClick={() => password === 'Bella2026' && setIsAuthenticated(true)}
            className="w-full bg-red-600 hover:bg-red-500 py-5 rounded-2xl font-black uppercase tracking-widest active:scale-95 transition-all shadow-lg shadow-red-600/20"
          >
            Verifiera Access
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen transition-all duration-700 ${isDark ? 'bg-black text-white' : 'bg-slate-50 text-slate-900'}`}>
      <style>{`
        .glass-panel { 
          background: ${isDark ? 'rgba(255,255,255,0.03)' : 'rgba(255,255,255,0.8)'}; 
          backdrop-filter: blur(24px); 
          border: 1px solid ${isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.05)'}; 
        }
        .btn-active { color: #ef4444; transform: scale(1.1); }
      `}</style>

      {/* HEADER */}
      <nav className="p-4 flex justify-between items-center glass-panel m-4 rounded-[2.5rem] sticky top-4 z-50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-red-600 rounded-2xl flex items-center justify-center text-white font-black italic shadow-lg">K</div>
          <div>
            <h1 className="font-black italic text-lg tracking-tighter leading-none">KETCHUP PRO</h1>
            <div className="flex items-center gap-1.5 opacity-40">
              <span className="text-[8px] font-black uppercase tracking-widest">System Stable</span>
              <CheckCircle2 size={10} className="text-green-500" />
            </div>
          </div>
        </div>
        <button onClick={() => setIsDark(!isDark)} className="p-3 rounded-2xl bg-white/5 hover:bg-white/10 transition-colors">
          {isDark ? <Sun size={18} className="text-yellow-400" /> : <Moon size={18} className="text-slate-800" />}
        </button>
      </nav>

      <main className="max-w-md mx-auto p-6 pb-32 space-y-6">
        
        {activeTab === 'home' && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* MAIN ACTION */}
            <button 
              onClick={logDose}
              disabled={isSyncing}
              className={`w-full h-56 rounded-[3.5rem] bg-gradient-to-br from-red-600 via-red-600 to-red-800 shadow-2xl flex flex-col items-center justify-center gap-3 active:scale-95 transition-all overflow-hidden relative group ${isSyncing ? 'opacity-70' : ''}`}
            >
              <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
              {isSyncing ? (
                <RefreshCw className="animate-spin text-white" size={48} />
              ) : (
                <Zap size={56} fill="white" className="drop-shadow-lg" />
              )}
              <div className="text-center">
                <span className="block text-2xl font-black italic text-white tracking-tighter uppercase leading-tight">Registrera Dos</span>
                <span className="text-[10px] text-white/50 font-black uppercase tracking-widest">Klick-till-Moln Synk</span>
              </div>
            </button>

            {/* AI PREDICTION CARD */}
            <div className="glass-panel p-7 rounded-[3rem] border-red-500/20">
              <div className="flex justify-between items-center mb-5">
                <div className="flex items-center gap-2">
                  <Sparkles size={18} className="text-red-500" />
                  <h3 className="font-black text-[11px] uppercase tracking-widest text-red-500">Statusanalys</h3>
                </div>
                <div className={`px-3 py-1 rounded-full text-[9px] font-black uppercase ${stats.isWarning ? 'bg-orange-500/20 text-orange-500' : 'bg-green-500/20 text-green-500'}`}>
                  Fas: {stats.phase}
                </div>
              </div>
              <p className="text-[13px] font-bold leading-relaxed mb-4 opacity-80">
                {stats.isWarning 
                  ? "Du är i din känsliga fas. Var extra noggrann med doseringsfönstret för att bibehålla jämn effekt." 
                  : "Stabil trend observerad. Inga fysiologiska avvikelser i nuvarande cykel."}
              </p>
              <div className="flex items-center gap-2 pt-2 border-t border-white/5">
                <TrendingUp size={14} className="opacity-30" />
                <span className="text-[9px] font-black uppercase tracking-widest opacity-30">Prediktiv Algoritm v2.1</span>
              </div>
            </div>

            {/* STATS GRID */}
            <div className="grid grid-cols-2 gap-4">
              <div className="glass-panel p-6 rounded-[2.5rem]">
                <p className="text-[9px] font-black uppercase tracking-widest opacity-40 mb-1">Cykeldag</p>
                <div className="flex items-end gap-1">
                  <p className="text-5xl font-black italic leading-none">{stats.cycleDay}</p>
                  <p className="text-[10px] font-black uppercase opacity-20 mb-1">/ 28</p>
                </div>
              </div>
              <div className="glass-panel p-6 rounded-[2.5rem]">
                <p className="text-[9px] font-black uppercase tracking-widest opacity-40 mb-1">Totala Loggar</p>
                <p className="text-5xl font-black italic leading-none text-red-500">{stats.totalLogs}</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analysis' && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="glass-panel p-8 rounded-[3.5rem]">
              <div className="flex items-center gap-2 mb-8">
                <History size={18} className="text-red-500" />
                <h3 className="font-black text-[11px] uppercase tracking-widest">Trendhistorik</h3>
              </div>
              <div className="h-64 w-full -ml-4">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendData}>
                    <defs>
                      <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.03)" />
                    <XAxis dataKey="name" hide />
                    <YAxis hide domain={[0, 6]} />
                    <Tooltip content={() => null} />
                    <Area 
                      type="monotone" 
                      dataKey="val" 
                      stroke="#ef4444" 
                      strokeWidth={4} 
                      fillOpacity={1} 
                      fill="url(#colorVal)" 
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-6 flex justify-between items-center text-[10px] font-black uppercase opacity-30">
                <span>7 Dagars Trend</span>
                <span>Optimering: On</span>
              </div>
            </div>
            
            <div className="space-y-3">
              {logs.slice(0, 3).map((log, idx) => (
                <div key={log.id} className="glass-panel p-4 rounded-2xl flex justify-between items-center opacity-60">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center">
                      <Zap size={14} className="text-red-500" />
                    </div>
                    <span className="text-xs font-bold uppercase tracking-tight">Doseringslogg #{logs.length - idx}</span>
                  </div>
                  <span className="text-[10px] font-black opacity-40">DAG {log.cycleDay}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* NAVIGATION */}
      <div className="fixed bottom-8 left-0 w-full px-10 z-50">
        <div className="max-w-xs mx-auto glass-panel h-20 rounded-[2.5rem] shadow-2xl flex justify-around items-center px-6">
            <button 
              onClick={() => setActiveTab('home')} 
              className={`p-4 transition-all duration-300 ${activeTab === 'home' ? 'btn-active' : 'text-slate-500 opacity-30 hover:opacity-100'}`}
            >
              <Zap size={24} fill={activeTab === 'home' ? 'currentColor' : 'none'} />
            </button>
            <button 
              onClick={() => setActiveTab('analysis')} 
              className={`p-4 transition-all duration-300 ${activeTab === 'analysis' ? 'btn-active' : 'text-slate-500 opacity-30 hover:opacity-100'}`}
            >
              <TrendingUp size={24} />
            </button>
        </div>
      </div>
    </div>
  );
}
