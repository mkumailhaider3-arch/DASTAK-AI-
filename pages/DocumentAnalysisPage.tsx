import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, Cpu, Eye, Play, Save, ShieldAlert } from 'lucide-react';
import type { DocumentItem } from '../types';

interface DocumentAnalysisPageProps {
  documents: DocumentItem[];
  onAnalyze: (docId: string) => Promise<void>;
  onSaveCorrections: (
    docId: string,
    selectedCategory: string,
    fields: { field_name: string; value: string }[],
  ) => Promise<void>;
  onGoUpload: () => void;
}

const CATEGORIES = [
  { id: 'identity-card-style sample', label: 'Identity-card-style sample' },
  { id: 'passport-style sample', label: 'Passport-style sample' },
  { id: 'educational certificate', label: 'Educational certificate' },
  { id: 'application form', label: 'Application form' },
  { id: 'receipt/other', label: 'Receipt / Other' },
];

export const DocumentAnalysisPage: React.FC<DocumentAnalysisPageProps> = ({
  documents,
  onAnalyze,
  onSaveCorrections,
  onGoUpload,
}) => {
  const [selectedId, setSelectedId] = useState<string | null>(documents[0]?.id ?? null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [categoryDraft, setCategoryDraft] = useState('');
  const [fieldDrafts, setFieldDrafts] = useState<Record<string, string>>({});
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  const activeDoc = documents.find((d) => d.id === selectedId) ?? documents[0] ?? null;

  useEffect(() => {
    if (activeDoc) {
      setSelectedId(activeDoc.id);
      setCategoryDraft(activeDoc.classification.selected_category || 'receipt/other');
      const map: Record<string, string> = {};
      activeDoc.fields.forEach((f) => {
        map[f.field_name] = f.value;
      });
      setFieldDrafts(map);
      setSaveMessage(null);
    }
  }, [activeDoc?.id, activeDoc?.analyzed, activeDoc?.fields]);

  if (documents.length === 0 || !activeDoc) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-10 text-center shadow-xs">
        <Eye className="w-10 h-10 text-slate-400 mx-auto mb-3" />
        <h1 className="text-lg font-semibold text-[#123B5D]">No Documents in Session</h1>
        <p className="text-sm text-slate-600 mt-1">
          Upload synthetic sample documents first to preview OCR, image quality, and classification.
        </p>
        <button
          type="button"
          onClick={onGoUpload}
          className="mt-4 bg-[#123B5D] hover:bg-[#0E2F4B] text-white text-sm font-semibold px-4 py-2 rounded-lg"
        >
          Go to Upload
        </button>
      </div>
    );
  }

  const handleAnalyze = async () => {
    setBusyId(activeDoc.id);
    try {
      await onAnalyze(activeDoc.id);
    } finally {
      setBusyId(null);
    }
  };

  const handleSave = async () => {
    setBusyId(activeDoc.id);
    setSaveMessage(null);
    try {
      const fieldsPayload = Object.entries(fieldDrafts).map(([field_name, value]) => ({
        field_name,
        value,
      }));
      await onSaveCorrections(activeDoc.id, categoryDraft, fieldsPayload);
      setSaveMessage('Saved category and field corrections.');
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#123B5D]">Document Analysis</h1>
          <p className="text-sm text-slate-600">
            Review document classification, OCR text, editable fields, and image readability heuristics.
          </p>
        </div>
        <button
          type="button"
          onClick={handleAnalyze}
          disabled={busyId === activeDoc.id}
          className="inline-flex items-center gap-2 bg-[#167D9A] hover:bg-[#12667E] disabled:opacity-50 text-white text-sm font-semibold px-4 py-2 rounded-xl transition-colors"
        >
          <Play className="w-4 h-4" />
          {busyId === activeDoc.id ? 'Analyzing...' : activeDoc.analyzed ? 'Re-run Analysis' : 'Run Analysis'}
        </button>
      </div>

      {/* Document Tabs */}
      <div className="flex flex-wrap gap-2">
        {documents.map((doc) => (
          <button
            key={doc.id}
            type="button"
            onClick={() => setSelectedId(doc.id)}
            className={`px-3.5 py-2 rounded-lg text-sm font-medium border transition-colors ${
              doc.id === activeDoc.id
                ? 'bg-[#123B5D] text-white border-[#123B5D]'
                : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
            }`}
          >
            {doc.original_filename}
          </button>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left: Preview & Classification & Quality */}
        <div className="space-y-6">
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
            <h2 className="text-sm font-semibold text-[#123B5D] mb-3">Document Preview</h2>
            {activeDoc.preview_url ? (
              <img
                src={activeDoc.preview_url}
                alt={`Preview of ${activeDoc.original_filename}`}
                className="w-full max-h-80 object-contain rounded-lg border border-slate-200 bg-slate-50"
              />
            ) : (
              <div className="h-48 flex items-center justify-center bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-500">
                Preview unavailable until processed.
              </div>
            )}
          </div>

          {/* Classification */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-[#123B5D] flex items-center gap-2">
                <Cpu className="w-4 h-4 text-[#167D9A]" />
                Document Classification
              </h2>
              {activeDoc.classification.status === 'demo_mode' ? (
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800">
                  Model not trained — demo mode
                </span>
              ) : (
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-teal-100 text-[#167D9A]">
                  Model {activeDoc.classification.model_version}
                </span>
              )}
            </div>

            <p className="text-xs text-slate-600">{activeDoc.classification.message}</p>

            {activeDoc.classification.status === 'trained' && activeDoc.classification.predicted_category && (
              <div className="text-sm bg-slate-50 border border-slate-200 rounded-lg p-3">
                Predicted: <strong>{activeDoc.classification.predicted_category}</strong>{' '}
                {activeDoc.classification.confidence !== null && (
                  <span className="text-slate-500">
                    ({(activeDoc.classification.confidence * 100).toFixed(1)}% confidence)
                  </span>
                )}
              </div>
            )}

            <div>
              <label htmlFor="doc-cat" className="block text-xs font-medium text-slate-600 mb-1">
                Selected Category (Manual override / Demo mode)
              </label>
              <select
                id="doc-cat"
                value={categoryDraft}
                onChange={(e) => setCategoryDraft(e.target.value)}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white"
              >
                {CATEGORIES.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Image Quality */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-3">
            <h2 className="text-sm font-semibold text-[#123B5D]">Image Quality Assessment (Heuristic)</h2>
            {activeDoc.quality ? (
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  {activeDoc.quality.is_readable ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                  )}
                  <span className="font-medium">
                    {activeDoc.quality.is_readable ? 'Readable (Heuristic Pass)' : 'Needs Review (Quality Warning)'}
                  </span>
                </div>
                <p className="text-xs text-slate-600">{activeDoc.quality.explanation}</p>
                <div className="grid grid-cols-2 gap-2 text-xs bg-slate-50 p-3 rounded-lg border border-slate-200">
                  <div>Dimensions: {activeDoc.quality.width} x {activeDoc.quality.height}px</div>
                  <div>Blur (Laplacian): {activeDoc.quality.blur_score.toFixed(1)}</div>
                  <div>Brightness: {activeDoc.quality.brightness.toFixed(1)}</div>
                  <div>Contrast: {activeDoc.quality.contrast.toFixed(1)}</div>
                </div>
                {activeDoc.quality.warnings.length > 0 && (
                  <ul className="list-disc list-inside text-xs text-amber-800 bg-amber-50 p-2.5 rounded-lg border border-amber-200">
                    {activeDoc.quality.warnings.map((w, i) => (
                      <li key={i}>{w}</li>
                    ))}
                  </ul>
                )}
              </div>
            ) : (
              <p className="text-xs text-slate-500">Run analysis to assess image readability.</p>
            )}
          </div>

          {/* Experimental Visual Anomaly Screening */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-2">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-[#123B5D] flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-slate-500" />
                Visual Anomaly Screening (Experimental)
              </h2>
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700">
                {activeDoc.anomaly.label}
              </span>
            </div>
            <p className="text-xs text-slate-600">{activeDoc.anomaly.explanation}</p>
          </div>
        </div>

        {/* Right: OCR & Editable Fields */}
        <div className="space-y-6">
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-[#123B5D]">Extracted Fields (Editable)</h2>
              <button
                type="button"
                onClick={handleSave}
                disabled={busyId === activeDoc.id}
                className="inline-flex items-center gap-1.5 bg-[#123B5D] hover:bg-[#0E2F4B] text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors"
              >
                <Save className="w-3.5 h-3.5" />
                Save Corrections
              </button>
            </div>

            {saveMessage && (
              <div className="text-xs text-emerald-800 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
                {saveMessage}
              </div>
            )}

            <div className="space-y-3">
              {activeDoc.fields.map((field) => (
                <div key={field.field_name} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <label
                      htmlFor={`field-${field.field_name}`}
                      className="text-xs font-semibold text-slate-700 capitalize"
                    >
                      {field.field_name.replace(/_/g, ' ')}
                    </label>
                    <span
                      className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                        field.status === 'Needs review'
                          ? 'bg-amber-100 text-amber-800'
                          : field.status === 'corrected'
                            ? 'bg-teal-100 text-[#167D9A]'
                            : field.status === 'extracted'
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {field.status}
                    </span>
                  </div>
                  <input
                    id={`field-${field.field_name}`}
                    type="text"
                    value={fieldDrafts[field.field_name] ?? ''}
                    onChange={(e) =>
                      setFieldDrafts((prev) => ({ ...prev, [field.field_name]: e.target.value }))
                    }
                    placeholder="Not detected — enter manually if needed"
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
                  />
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-2">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-[#123B5D]">Raw OCR Text Preview</h2>
              {activeDoc.ocr_engine && (
                <span className="text-xs text-slate-500">Engine: {activeDoc.ocr_engine}</span>
              )}
            </div>
            {activeDoc.ocr_error ? (
              <div className="text-xs text-rose-800 bg-rose-50 border border-rose-200 rounded-lg p-3">
                OCR Error: {activeDoc.ocr_error}
              </div>
            ) : (
              <pre className="text-xs bg-slate-50 border border-slate-200 rounded-lg p-3 whitespace-pre-wrap max-h-64 overflow-y-auto font-mono text-slate-700">
                {activeDoc.ocr_text || 'No text extracted yet. Click "Run Analysis".'}
              </pre>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
