'use client'

import { useState, useEffect } from 'react'

interface GapAnalysisResultsProps {
  resumeId: number
  jobDescriptionId: number
  onAnalysisComplete: (gapAnalysisId: number) => void
  onBack: () => void
}

export default function GapAnalysisResults({
  resumeId,
  jobDescriptionId,
  onAnalysisComplete,
  onBack,
}: GapAnalysisResultsProps) {
  const [analyzing, setAnalyzing] = useState(false)
  const [gapAnalysis, setGapAnalysis] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const performAnalysis = async () => {
    setAnalyzing(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('resume_id', resumeId.toString())
      formData.append('job_description_id', jobDescriptionId.toString())

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/gap-analysis`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Analysis failed')
      }

      const data = await response.json()
      setGapAnalysis(data)
      onAnalysisComplete(data.id)
    } catch (err: any) {
      setError(err.message || 'Failed to perform gap analysis')
    } finally {
      setAnalyzing(false)
    }
  }

  useEffect(() => {
    performAnalysis()
  }, [])

  if (analyzing) {
    return (
      <div className="py-16 text-center">
        <div className="spinner-dark w-8 h-8 mx-auto mb-4"></div>
        <p className="text-[var(--text-secondary)]">Analyzing skill gaps...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-4">
        <div className="alert alert-error">
          <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>{error}</span>
        </div>
        <div className="flex gap-3">
          <button onClick={onBack} className="btn-secondary">
            Back
          </button>
          <button onClick={performAnalysis} className="btn-primary">
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (!gapAnalysis) return null

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-[var(--text-primary)]">
          Gap Analysis Results
        </h2>
        <p className="text-[var(--text-secondary)] text-sm mt-1">
          Comparison of your skills against job requirements
        </p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 bg-[var(--bg-tertiary)] rounded-lg text-center">
          <p className="text-2xl font-semibold text-[var(--text-primary)]">
            {gapAnalysis.confidence_score || 0}%
          </p>
          <p className="text-xs text-[var(--text-muted)] mt-1">Match Score</p>
        </div>
        <div className="p-4 bg-[var(--success-light)] rounded-lg text-center">
          <p className="text-2xl font-semibold text-[var(--success)]">
            {gapAnalysis.existing_skills?.length || 0}
          </p>
          <p className="text-xs text-[var(--success)] mt-1">Matched Skills</p>
        </div>
        <div className="p-4 bg-[var(--error-light)] rounded-lg text-center">
          <p className="text-2xl font-semibold text-[var(--error)]">
            {gapAnalysis.missing_skills?.length || 0}
          </p>
          <p className="text-xs text-[var(--error)] mt-1">Skill Gaps</p>
        </div>
      </div>

      {/* Matched Skills */}
      <div>
        <p className="section-header">Matched Skills</p>
        <div className="flex flex-wrap gap-2">
          {gapAnalysis.existing_skills?.map((skill: string, idx: number) => (
            <span key={idx} className="skill-tag skill-tag-success">
              {skill}
            </span>
          ))}
          {(!gapAnalysis.existing_skills || gapAnalysis.existing_skills.length === 0) && (
            <p className="text-[var(--text-muted)] text-sm">No matching skills found</p>
          )}
        </div>
      </div>

      {/* Missing Skills */}
      <div>
        <p className="section-header">Skill Gaps</p>
        <div className="flex flex-wrap gap-2">
          {gapAnalysis.missing_skills?.slice(0, 15).map((skill: string, idx: number) => (
            <span key={idx} className="skill-tag skill-tag-error">
              {skill}
            </span>
          ))}
          {(!gapAnalysis.missing_skills || gapAnalysis.missing_skills.length === 0) && (
            <p className="text-[var(--text-muted)] text-sm">No skill gaps identified</p>
          )}
        </div>
      </div>

      {/* Priority Gaps */}
      {gapAnalysis.gap_priority && gapAnalysis.gap_priority.length > 0 && (
        <div>
          <p className="section-header">Priority Analysis</p>
          <div className="space-y-3">
            {gapAnalysis.gap_priority.map((gap: any, idx: number) => (
              <div key={idx} className="p-4 border border-[var(--border-color)] rounded-lg">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium text-[var(--text-primary)]">{gap.skill}</h4>
                      <span className={
                        gap.importance === 'critical' ? 'priority-critical' :
                        gap.importance === 'important' ? 'priority-important' :
                        'priority-normal'
                      }>
                        {gap.importance}
                      </span>
                    </div>
                    <p className="text-sm text-[var(--text-secondary)]">{gap.reason}</p>
                    {gap.related_skills && gap.related_skills.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {gap.related_skills.map((skill: string, sidx: number) => (
                          <span key={sidx} className="text-xs px-2 py-0.5 bg-[var(--bg-tertiary)] text-[var(--text-muted)] rounded">
                            {skill}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <span className="text-sm text-[var(--text-muted)]">#{gap.priority}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-3 pt-4 border-t border-[var(--border-color)]">
        <button onClick={onBack} className="btn-secondary">
          Back
        </button>
        <button
          onClick={() => onAnalysisComplete(gapAnalysis.id)}
          className="btn-primary flex-1"
        >
          Generate Training Modules
        </button>
      </div>
    </div>
  )
}
