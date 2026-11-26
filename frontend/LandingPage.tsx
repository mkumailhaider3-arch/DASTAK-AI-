import React from 'react';
import { ArrowRight, CheckCircle2, FileCheck2, Languages, ShieldAlert } from 'lucide-react';
import type { ScreenId } from '../types';

interface LandingPageProps {
  onStart: () => void;
  onNavigate: (screen: ScreenId) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onStart, onNavigate }) => {
  return (
    <div className="space-y-6">
      {/* Hero Card */}
      <section className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-10 shadow-xs">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-50 text-[#167D9A] text-xs font-semibold mb-4 border border-teal-200">
          Academic Pre-Checking Prototype
        </div>
        <h1 className="text-3xl sm:text-4xl font-bold text-[#123B5D] tracking-tight">
          DASTAK AI
        </h1>
        <p className="text-lg text-[#167D9A] font-medium mt-1">
          Smart Documents, Secure Future.
        </p>
        <p className="mt-4 text-slate-600 max-w-2xl leading-relaxed">
          Organise your document package and spot potential issues — such as blurry scans, missing
          documents, or mismatched names and dates — before a human or official authority reviews
          your application.
        </p>

        <div className="mt-6 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={onStart}
            className="inline-flex items-center gap-2 bg-[#123B5D] hover:bg-[#0E2F4B] text-white font-semibold px-5 py-3 rounded-xl transition-colors shadow-xs"
          >
            Start Checking Documents
            <ArrowRight className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={() => onNavigate('dashboard')}
            className="inline-flex items-center gap-2 bg-white hover:bg-slate-50 text-[#123B5D] border border-slate-300 font-semibold px-5 py-3 rounded-xl transition-colors"
          >
            Open Dashboard
          </button>
        </div>
      </section>

      {/* Prominent Academic Disclaimer */}
      <section className="bg-amber-50 border border-amber-200 rounded-xl p-5 flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
        <div className="text-sm text-amber-900 space-y-1">
          <div className="font-semibold">Important Academic Prototype Disclaimer</div>
          <p>
            DASTAK AI is an academic prototype only. It is <strong>not NADRA</strong>, is not
            connected to any government database, and does not verify identity or certify legal
            authenticity. All labels such as <em>Match</em>, <em>Mismatch</em>, or{' '}
            <em>Needs Human Review</em> are pre-checking aids, not official decisions.
          </p>
        </div>
      </section>

      {/* Capabilities Grid */}
      <section className="grid sm:grid-cols-3 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <FileCheck2 className="w-6 h-6 text-[#167D9A] mb-3" />
          <h2 className="font-semibold text-[#123B5D]">OCR &amp; Quality Checks</h2>
          <p className="text-sm text-slate-600 mt-1">
            Extracts visible text for review and runs OpenCV heuristic checks for blur, low
            resolution, brightness, and contrast.
          </p>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <CheckCircle2 className="w-6 h-6 text-[#167D9A] mb-3" />
          <h2 className="font-semibold text-[#123B5D]">Cross-Document Matching</h2>
          <p className="text-sm text-slate-600 mt-1">
            Compares selected fields across documents transparently and calculates an explainable
            Prototype Readiness Score.
          </p>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <Languages className="w-6 h-6 text-[#167D9A] mb-3" />
          <h2 className="font-semibold text-[#123B5D]">Multilingual Guidance</h2>
          <p className="text-sm text-slate-600 mt-1">
            Explains checklist findings and next steps in English, Urdu, and Roman Urdu, plus
            generates downloadable PDF reports.
          </p>
        </div>
      </section>
    </div>
  );
};
