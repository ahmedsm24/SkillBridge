'use client'

import { useState } from 'react'

interface ProjectFormProps {
  resumeId: number
  gapAnalysisId: number
  onGenerated: (moduleId: number, trainingData: any) => void
  onBack: () => void
  onSkip: () => void
}

export default function ProjectForm({
  resumeId,
  gapAnalysisId,
  onGenerated,
  onBack,
  onSkip,
}: ProjectFormProps) {
  const [projectName, setProjectName] = useState('')
  const [projectDescription, setProjectDescription] = useState('')
  const [organization, setOrganization] = useState('')
  const [teamRole, setTeamRole] = useState('')
  const [techStack, setTechStack] = useState('')
  const [goals, setGoals] = useState('')
  const [timeline, setTimeline] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('resume_id', resumeId.toString())
      formData.append('gap_analysis_id', gapAnalysisId.toString())
      formData.append('project_name', projectName)
      formData.append('project_description', projectDescription)
      formData.append('team_role', teamRole)
      if (organization) formData.append('organization', organization)
      if (techStack) formData.append('tech_stack', techStack)
      if (goals) formData.append('goals', goals)
      if (timeline) formData.append('timeline', timeline)

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/projects/training`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to generate project training')
      }

      const data = await response.json()
      onGenerated(data.id, data)
    } catch (err: any) {
      setError(err.message || 'Failed to generate project training')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-[var(--text-primary)]">
          Project-Based Training
        </h2>
        <p className="text-[var(--text-secondary)] text-sm mt-1">
          Tailor training modules to a specific project. Training will first address skill gaps, then focus on project requirements.
        </p>
      </div>

      <div className="p-4 bg-[var(--bg-tertiary)] rounded-lg border border-[var(--border-color)]">
        <p className="text-sm text-[var(--text-secondary)]">
          <span className="font-medium text-[var(--text-primary)]">Two-Phase Training:</span> This will create a comprehensive program with Foundation modules (based on skill gaps) followed by Project-Specific modules (tailored to your project needs).
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">
              Project Name <span className="text-[var(--error)]">*</span>
            </label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              required
              placeholder="e.g., Customer Analytics Platform"
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">
              Team Role <span className="text-[var(--error)]">*</span>
            </label>
            <input
              type="text"
              value={teamRole}
              onChange={(e) => setTeamRole(e.target.value)}
              required
              placeholder="e.g., ML Intern, Backend Developer"
              className="input-field"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">
              Organization
            </label>
            <input
              type="text"
              value={organization}
              onChange={(e) => setOrganization(e.target.value)}
              placeholder="Company or team name"
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">
              Onboarding Timeline
            </label>
            <input
              type="text"
              value={timeline}
              onChange={(e) => setTimeline(e.target.value)}
              placeholder="e.g., 4 weeks, 2 months"
              className="input-field"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">
            Project Description <span className="text-[var(--error)]">*</span>
          </label>
          <textarea
            value={projectDescription}
            onChange={(e) => setProjectDescription(e.target.value)}
            required
            rows={4}
            placeholder="Describe the project, its purpose, and what the team member will be working on..."
            className="input-field resize-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">
            Tech Stack
          </label>
          <input
            type="text"
            value={techStack}
            onChange={(e) => setTechStack(e.target.value)}
            placeholder="e.g., Python, TensorFlow, PostgreSQL, Docker (comma-separated)"
            className="input-field"
          />
          <p className="text-xs text-[var(--text-muted)] mt-1">Separate technologies with commas</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">
            Project Goals
          </label>
          <input
            type="text"
            value={goals}
            onChange={(e) => setGoals(e.target.value)}
            placeholder="e.g., Build ML pipeline, Improve prediction accuracy (comma-separated)"
            className="input-field"
          />
          <p className="text-xs text-[var(--text-muted)] mt-1">Separate goals with commas</p>
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
            type="button"
            onClick={onSkip}
            className="btn-secondary"
          >
            Skip (General Training)
          </button>
          <button
            type="submit"
            disabled={submitting || !projectName || !projectDescription || !teamRole}
            className="btn-primary flex-1 flex items-center justify-center gap-2"
          >
            {submitting ? (
              <>
                <div className="spinner"></div>
                <span>Generating...</span>
              </>
            ) : (
              <span>Generate Project Training</span>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}

