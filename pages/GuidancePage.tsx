import React, { useState } from 'react';
import { Compass, Send } from 'lucide-react';
import type { AssistantResponse, LanguageCode } from '../types';

interface GuidancePageProps {
  onAsk: (question: string, language: LanguageCode) => Promise<AssistantResponse>;
}

const QUICK_PROMPTS: { label: string; question: string }[] = [
  { label: 'Missing Document', question: 'Why is a document marked missing in my checklist?' },
  { label: 'Field Mismatch', question: 'What does a field mismatch mean and how do I fix it?' },
  { label: 'Blurry Image', question: 'Why did my document get a blur or readability warning?' },
  { label: 'Readiness Score', question: 'How is my prototype readiness score calculated?' },
  { label: 'Next Step', question: 'What should my next step be?' },
];

export const GuidancePage: React.FC<GuidancePageProps> = ({ onAsk }) => {
  const [language, setLanguage] = useState<LanguageCode>('en');
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<AssistantResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const submitQuestion = async (q: string) => {
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await onAsk(q, language);
      setResponse(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get guidance');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[#123B5D]">AI Guidance Assistant</h1>
        <p className="text-sm text-slate-600">
          Grounded in your current session analysis and curated FAQ knowledge base. Does not provide legal advice.
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-5">
        {/* Language Selector */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm font-semibold text-[#123B5D] mr-2">Language:</span>
          {[
            { id: 'en' as LanguageCode, label: 'English' },
            { id: 'roman_ur' as LanguageCode, label: 'Roman Urdu' },
            { id: 'ur' as LanguageCode, label: 'اردو (Urdu)' },
          ].map((lang) => (
            <button
              key={lang.id}
              type="button"
              onClick={() => setLanguage(lang.id)}
              className={`px-3.5 py-1.5 rounded-lg text-sm font-medium border transition-colors ${
                language === lang.id
                  ? 'bg-[#123B5D] text-white border-[#123B5D]'
                  : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
              }`}
            >
              {lang.label}
            </button>
          ))}
        </div>

        {/* Quick Prompts */}
        <div className="flex flex-wrap gap-2">
          {QUICK_PROMPTS.map((p) => (
            <button
              key={p.label}
              type="button"
              onClick={() => {
                setQuestion(p.question);
                void submitQuestion(p.question);
              }}
              className="text-xs font-medium bg-slate-100 hover:bg-teal-50 hover:text-[#167D9A] text-slate-700 px-3 py-1.5 rounded-full border border-slate-200 transition-colors"
            >
              {p.label}
            </button>
          ))}
        </div>

        {/* Input */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            void submitQuestion(question);
          }}
          className="flex gap-2"
        >
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask about missing documents, mismatches, blur warnings, or next steps..."
            className="flex-1 border border-slate-300 rounded-xl px-4 py-2.5 text-sm"
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="inline-flex items-center gap-2 bg-[#167D9A] hover:bg-[#12667E] disabled:opacity-50 text-white text-sm font-semibold px-4 py-2.5 rounded-xl"
          >
            <Send className="w-4 h-4" />
            Ask
          </button>
        </form>

        {error && (
          <div className="text-sm text-rose-800 bg-rose-50 border border-rose-200 rounded-lg p-3">
            {error}
          </div>
        )}

        {response && (
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-500">
              <span className="inline-flex items-center gap-1.5 font-semibold text-[#123B5D]">
                <Compass className="w-4 h-4 text-[#167D9A]" />
                Intent: {response.intent}
              </span>
              {response.uncertain && (
                <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-semibold">
                  Uncertain / General Guidance
                </span>
              )}
            </div>
            <p
              dir={response.language === 'ur' ? 'rtl' : 'ltr'}
              className="text-sm text-slate-800 leading-relaxed whitespace-pre-line"
            >
              {response.answer}
            </p>
            {response.grounded_facts.length > 0 && (
              <div className="text-xs text-slate-600 border-t border-slate-200 pt-2">
                <div className="font-semibold mb-1">Grounded in current session:</div>
                <ul className="list-disc list-inside space-y-0.5">
                  {response.grounded_facts.map((fact, idx) => (
                    <li key={idx}>{fact}</li>
                  ))}
                </ul>
              </div>
            )}
            <div className="text-[11px] text-slate-500 border-t border-slate-200 pt-2">
              {response.disclaimer}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
