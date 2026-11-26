import React from 'react';
import { FileText, FolderOpen, Plus, Trash2, UploadCloud } from 'lucide-react';
import type { DashboardStats, SessionSummary } from '../types';

interface DashboardPageProps {
  stats: DashboardStats;
  loading: boolean;
  onNewAnalysis: () => void;
  onOpenSession: (session: SessionSummary) => void;
  onDeleteSession: (sessionId: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  stats,
  loading,
  onNewAnalysis,
  onOpenSession,
  onDeleteSession,
}) => {
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#123B5D]">Dashboard</h1>
          <p className="text-sm text-slate-600">
            Local academic sessions stored in SQLite. Statistics reflect only real local sessions.
          </p>
        </div>
        <button
          type="button"
          onClick={onNewAnalysis}
          className="inline-flex items-center gap-2 bg-[#123B5D] hover:bg-[#0E2F4B] text-white font-semibold px-4 py-2.5 rounded-xl transition-colors shadow-xs"
        >
          <Plus className="w-4 h-4" />
          New Analysis
        </button>
      </div>

      {/* Summary Cards (real counts only, 0 when empty) */}
      <div className="grid sm:grid-cols-3 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">
            Local Sessions
          </div>
          <div className="text-3xl font-bold text-[#123B5D] mt-2">
            {loading ? '—' : stats.total_sessions}
          </div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">
            Documents Processed
          </div>
          <div className="text-3xl font-bold text-[#167D9A] mt-2">
            {loading ? '—' : stats.total_documents}
          </div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">
            Reports Created
          </div>
          <div className="text-3xl font-bold text-[#123B5D] mt-2">
            {loading ? '—' : stats.total_reports}
          </div>
        </div>
      </div>

      {/* Recent Local Sessions */}
      <section className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
        <h2 className="text-lg font-semibold text-[#123B5D] mb-4">Recent Local Sessions</h2>
        {stats.sessions.length === 0 ? (
          <div className="text-center py-10 border border-dashed border-slate-300 rounded-xl bg-slate-50">
            <UploadCloud className="w-10 h-10 text-slate-400 mx-auto mb-3" />
            <p className="text-slate-700 font-medium">No local sessions yet</p>
            <p className="text-sm text-slate-500 mt-1">
              Start a new document-check session using synthetic sample files.
            </p>
            <button
              type="button"
              onClick={onNewAnalysis}
              className="mt-4 inline-flex items-center gap-2 bg-[#167D9A] hover:bg-[#12667E] text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4" />
              Start First Session
            </button>
          </div>
        ) : (
          <div className="divide-y divide-slate-200">
            {stats.sessions.map((s) => (
              <div
                key={s.id}
                className="py-3.5 flex flex-wrap items-center justify-between gap-4"
              >
                <div>
                  <div className="font-semibold text-[#123B5D] flex items-center gap-2">
                    <FileText className="w-4 h-4 text-[#167D9A]" />
                    {s.application_type}
                  </div>
                  <div className="text-xs text-slate-500 mt-0.5">
                    ID: <span className="font-mono">{s.id.slice(0, 8)}</span> • Created:{' '}
                    {new Date(s.created_at).toLocaleString()} • Documents: {s.document_count}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => onOpenSession(s)}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-[#123B5D] px-3 py-1.5 rounded-lg transition-colors"
                  >
                    <FolderOpen className="w-3.5 h-3.5" />
                    Open
                  </button>
                  <button
                    type="button"
                    onClick={() => onDeleteSession(s.id)}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-rose-700 hover:bg-rose-50 px-2.5 py-1.5 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};
