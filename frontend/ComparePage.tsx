import React, { useState } from 'react';
import { GitCompare } from 'lucide-react';
import type { DocumentItem, FieldComparisonRow } from '../types';

interface ComparePageProps {
  documents: DocumentItem[];
  comparisons: FieldComparisonRow[];
  onCompare: (fields: string[]) => Promise<void>;
  onGoUpload: () => void;
}

const AVAILABLE_FIELDS = [
  { id: 'full_name', label: 'Full Name' },
  { id: 'date_of_birth', label: 'Date of Birth' },
  { id: 'id_number', label: 'Document / ID Number' },
  { id: 'document_date', label: 'Issue / Document Date' },
];

export const ComparePage: React.FC<ComparePageProps> = ({
  documents,
  comparisons,
  onCompare,
  onGoUpload,
}) => {
  const [selectedFields, setSelectedFields] = useState<string[]>(['full_name', 'date_of_birth', 'id_number']);
  const [loading, setLoading] = useState(false);

  const toggleField = (fieldId: string) => {
    setSelectedFields((prev) =>
      prev.includes(fieldId) ? prev.filter((f) => f !== fieldId) : [...prev, fieldId],
    );
  };

  const handleRun = async () => {
    if (selectedFields.length === 0) return;
    setLoading(true);
    try {
      await onCompare(selectedFields);
    } finally {
      setLoading(false);
    }
  };

  if (documents.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-10 text-center shadow-xs">
        <GitCompare className="w-10 h-10 text-slate-400 mx-auto mb-3" />
        <h1 className="text-lg font-semibold text-[#123B5D]">No Documents to Compare</h1>
        <p className="text-sm text-slate-600 mt-1">Upload at least two documents to compare fields side by side.</p>
        <button
          type="button"
          onClick={onGoUpload}
          className="mt-4 bg-[#123B5D] text-white text-sm font-semibold px-4 py-2 rounded-lg"
        >
          Go to Upload
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[#123B5D]">Compare Documents</h1>
        <p className="text-sm text-slate-600">
          Side-by-side comparison showing both original extracted values and normalized text.
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
        <div className="text-sm font-semibold text-[#123B5D]">Select Fields to Compare</div>
        <div className="flex flex-wrap gap-4">
          {AVAILABLE_FIELDS.map((f) => (
            <label key={f.id} className="inline-flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={selectedFields.includes(f.id)}
                onChange={() => toggleField(f.id)}
                className="rounded border-slate-300 text-[#167D9A]"
              />
              <span>{f.label}</span>
            </label>
          ))}
        </div>
        <button
          type="button"
          onClick={handleRun}
          disabled={loading || selectedFields.length === 0}
          className="inline-flex items-center gap-2 bg-[#123B5D] hover:bg-[#0E2F4B] disabled:opacity-50 text-white text-sm font-semibold px-4 py-2 rounded-xl transition-colors"
        >
          <GitCompare className="w-4 h-4" />
          {loading ? 'Comparing...' : 'Compare Selected Fields'}
        </button>
      </div>

      {comparisons.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-slate-50 border-b border-slate-200 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-4 py-3">Field</th>
                  <th className="px-4 py-3">Document Values (Original &amp; Normalized)</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Explanation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {comparisons.map((row) => (
                  <tr key={row.field_name} className="align-top">
                    <td className="px-4 py-3 font-semibold text-[#123B5D] capitalize">
                      {row.field_name.replace(/_/g, ' ')}
                    </td>
                    <td className="px-4 py-3 space-y-1.5">
                      {row.values.map((v) => (
                        <div key={v.document_id} className="text-xs bg-slate-50 border border-slate-200 rounded p-2">
                          <div className="font-semibold text-slate-700">{v.document_name}</div>
                          <div>Original: <span className="font-mono">{v.original_value || '—'}</span></div>
                          <div className="text-slate-500">
                            Normalized: <span className="font-mono">{v.normalized_value || '—'}</span>
                          </div>
                        </div>
                      ))}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-block text-xs font-semibold px-2.5 py-1 rounded-full ${
                          row.status === 'Match'
                            ? 'bg-emerald-100 text-emerald-800'
                            : row.status === 'Mismatch'
                              ? 'bg-rose-100 text-rose-800'
                              : row.status === 'Near-match'
                                ? 'bg-amber-100 text-amber-800'
                                : 'bg-slate-100 text-slate-700'
                        }`}
                      >
                        {row.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-600">{row.explanation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
