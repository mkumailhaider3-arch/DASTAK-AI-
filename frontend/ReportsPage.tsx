import React, { useState } from 'react';
import { Download, FileText } from 'lucide-react';
import { getReportDownloadUrl } from '../services/api';
import type { DocumentItem, FieldComparisonRow, ReadinessResponse, SessionSummary } from '../types';

interface ReportsPageProps {
  session: SessionSummary | null;
  documents: DocumentItem[];
  comparisons: FieldComparisonRow[];
  readiness: ReadinessResponse | null;
}

export const ReportsPage: React.FC<ReportsPageProps> = ({
  session,
  documents,
  comparisons,
  readiness,
}) => {
  const [includeFullOcr, setIncludeFullOcr] = useState(false);

  if (!session) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-10 text-center shadow-xs">
        <FileText className="w-10 h-10 text-slate-400 mx-auto mb-3" />
        <h1 className="text-lg font-semibold text-[#123B5D]">No Active Session</h1>
        <p className="text-sm text-slate-600 mt-1">
          Start or open a session to preview and download the PDF analysis report.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#123B5D]">Reports</h1>
          <p className="text-sm text-slate-600">
            Preview your session summary and download a PDF report with prototype disclaimers.
          </p>
        </div>
        <a
          href={getReportDownloadUrl(session.id, includeFullOcr)}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 bg-[#123B5D] hover:bg-[#0E2F4B] text-white text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors"
        >
          <Download className="w-4 h-4" />
          Download PDF Report
        </a>
      </div>

      {/* Privacy Option */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs flex items-center justify-between gap-4">
        <label className="inline-flex items-center gap-2.5 text-sm text-slate-700 cursor-pointer">
          <input
            type="checkbox"
            checked={includeFullOcr}
            onChange={(e) => setIncludeFullOcr(e.target.checked)}
            className="rounded border-slate-300 text-[#167D9A]"
          />
          <span>
            Include full raw OCR text in PDF (off by default to avoid exposing sensitive text)
          </span>
        </label>
      </div>

      {/* Report Preview Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-5 text-sm">
        <div className="border-b border-slate-200 pb-4">
          <div className="text-xs font-semibold uppercase tracking-wider text-[#167D9A]">
            DASTAK AI • Pre-Check Summary Preview
          </div>
          <h2 className="text-xl font-bold text-[#123B5D] mt-1">{session.application_type}</h2>
          <div className="text-xs text-slate-500 mt-1">
            Session ID: {session.id} • Generated: {new Date().toLocaleString()}
          </div>
        </div>

        <div>
          <h3 className="font-semibold text-[#123B5D] mb-2">
            Files Analysed ({documents.length})
          </h3>
          <ul className="list-disc list-inside text-slate-700 space-y-1 text-xs">
            {documents.map((d) => (
              <li key={d.id}>
                {d.original_filename} — Category: {d.classification.selected_category} — Quality:{' '}
                {d.quality ? (d.quality.is_readable ? 'Readable' : 'Warnings') : 'Not assessed'}
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="font-semibold text-[#123B5D] mb-2">Prototype Readiness Score</h3>
          <p className="text-slate-700 text-xs">
            {readiness?.percentage !== null && readiness?.percentage !== undefined
              ? `${readiness.percentage.toFixed(1)}% (${readiness.total_score?.toFixed(1)} / ${readiness.max_assessed_score} assessed points)`
              : 'Not assessed yet'}
          </p>
        </div>

        {comparisons.length > 0 && (
          <div>
            <h3 className="font-semibold text-[#123B5D] mb-2">Field Comparisons</h3>
            <ul className="list-disc list-inside text-xs text-slate-700 space-y-1">
              {comparisons.map((c) => (
                <li key={c.field_name}>
                  <strong>{c.field_name}:</strong> {c.status} — {c.explanation}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-900">
          <strong>Limitations:</strong> Academic prototype only. Not NADRA or an official
          government service. Does not certify legal authenticity or verify identity.
        </div>
      </div>
    </div>
  );
};
