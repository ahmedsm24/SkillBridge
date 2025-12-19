'use client'

import { useState, useEffect } from 'react'

interface TrainingModulesProps {
  gapAnalysisId: number
  onGenerated: (moduleId: number) => void
  onBack: () => void
}

export default function TrainingModules({
  gapAnalysisId,
  onGenerated,
  onBack,
}: TrainingModulesProps) {
  const [generating, setGenerating] = useState(false)
  const [trainingModule, setTrainingModule] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [expandedModule, setExpandedModule] = useState<number | null>(null)

  const generateModules = async () => {
    setGenerating(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('gap_analysis_id', gapAnalysisId.toString())

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/training-modules/generate`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Generation failed')
      }

      const data = await response.json()
      setTrainingModule(data)
      onGenerated(data.id)
    } catch (err: any) {
      setError(err.message || 'Failed to generate training modules')
    } finally {
      setGenerating(false)
    }
  }

  useEffect(() => {
    generateModules()
  }, [])

  if (generating) {
    return (
      <div className="py-16 text-center">
        <div className="spinner-dark w-8 h-8 mx-auto mb-4"></div>
        <p className="text-[var(--text-secondary)]">Generating training modules...</p>
        <p className="text-[var(--text-muted)] text-sm mt-1">This may take a moment</p>
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
          <button type="button" onClick={onBack} className="btn-secondary">
            Back
          </button>
          <button type="button" onClick={generateModules} className="btn-primary">
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (!trainingModule) return null

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-[var(--text-primary)]">
          Training Program
        </h2>
        <p className="text-[var(--text-secondary)] text-sm mt-1">
          Personalized modules based on your skill gaps
        </p>
      </div>

      {/* Overview */}
      <div className="p-4 bg-[var(--bg-tertiary)] rounded-lg">
        <h3 className="font-medium text-[var(--text-primary)]">{trainingModule.title}</h3>
        {trainingModule.description && (
          <p className="text-sm text-[var(--text-secondary)] mt-1">{trainingModule.description}</p>
        )}
        {trainingModule.estimated_duration && (
          <p className="text-xs text-[var(--text-muted)] mt-2">
            Estimated duration: {trainingModule.estimated_duration}
          </p>
        )}
      </div>

      {/* Learning Objectives */}
      {trainingModule.learning_objectives && trainingModule.learning_objectives.length > 0 && (
        <div>
          <p className="section-header">Learning Objectives</p>
          <ul className="space-y-2">
            {trainingModule.learning_objectives.map((obj: string, idx: number) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                <svg className="w-4 h-4 text-[var(--success)] mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{obj}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Modules */}
      {trainingModule.modules && trainingModule.modules.length > 0 && (
        <div>
          <p className="section-header">Modules</p>
          <div className="space-y-2">
            {trainingModule.modules.map((module: any, idx: number) => (
              <div key={idx} className="accordion-item">
                <div
                  className="accordion-header flex items-center justify-between"
                  onClick={() => setExpandedModule(expandedModule === idx ? null : idx)}
                >
                  <div className="flex-1">
                    <h4 className="font-medium text-[var(--text-primary)]">{module.title}</h4>
                    <p className="text-sm text-[var(--text-secondary)] mt-0.5">{module.description}</p>
                    <div className="flex gap-2 mt-2">
                      {module.estimated_duration && (
                        <span className="text-xs px-2 py-1 bg-[var(--bg-tertiary)] text-[var(--text-muted)] rounded">
                          {module.estimated_duration}
                        </span>
                      )}
                      {module.difficulty && (
                        <span className="text-xs px-2 py-1 bg-[var(--bg-tertiary)] text-[var(--text-muted)] rounded capitalize">
                          {module.difficulty}
                        </span>
                      )}
                    </div>
                  </div>
                  <svg 
                    className={`w-5 h-5 text-[var(--text-muted)] transition-transform ${expandedModule === idx ? 'rotate-180' : ''}`} 
                    fill="none" 
                    viewBox="0 0 24 24" 
                    stroke="currentColor" 
                    strokeWidth={2}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>

                {expandedModule === idx && (
                  <div className="accordion-content space-y-4">
                    {module.learning_objectives && module.learning_objectives.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wide mb-2">Objectives</p>
                        <ul className="space-y-1">
                          {module.learning_objectives.map((obj: string, oidx: number) => (
                            <li key={oidx} className="text-sm text-[var(--text-secondary)] flex items-start gap-2">
                              <span className="text-[var(--text-muted)]">•</span>
                              <span>{obj}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {module.content && module.content.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wide mb-2">Content</p>
                        <div className="space-y-3">
                          {module.content.map((section: any, sidx: number) => (
                            <div key={sidx}>
                              <p className="text-sm font-medium text-[var(--text-primary)]">{section.section}</p>
                              <p className="text-sm text-[var(--text-secondary)] mt-0.5">{section.content}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {module.practical_exercises && module.practical_exercises.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wide mb-2">Exercises</p>
                        <div className="space-y-2">
                          {module.practical_exercises.map((exercise: any, eidx: number) => (
                            <div key={eidx} className="p-3 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded">
                              <p className="text-sm font-medium text-[var(--text-primary)]">{exercise.title}</p>
                              <p className="text-sm text-[var(--text-secondary)] mt-0.5">{exercise.description}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Case Studies */}
      {trainingModule.case_studies && trainingModule.case_studies.length > 0 && (
        <div>
          <p className="section-header">Case Studies</p>
          <div className="space-y-3">
            {trainingModule.case_studies.map((caseStudy: any, idx: number) => (
              <div key={idx} className="p-4 border border-[var(--border-color)] rounded-lg">
                <h4 className="font-medium text-[var(--text-primary)]">{caseStudy.title}</h4>
                <p className="text-sm text-[var(--text-secondary)] mt-1">{caseStudy.description}</p>
                {caseStudy.learning_outcomes && caseStudy.learning_outcomes.length > 0 && (
                  <div className="mt-3">
                    <p className="text-xs text-[var(--text-muted)] mb-1">Learning Outcomes:</p>
                    <ul className="space-y-1">
                      {caseStudy.learning_outcomes.map((outcome: string, oidx: number) => (
                        <li key={oidx} className="text-sm text-[var(--text-secondary)] flex items-start gap-2">
                          <span className="text-[var(--text-muted)]">•</span>
                          <span>{outcome}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Resources */}
      {trainingModule.resources && trainingModule.resources.length > 0 && (
        <div>
          <p className="section-header">Resources</p>
          <div className="space-y-2">
            {trainingModule.resources.map((resource: any, idx: number) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-[var(--bg-tertiary)] rounded-lg">
                <div className="flex items-center gap-3">
                  <span className="text-xs px-2 py-1 bg-[var(--bg-secondary)] border border-[var(--border-color)] text-[var(--text-muted)] rounded uppercase">
                    {resource.type}
                  </span>
                  <span className="text-sm text-[var(--text-primary)]">{resource.title}</span>
                </div>
                {resource.url && (
                  <a
                    href={resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-[var(--accent-highlight)] hover:underline"
                  >
                    View
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-3 pt-4 border-t border-[var(--border-color)]">
        <button type="button" onClick={onBack} className="btn-secondary">
          Back
        </button>
        <button type="button" onClick={generateModules} className="btn-primary flex-1">
          Regenerate Modules
        </button>
      </div>
    </div>
  )
}
