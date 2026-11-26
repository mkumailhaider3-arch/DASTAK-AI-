export type ScreenId =
  | 'landing'
  | 'dashboard'
  | 'upload'
  | 'analysis'
  | 'compare'
  | 'readiness'
  | 'guidance'
  | 'reports'
  | 'about';

export type LanguageCode = 'en' | 'ur' | 'roman_ur';

export interface SessionSummary {
  id: string;
  application_type: string;
  created_at: string;
  document_count: number;
  report_count: number;
  readiness_score: number | null;
}

export interface QualityMetric {
  width: number;
  height: number;
  blur_score: number;
  brightness: number;
  contrast: number;
  warnings: string[];
  is_readable: boolean;
  explanation: string;
}

export interface ExtractedField {
  field_name: string;
  value: string;
  confidence: number | null;
  status: 'extracted' | 'Needs review' | 'corrected' | 'not_detected';
}

export interface ClassificationResult {
  status: 'trained' | 'demo_mode';
  predicted_category: string | null;
  confidence: number | null;
  model_version: string | null;
  message: string;
  selected_category: string;
}

export interface AnomalyResult {
  status: 'not_configured' | 'evaluated';
  label: string;
  score: number | null;
  explanation: string;
  heatmap_base64: string | null;
}

export interface DocumentItem {
  id: string;
  session_id: string;
  original_filename: string;
  mime_type: string;
  size_bytes: number;
  uploaded_at: string;
  preview_url: string | null;
  classification: ClassificationResult;
  ocr_text: string;
  ocr_error: string | null;
  ocr_engine: string | null;
  fields: ExtractedField[];
  quality: QualityMetric | null;
  anomaly: AnomalyResult;
  analyzed: boolean;
}

export interface FieldComparisonRow {
  field_name: string;
  values: {
    document_id: string;
    document_name: string;
    original_value: string;
    normalized_value: string;
  }[];
  status: 'Match' | 'Mismatch' | 'Near-match' | 'Missing' | 'Not detected';
  similarity: number | null;
  explanation: string;
}

export interface ChecklistItem {
  category: string;
  label: string;
  required: boolean;
  status: 'Present' | 'Missing' | 'Needs review';
  matched_documents: string[];
}

export interface ScoreCriterion {
  name: string;
  weight: number;
  earned: number | null;
  status: 'assessed' | 'Not assessed';
  explanation: string;
}

export interface ReadinessResponse {
  score_label: string;
  total_score: number | null;
  max_assessed_score: number;
  percentage: number | null;
  criteria: ScoreCriterion[];
  checklist: ChecklistItem[];
  disclaimer: string;
}

export interface AssistantResponse {
  language: LanguageCode;
  intent: string;
  answer: string;
  grounded_facts: string[];
  uncertain: boolean;
  disclaimer: string;
}

export interface DashboardStats {
  total_sessions: number;
  total_documents: number;
  total_reports: number;
  sessions: SessionSummary[];
}
