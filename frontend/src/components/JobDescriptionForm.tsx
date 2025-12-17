'use client'

import { useState } from 'react'

interface JobDescriptionFormProps {
  onCreated: (jobDescriptionId: number) => void
  onBack: () => void
}

export default function JobDescriptionForm({ onCreated, onBack }: JobDescriptionFormProps) {
  const [title, setTitle] = useState('')
  const [company, setCompany] = useState('')
  const [description, setDescription] = useState('')
  const [domain, setDomain] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/job-descriptions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title,
          company: company || undefined,
          description,
          domain: domain || undefined,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create job description')
      }

      const data = await response.json()
      onCreated(data.id)
    } catch (err: any) {
      setError(err.message || 'Failed to create job description')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-[var(--text-primary)]">
          Job Description
        </h2>
        <p className="text-[var(--text-secondary)] text-sm mt-1">
          Enter the job details to identify required skills
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">
              Job Title <span className="text-[var(--error)]">*</span>
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              placeholder="Machine Learning Engineer"
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">
              Company
            </label>
            <input
              type="text"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="Company name"
              className="input-field"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">
            Industry / Domain
          </label>
          <input
            type="text"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            placeholder="e.g., Healthcare, Finance, Technology"
            className="input-field"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">
            Job Description <span className="text-[var(--error)]">*</span>
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            rows={8}
            placeholder="Paste the complete job description including responsibilities, requirements, and qualifications..."
            className="input-field resize-none"
          />
        </div>

        {error && (
          <div className="alert alert-error">
            <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        <div className="flex gap-3 pt-2">
          <button
            type="button"
            onClick={onBack}
            className="btn-secondary"
          >
            Back
          </button>
          <button
            type="submit"
            disabled={submitting || !title || !description}
            className="btn-primary flex-1 flex items-center justify-center gap-2"
          >
            {submitting ? (
              <>
                <div className="spinner"></div>
                <span>Analyzing...</span>
              </>
            ) : (
              <span>Continue</span>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
