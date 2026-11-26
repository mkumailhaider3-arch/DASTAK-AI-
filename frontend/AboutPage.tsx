import React from 'react';
import { ShieldAlert, Trash2 } from 'lucide-react';
import type { SessionSummary } from '../types';

interface AboutPageProps {
  activeSession: SessionSummary | null;
  onDeleteSession: () => void;
}

export const AboutPage: React.FC<AboutPageProps> = ({ activeSession, onDeleteSession }) => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[#123B5D]">About &amp; Privacy</h1>
        <p className="text-sm text-slate-600">
          Prototype scope, limitations, local data handling, and session cleanup.
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4 text-sm text-slate-700">
        <div className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-lg p-4 text-amber-900">
          <ShieldAlert className="w-5 h-5 shrink-0 mt-0.5" />
          <div>
            <strong>Not an Official Service:</strong> DASTAK AI is an academic prototype. It is not
            connected to NADRA or any government database, and it cannot certify legal authenticity
            or verify identity.
          </div>
        </div>

        <div>
          <h2 className="font-semibold text-[#123B5D] text-base">Data Handling &amp; Privacy</h2>
          <ul className="list-disc list-inside mt-2 space-y-1 text-slate-600">
            <li>Use synthetic fictional sample documents only; never upload real identity documents.</li>
            <li>Uploaded files are stored outside public static directories using generated UUID filenames.</li>
            <li>OCR text and personal fields are never written to application logs.</li>
            <li>
              <strong>Local Academic Storage Notice:</strong> SQLite and local disk storage are used
              for academic demonstration and are not production-grade security.
            </li>
          </ul>
        </div>

        {activeSession && (
          <div className="border-t border-slate-200 pt-4 flex items-center justify-between gap-4">
            <div>
              <div className="font-semibold text-[#123B5D]">Active Session Cleanup</div>
              <div className="text-xs text-slate-500">
                Permanently delete session {activeSession.id.slice(0, 8)} and all temporary files.
              </div>
            </div>
            <button
              type="button"
              onClick={onDeleteSession}
              className="inline-flex items-center gap-2 bg-rose-700 hover:bg-rose-800 text-white text-xs font-semibold px-4 py-2 rounded-lg"
            >
              <Trash2 className="w-4 h-4" />
              Delete This Session
            </button>
          </div>
        )}

        <div className="border-t border-slate-200 pt-4 text-xs text-slate-500">
          Contact / Project Info Placeholder: DASTAK AI Academic Capstone Team • Local Prototype v0.1
        </div>
      </div>
    </div>
  );
};
