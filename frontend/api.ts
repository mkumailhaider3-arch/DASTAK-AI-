import type {
  AssistantResponse,
  DashboardStats,
  DocumentItem,
  FieldComparisonRow,
  LanguageCode,
  ReadinessResponse,
  SessionSummary,
} from '../types';

const API_BASE = '/api';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      if (data?.detail) {
        detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      }
    } catch {
      // ignore json parse errors
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export async function checkHealth(): Promise<{ status: string; ocr_engine: string; classifier_status: string }> {
  const res = await fetch(`${API_BASE}/health`);
  return handleResponse(res);
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const res = await fetch(`${API_BASE}/sessions`);
  return handleResponse(res);
}

export async function createSession(applicationType: string): Promise<SessionSummary> {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ application_type: applicationType }),
  });
  return handleResponse(res);
}

export async function deleteSession(sessionId: string): Promise<{ deleted: boolean; message: string }> {
  const res = await fetch(`${API_BASE}/sessions/${encodeURIComponent(sessionId)}`, {
    method: 'DELETE',
  });
  return handleResponse(res);
}

export async function uploadDocuments(sessionId: string, files: File[]): Promise<DocumentItem[]> {
  const formData = new FormData();
  files.forEach((f) => formData.append('files', f));
  const res = await fetch(`${API_BASE}/sessions/${encodeURIComponent(sessionId)}/documents`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(res);
}

export async function getSessionDocuments(sessionId: string): Promise<DocumentItem[]> {
  const res = await fetch(`${API_BASE}/sessions/${encodeURIComponent(sessionId)}/documents`);
  return handleResponse(res);
}

export async function analyzeDocument(documentId: string): Promise<DocumentItem> {
  const res = await fetch(`${API_BASE}/documents/${encodeURIComponent(documentId)}/analyze`, {
    method: 'POST',
  });
  return handleResponse(res);
}

export async function updateDocumentFields(
  documentId: string,
  selectedCategory: string,
  fields: { field_name: string; value: string }[],
): Promise<DocumentItem> {
  const res = await fetch(`${API_BASE}/documents/${encodeURIComponent(documentId)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ selected_category: selectedCategory, fields }),
  });
  return handleResponse(res);
}

export async function compareDocuments(
  sessionId: string,
  fieldNames: string[],
  fuzzyThreshold = 0.85,
): Promise<{ comparisons: FieldComparisonRow[] }> {
  const res = await fetch(`${API_BASE}/sessions/${encodeURIComponent(sessionId)}/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ field_names: fieldNames, fuzzy_threshold: fuzzyThreshold }),
  });
  return handleResponse(res);
}

export async function getReadiness(sessionId: string): Promise<ReadinessResponse> {
  const res = await fetch(`${API_BASE}/sessions/${encodeURIComponent(sessionId)}/readiness`);
  return handleResponse(res);
}

export async function askAssistant(
  sessionId: string | null,
  question: string,
  language: LanguageCode,
): Promise<AssistantResponse> {
  const res = await fetch(`${API_BASE}/assistant/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, question, language }),
  });
  return handleResponse(res);
}

export function getReportDownloadUrl(sessionId: string, includeFullOcr: boolean): string {
  return `${API_BASE}/sessions/${encodeURIComponent(sessionId)}/report?include_full_ocr=${includeFullOcr ? 'true' : 'false'}`;
}
