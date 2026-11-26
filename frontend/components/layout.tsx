import React from 'react';
import {
  AlertTriangle,
  CheckSquare,
  Compass,
  FileSearch,
  FileText,
  GitCompare,
  Home,
  Info,
  LayoutDashboard,
  ShieldAlert,
  Trash2,
  Upload,
} from 'lucide-react';
import type { ScreenId, SessionSummary } from '../types';

interface LayoutProps {
  activeScreen: ScreenId;
  onNavigate: (screen: ScreenId) => void;
  activeSession: SessionSummary | null;
  onDeleteSession: () => void;
  backendConnected: boolean | null;
  children: React.ReactNode;
}

const NAV_ITEMS: { id: ScreenId; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: 'landing', label: 'Welcome', icon: Home },
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'upload', label: 'New Analysis', icon: Upload },
  { id: 'analysis', label: 'Document Analysis', icon: FileSearch },
  { id: 'compare', label: 'Compare Documents', icon: GitCompare },
  { id: 'readiness', label: 'Readiness Checklist', icon: CheckSquare },
  { id: 'guidance', label: 'AI Guidance', icon: Compass },
  { id: 'reports', label: 'Reports', icon: FileText },
  { id: 'about', label: 'About / Privacy', icon: Info },
];

export const Layout: React.FC<LayoutProps> = ({
  activeScreen,
  onNavigate,
  activeSession,
  onDeleteSession,
  backendConnected,
  children,
}) => {
  return (
    <div className="min-h-screen flex flex-col bg-[#F5F7FA] text-slate-800">
      {/* Persistent Academic Prototype Disclaimer */}
      <div className="bg-[#123B5D] text-white text-xs px-4 py-2 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-[#5EEAD4] shrink-0" />
          <span>
            <strong>Academic Prototype:</strong> Not an official government or NADRA service. Does not verify identity or certify legal authenticity.
          </span>
        </div>
        <div className="flex items-center gap-3">
          {backendConnected === true && (
            <span className="inline-flex items-center gap-1.5 text-emerald-200">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              API Connected
            </span>
          )}
          {backendConnected === false && (
            <span className="inline-flex items-center gap-1.5 text-amber-200">
              <AlertTriangle className="w-3.5 h-3.5" />
              API Offline (Start backend on :8000)
            </span>
          )}
        </div>
      </div>

      {/* Top Header */}
      <header className="bg-white border-b border-slate-200 px-4 lg:px-8 py-3 flex flex-wrap items-center justify-between gap-4 shadow-xs">
        <button
          type="button"
          onClick={() => onNavigate('landing')}
          className="flex items-center gap-3 text-left group"
        >
          <div className="w-9 h-9 rounded-lg bg-[#123B5D] text-white flex items-center justify-center font-bold text-lg tracking-tight">
            D
          </div>
          <div>
            <div className="text-lg font-bold text-[#123B5D] leading-tight group-hover:text-[#167D9A] transition-colors">
              DASTAK AI
            </div>
            <div className="text-xs text-slate-500">Smart Documents, Secure Future.</div>
          </div>
        </button>

        {activeSession && (
          <div className="flex items-center gap-3 bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-xs">
            <div>
              <span className="text-slate-500">Active Session:</span>{' '}
              <span className="font-semibold text-[#123B5D]">{activeSession.application_type}</span>{' '}
              <span className="text-slate-400 font-mono">({activeSession.id.slice(0, 8)})</span>
            </div>
            <button
              type="button"
              onClick={onDeleteSession}
              className="inline-flex items-center gap-1 text-rose-700 hover:text-rose-900 font-medium px-2 py-1 rounded hover:bg-rose-50 transition-colors"
              title="Delete this session and all temporary uploaded files"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Delete Session
            </button>
          </div>
        )}
      </header>

      <div className="flex-1 flex flex-col lg:flex-row max-w-7xl w-full mx-auto px-4 lg:px-8 py-6 gap-6">
        {/* Sidebar Navigation */}
        <nav aria-label="Primary navigation" className="lg:w-60 shrink-0">
          <div className="bg-white border border-slate-200 rounded-xl p-2 shadow-xs flex lg:flex-col gap-1 overflow-x-auto">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = activeScreen === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => onNavigate(item.id)}
                  className={`flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-medium whitespace-nowrap transition-colors text-left ${
                    isActive
                      ? 'bg-[#123B5D] text-white'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-[#123B5D]'
                  }`}
                >
                  <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-[#5EEAD4]' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 min-w-0">{children}</main>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white text-xs text-slate-500 py-3 px-4 text-center">
        DASTAK AI • Academic Prototype • Not an official government or NADRA service • Use synthetic fictional data only.
      </footer>
    </div>
  );
};
