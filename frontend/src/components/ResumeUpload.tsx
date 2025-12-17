'use client'

import { useState, useRef } from 'react'

interface ResumeUploadProps {
  onUploaded: (resumeId: number) => void
}

export default function ResumeUpload({ onUploaded }: ResumeUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [resumeData, setResumeData] = useState<any>(null)
  const [dragActive, setDragActive] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }

    setUploading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/resumes/upload`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Upload failed')
      }

      const data = await response.json()
      setResumeData(data)
      onUploaded(data.id)
    } catch (err: any) {
      setError(err.message || 'Failed to upload resume')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-[var(--text-primary)]">
          Upload Resume
        </h2>
        <p className="text-[var(--text-secondary)] text-sm mt-1">
          Upload your resume to extract skills and qualifications
        </p>
      </div>

      {/* Drop Zone */}
      <div
        className={`file-input-wrapper ${dragActive ? 'border-[var(--text-muted)] bg-[var(--bg-tertiary)]' : ''} ${file ? 'has-file' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.txt"
          onChange={handleFileChange}
          className="hidden"
        />
        
        {file ? (
          <>
            <svg className="w-10 h-10 text-[var(--success)] mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-[var(--text-primary)] font-medium">{file.name}</p>
            <p className="text-[var(--text-secondary)] text-sm mt-1">
              {(file.size / 1024).toFixed(1)} KB
            </p>
            <p className="text-[var(--text-muted)] text-xs mt-3">
              Click to replace
            </p>
          </>
        ) : (
          <>
            <svg className="w-10 h-10 text-[var(--text-muted)] mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12l-3-3m0 0l-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
            <p className="text-[var(--text-primary)] font-medium">
              Drop your resume here
            </p>
            <p className="text-[var(--text-secondary)] text-sm mt-1">
              or click to browse
            </p>
            <p className="text-[var(--text-muted)] text-xs mt-3">
              PDF or TXT format
            </p>
          </>
        )}
      </div>

      {error && (
        <div className="alert alert-error">
          <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>{error}</span>
        </div>
      )}

      {resumeData && (
        <div className="alert alert-success">
          <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p className="font-medium">Resume processed successfully</p>
            <p className="text-sm opacity-80 mt-0.5">
              {resumeData.skills?.length || 0} skills extracted
            </p>
          </div>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="btn-primary w-full flex items-center justify-center gap-2"
      >
        {uploading ? (
          <>
            <div className="spinner"></div>
            <span>Processing...</span>
          </>
        ) : (
          <span>Upload and Continue</span>
        )}
      </button>

      {resumeData && resumeData.skills?.length > 0 && (
        <div className="pt-4 border-t border-[var(--border-color)]">
          <p className="section-header">Extracted Skills</p>
          <div className="flex flex-wrap gap-2">
            {resumeData.skills?.slice(0, 15).map((skill: string, idx: number) => (
              <span key={idx} className="skill-tag skill-tag-primary">
                {skill}
              </span>
            ))}
            {resumeData.skills?.length > 15 && (
              <span className="skill-tag skill-tag-muted">
                +{resumeData.skills.length - 15} more
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
