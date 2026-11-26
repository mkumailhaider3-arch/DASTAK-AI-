import { useCallback, useEffect, useState } from 'react';
import { Layout } from './components/Layout';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { UploadPage } from './pages/UploadPage';
import { DocumentAnalysisPage } from './pages/DocumentAnalysisPage';
import { ComparePage } from './pages/ComparePage';
import { ReadinessPage } from './pages/ReadinessPage';
import { GuidancePage } from './pages/GuidancePage';
import { ReportsPage } from './pages/ReportsPage';
import { AboutPage } from './pages/AboutPage';
import * as api from './services/api';
import type {
  DashboardStats,
  DocumentItem,
  FieldComparisonRow,
  LanguageCode,
  ReadinessResponse,
  ScreenId,
  SessionSummary,
} from './types';

const EMPTY_STATS: DashboardStats = {
  total_sessions: 0,
  total_documents: 0,
  total_reports: 0,
  sessions: [],
};

export function App() {
  const [activeScreen, setActiveScreen] = useState<ScreenId>('landing');
  const [backendConnected, setBackendConnected] = useState<boolean | null>(null);
  const [stats, setStats] = useState<DashboardStats>(EMPTY_STATS);
  const [loadingStats, setLoadingStats] = useState(false);

  const [activeSession, setActiveSession] = useState<SessionSummary | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [comparisons, setComparisons] = useState<FieldComparisonRow[]>([]);
  const [readiness, setReadiness] = useState<ReadinessResponse | null>(null);

  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [readinessLoading, setReadinessLoading] = useState(false);

  const refreshDashboard = useCallback(async () => {
    setLoadingStats(true);
    try {
      const data = await api.getDashboardStats();
      setStats(data);
      setBackendConnected(true);
    } catch {
      setBackendConnected(false);
    } finally {
      setLoadingStats(false);
    }
  }, []);

  useEffect(() => {
    api
      .checkHealth()
      .then(() => {
        setBackendConnected(true);
        void refreshDashboard();
      })
      .catch(() => setBackendConnected(false));
  }, [refreshDashboard]);

  const loadSessionData = async (session: SessionSummary) => {
    setActiveSession(session);
    const docs = await api.getSessionDocuments(session.id);
    setDocuments(docs);
    setComparisons([]);
    try {
      const r = await api.getReadiness(session.id);
      setReadiness(r);
    } catch {
      setReadiness(null);
    }
  };

  const handleStartUpload = async (applicationType: string, files: File[]) => {
    setUploading(true);
    setUploadError(null);
    try {
      const session = await api.createSession(applicationType);
      const uploaded = await api.uploadDocuments(session.id, files);
      const analyzedDocs: DocumentItem[] = [];
      for (const doc of uploaded) {
        const res = await api.analyzeDocument(doc.id);
        analyzedDocs.push(res);
      }
      setActiveSession(session);
      setDocuments(analyzedDocs);
      const r = await api.getReadiness(session.id);
      setReadiness(r);
      await refreshDashboard();
      setActiveScreen('analysis');
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyzeDoc = async (docId: string) => {
    const updated = await api.analyzeDocument(docId);
    setDocuments((prev) => prev.map((d) => (d.id === docId ? updated : d)));
    if (activeSession) {
      const r = await api.getReadiness(activeSession.id);
      setReadiness(r);
    }
  };

  const handleSaveCorrections = async (
    docId: string,
    selectedCategory: string,
    fields: { field_name: string; value: string }[],
  ) => {
    const updated = await api.updateDocumentFields(docId, selectedCategory, fields);
    setDocuments((prev) => prev.map((d) => (d.id === docId ? updated : d)));
    if (activeSession) {
      const r = await api.getReadiness(activeSession.id);
      setReadiness(r);
    }
  };

  const handleCompare = async (fields: string[]) => {
    if (!activeSession) return;
    const res = await api.compareDocuments(activeSession.id, fields);
    setComparisons(res.comparisons);
    const r = await api.getReadiness(activeSession.id);
    setReadiness(r);
  };

  const handleRefreshReadiness = async () => {
    if (!activeSession) return;
    setReadinessLoading(true);
    try {
      const r = await api.getReadiness(activeSession.id);
      setReadiness(r);
    } finally {
      setReadinessLoading(false);
    }
  };

  const handleDeleteSession = async (sessionId?: string) => {
    const targetId = sessionId ?? activeSession?.id;
    if (!targetId) return;
    await api.deleteSession(targetId);
    if (activeSession?.id === targetId) {
      setActiveSession(null);
      setDocuments([]);
      setComparisons([]);
      setReadiness(null);
    }
    await refreshDashboard();
  };

  const handleAskAssistant = async (question: string, language: LanguageCode) => {
    return api.askAssistant(activeSession?.id ?? null, question, language);
  };

  return (
    <Layout
      activeScreen={activeScreen}
      onNavigate={setActiveScreen}
      activeSession={activeSession}
      onDeleteSession={() => void handleDeleteSession()}
      backendConnected={backendConnected}
    >
      {activeScreen === 'landing' && (
        <LandingPage onStart={() => setActiveScreen('upload')} onNavigate={setActiveScreen} />
      )}
      {activeScreen === 'dashboard' && (
        <DashboardPage
          stats={stats}
          loading={loadingStats}
          onNewAnalysis={() => setActiveScreen('upload')}
          onOpenSession={(s) => {
            void loadSessionData(s).then(() => setActiveScreen('analysis'));
          }}
          onDeleteSession={(id) => void handleDeleteSession(id)}
        />
      )}
      {activeScreen === 'upload' && (
        <UploadPage
          onStartUpload={handleStartUpload}
          uploading={uploading}
          error={uploadError}
        />
      )}
      {activeScreen === 'analysis' && (
        <DocumentAnalysisPage
          documents={documents}
          onAnalyze={handleAnalyzeDoc}
          onSaveCorrections={handleSaveCorrections}
          onGoUpload={() => setActiveScreen('upload')}
        />
      )}
      {activeScreen === 'compare' && (
        <ComparePage
          documents={documents}
          comparisons={comparisons}
          onCompare={handleCompare}
          onGoUpload={() => setActiveScreen('upload')}
        />
      )}
      {activeScreen === 'readiness' && (
        <ReadinessPage
          readiness={readiness}
          onRefresh={handleRefreshReadiness}
          loading={readinessLoading}
        />
      )}
      {activeScreen === 'guidance' && <GuidancePage onAsk={handleAskAssistant} />}
      {activeScreen === 'reports' && (
        <ReportsPage
          session={activeSession}
          documents={documents}
          comparisons={comparisons}
          readiness={readiness}
        />
      )}
      {activeScreen === 'about' && (
        <AboutPage
          activeSession={activeSession}
          onDeleteSession={() => void handleDeleteSession()}
        />
      )}
    </Layout>
  );
}

export default App;
