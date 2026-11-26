import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, RefreshCw } from 'lucide-react';
import type { ReadinessResponse } from '../types';

interface ReadinessPageProps {
  readiness: ReadinessResponse | null;
  onRefresh: () => Promise<void>;
  loading: boolean;
}

export const ReadinessPage: React.FC<ReadinessPageProps> = ({ readiness, onRefresh, loading }) => {
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#123B5D]">Readiness Checklist</h1>
          <p className="text-sm text-slate-600">
            Transparent rule-based Prototype Readiness Score and required document categories.
          </p>
        </div>
        <button
          type="button"
          onClick={onRefresh}
          disabled={loading}
          className="inline-flex items-center gap-2 bg-[#123B5D] hover:bg-[#0E2F4B] disabled:opacity-50 text-white text-sm font-semibold px-4 py-2 rounded-xl"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Recalculate
        </button>
      </div>

      {!readiness ? (
        <div className="bg-white border border-slate-200 rounded-xl p-8 text-center text-sm text-slate-600">
          Create a session and upload documents to calculate the Prototype Readiness Score.
        </div>
      ) : (
        <>
          {/* Score Card */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs flex flex-wrap items-center justify-between gap-6">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-[#167D9A]">
                {readiness.score_label}
              </div>
              <div className="text-4xl font-bold text-[#123B5D] mt-1">
                {readiness.percentage !== null ? `${readiness.percentage.toFixed(0)}%` : 'Not assessed'}
              </div>
              <div className="text-xs text-slate-500 mt-1">
                {readiness.total_score !== null
                  ? `${readiness.total_score.toFixed(1)} / ${readiness.max_assessed_score} assessed points`
                  : 'No criteria assessed yet'}
              </div>
            </div>
            <p className="text-xs text-slate-600 max-w-md bg-slate-50 border border-slate-200 rounded-lg p-3">
              {readiness.disclaimer}
            </p>
          </div>

          {/* Checklist */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-3">
            <h2 className="text-base font-semibold text-[#123B5D]">Required Document Categories</h2>
            <div className="divide-y divide-slate-200">
              {readiness.checklist.map((item) => (
                <div key={item.category} className="py-3 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    {item.status === 'Present' && <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />}
                    {item.status === 'Needs review' && <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />}
                    {item.status === 'Missing' && <XCircle className="w-5 h-5 text-rose-600 shrink-0" />}
                    <div>
                      <div className="text-sm font-semibold text-slate-800">{item.label}</div>
                      <div className="text-xs text-slate-500">
                        {item.matched_documents.length > 0
                          ? `Matched: ${item.matched_documents.join(', ')}`
                          : 'No uploaded document matched this category'}
                      </div>
                    </div>
                  </div>
                  <span
                    className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                      item.status === 'Present'
                        ? 'bg-emerald-100 text-emerald-800'
                        : item.status === 'Needs review'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-rose-100 text-rose-800'
                    }`}
                  >
                    {item.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Score Breakdown */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-3">
            <h2 className="text-base font-semibold text-[#123B5D]">Transparent Score Breakdown</h2>
            <div className="space-y-3">
              {readiness.criteria.map((c) => (
                <div key={c.name} className="border border-slate-200 rounded-lg p-3.5 bg-slate-50">
                  <div className="flex items-center justify-between text-sm font-semibold text-[#123B5D]">
                    <span>{c.name}</span>
                    <span>
                      {c.status === 'Not assessed'
                        ? `Not assessed (weight ${c.weight})`
                        : `${c.earned?.toFixed(1)} / ${c.weight}`}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 mt-1">{c.explanation}</p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};
