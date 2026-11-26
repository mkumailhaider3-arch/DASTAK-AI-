import React, { useRef, useState } from 'react';
import { AlertCircle, FileUp, ShieldCheck, Trash2, UploadCloud } from 'lucide-react';

interface UploadPageProps {
  onStartUpload: (applicationType: string, files: File[]) => Promise<void>;
  uploading: boolean;
  error: string | null;
}

const APPLICATION_TYPES = [
  'General Application',
  'University Admission Demo',
  'Travel / Visa Package Demo',
];

const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB
const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf'];

export const UploadPage: React.FC<UploadPageProps> = ({ onStartUpload, uploading, error }) => {
  const [applicationType, setApplicationType] = useState(APPLICATION_TYPES[0]);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [localError, setLocalError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateAndAddFiles = (incoming: FileList | null) => {
    if (!incoming) return;
    setLocalError(null);
    const valid: File[] = [];
    const errors: string[] = [];

    Array.from(incoming).forEach((file) => {
      const lower = file.name.toLowerCase();
      const hasValidExt = ALLOWED_EXTENSIONS.some((ext) => lower.endsWith(ext));
      if (!hasValidExt) {
        errors.push(`${file.name}: Unsupported file type (only JPG, PNG, PDF allowed).`);
        return;
      }
      if (file.size > MAX_FILE_SIZE_BYTES) {
        errors.push(`${file.name}: Exceeds 10 MB limit.`);
        return;
      }
      if (file.size === 0) {
        errors.push(`${file.name}: File is empty.`);
        return;
      }
      valid.push(file);
    });

    if (errors.length > 0) {
      setLocalError(errors.join(' '));
    }
    if (valid.length > 0) {
      setSelectedFiles((prev) => [...prev, ...valid]);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, idx) => idx !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedFiles.length === 0) {
      setLocalError('Please select at least one JPG, PNG, or PDF file.');
      return;
    }
    setLocalError(null);
    await onStartUpload(applicationType, selectedFiles);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[#123B5D]">New Analysis / Upload</h1>
        <p className="text-sm text-slate-600">
          Select a demo checklist and upload synthetic sample documents for pre-checking.
        </p>
      </div>

      {/* Privacy Notice */}
      <div className="bg-teal-50 border border-teal-200 rounded-xl p-4 flex items-start gap-3 text-sm text-teal-950">
        <ShieldCheck className="w-5 h-5 text-[#167D9A] shrink-0 mt-0.5" />
        <div>
          <strong>Privacy Notice:</strong> This is a local academic prototype. Do not upload real
          CNICs, passports, or sensitive personal records. Use synthetic fictional examples only. You
          can delete your session and temporary files at any time.
        </div>
      </div>

      <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-6">
        {/* Application Type */}
        <div>
          <label htmlFor="app-type" className="block text-sm font-semibold text-[#123B5D] mb-2">
            Demo Application Checklist
          </label>
          <select
            id="app-type"
            value={applicationType}
            onChange={(e) => setApplicationType(e.target.value)}
            className="w-full sm:w-96 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white"
          >
            {APPLICATION_TYPES.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        {/* Drag and drop zone */}
        <div>
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragActive(false);
              validateAndAddFiles(e.dataTransfer.files);
            }}
            onClick={() => inputRef.current?.click()}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click();
            }}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
              dragActive
                ? 'border-[#167D9A] bg-teal-50'
                : 'border-slate-300 hover:border-[#167D9A] bg-slate-50'
            }`}
          >
            <UploadCloud className="w-10 h-10 text-[#167D9A] mx-auto mb-3" />
            <p className="text-sm font-semibold text-[#123B5D]">
              Drag and drop documents here, or click to browse
            </p>
            <p className="text-xs text-slate-500 mt-1">
              Supported formats: JPG, PNG, PDF • Maximum file size: 10 MB per file
            </p>
            <input
              ref={inputRef}
              type="file"
              multiple
              accept=".jpg,.jpeg,.png,.pdf"
              onChange={(e) => validateAndAddFiles(e.target.files)}
              className="hidden"
            />
          </div>
        </div>

        {/* Errors */}
        {(localError || error) && (
          <div className="bg-rose-50 border border-rose-200 text-rose-800 rounded-lg p-3 text-sm flex items-start gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{localError || error}</span>
          </div>
        )}

        {/* Selected File List */}
        {selectedFiles.length > 0 && (
          <div className="space-y-2">
            <h2 className="text-sm font-semibold text-[#123B5D]">
              Selected Files ({selectedFiles.length})
            </h2>
            <ul className="divide-y divide-slate-200 border border-slate-200 rounded-lg">
              {selectedFiles.map((file, idx) => (
                <li key={`${file.name}-${idx}`} className="px-4 py-2.5 flex items-center justify-between text-sm">
                  <div>
                    <span className="font-medium text-slate-800">{file.name}</span>{' '}
                    <span className="text-xs text-slate-500">
                      ({(file.size / 1024).toFixed(1)} KB)
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeFile(idx)}
                    className="text-rose-600 hover:text-rose-800 p-1 rounded hover:bg-rose-50"
                    aria-label={`Remove ${file.name}`}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Upload Progress / Submit */}
        <div className="flex items-center gap-4">
          <button
            type="submit"
            disabled={uploading || selectedFiles.length === 0}
            className="inline-flex items-center gap-2 bg-[#123B5D] hover:bg-[#0E2F4B] disabled:opacity-50 text-white font-semibold px-5 py-2.5 rounded-xl transition-colors"
          >
            <FileUp className="w-4 h-4" />
            {uploading ? 'Uploading & Analyzing...' : 'Upload & Start Analysis'}
          </button>
          {uploading && (
            <span className="text-xs text-[#167D9A] font-medium">
              Validating files, running OCR and image quality checks...
            </span>
          )}
        </div>
      </form>
    </div>
  );
};
