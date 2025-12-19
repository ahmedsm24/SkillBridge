'use client'

import { useState } from 'react'
import ResumeUpload from '@/components/ResumeUpload'
import JobDescriptionForm from '@/components/JobDescriptionForm'
import GapAnalysisResults from '@/components/GapAnalysisResults'
import ProjectForm from '@/components/ProjectForm'
import TrainingModules from '@/components/TrainingModules'

const steps = [
  { id: 'upload', label: 'Resume', number: 1 },
  { id: 'job', label: 'Job Description', number: 2 },
  { id: 'analysis', label: 'Analysis', number: 3 },
  { id: 'project', label: 'Project', number: 4 },
  { id: 'training', label: 'Training', number: 5 },
]

export default function Home() {
  const [resumeId, setResumeId] = useState<number | null>(null)
  const [jobDescriptionId, setJobDescriptionId] = useState<number | null>(null)
  const [gapAnalysisId, setGapAnalysisId] = useState<number | null>(null)
  const [trainingModuleId, setTrainingModuleId] = useState<number | null>(null)
  const [projectTrainingData, setProjectTrainingData] = useState<any>(null)
  const [currentStep, setCurrentStep] = useState<'upload' | 'job' | 'analysis' | 'project' | 'training'>('upload')

  const handleResumeUploaded = (id: number) => {
    setResumeId(id)
    setCurrentStep('job')
  }

  const handleJobDescriptionCreated = (id: number) => {
    setJobDescriptionId(id)
    setCurrentStep('analysis')
  }

  const handleGapAnalysisComplete = (id: number) => {
    setGapAnalysisId(id)
    setCurrentStep('project')
  }

  const handleProjectTrainingGenerated = (id: number, data: any) => {
    setTrainingModuleId(id)
    setProjectTrainingData(data)
    setCurrentStep('training')
  }

  const handleSkipProject = () => {
    // Skip to general training
    setCurrentStep('training')
  }

  const handleTrainingGenerated = (id: number) => {
    setTrainingModuleId(id)
  }

  const getStepIndex = (step: string) => steps.findIndex(s => s.id === step)
  const currentStepIndex = getStepIndex(currentStep)

  return (
    <main className="min-h-screen py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <header className="mb-16 text-center animate-fade-in">
          <h1 className="text-4xl font-light text-[var(--text-primary)] tracking-tight mb-3">
            SkillBridge
          </h1>
          <p className="text-[var(--text-muted)] text-lg font-light">
            Identify skill gaps. Generate personalized learning paths.
          </p>
        </header>

        {/* Step Indicator */}
        <nav className="mb-12 animate-fade-in-delay-1">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center flex-1">
                <div className="flex flex-col items-center">
                  <div
                    className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-medium transition-all ${
                      index < currentStepIndex
                        ? 'bg-[var(--accent-secondary)] text-white'
                        : index === currentStepIndex
                        ? 'bg-[var(--accent-primary)] text-white'
                        : 'bg-[var(--bg-accent)] text-[var(--text-muted)] border border-[var(--border-color)]'
                    }`}
                  >
                    {index < currentStepIndex ? (
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      step.number
                    )}
                  </div>
                  <span className={`mt-2 text-xs font-medium tracking-wide uppercase hidden sm:block ${
                    index <= currentStepIndex ? 'text-[var(--text-secondary)]' : 'text-[var(--text-muted)]'
                  }`}>
                    {step.label}
                  </span>
                </div>
                {index < steps.length - 1 && (
                  <div className={`flex-1 h-px mx-3 mt-[-20px] sm:mt-[-24px] transition-all ${
                    index < currentStepIndex ? 'bg-[var(--accent-secondary)]' : 'bg-[var(--border-color)]'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </nav>

        {/* Content Card */}
        <div className="card p-8 sm:p-10 animate-fade-in-delay-2">
          {currentStep === 'upload' && (
            <ResumeUpload onUploaded={handleResumeUploaded} />
          )}

          {currentStep === 'job' && resumeId && (
            <JobDescriptionForm
              onCreated={handleJobDescriptionCreated}
              onBack={() => setCurrentStep('upload')}
            />
          )}

          {currentStep === 'analysis' && resumeId && jobDescriptionId && (
            <GapAnalysisResults
              resumeId={resumeId}
              jobDescriptionId={jobDescriptionId}
              onAnalysisComplete={handleGapAnalysisComplete}
              onBack={() => setCurrentStep('job')}
            />
          )}

          {currentStep === 'project' && resumeId && gapAnalysisId && (
            <ProjectForm
              resumeId={resumeId}
              gapAnalysisId={gapAnalysisId}
              onGenerated={handleProjectTrainingGenerated}
              onBack={() => setCurrentStep('analysis')}
              onSkip={handleSkipProject}
            />
          )}

          {currentStep === 'training' && gapAnalysisId && (
            <TrainingModules
              gapAnalysisId={gapAnalysisId}
              onGenerated={handleTrainingGenerated}
              onBack={() => setCurrentStep('project')}
              projectData={projectTrainingData}
            />
          )}
        </div>

        {/* Footer */}
        <footer className="mt-16 text-center animate-fade-in-delay-2">
          <div className="inline-flex items-center gap-3 text-sm text-[var(--text-muted)]">
            <a 
              href="https://s2.smu.edu/~eclarson/index.html" 
              target="_blank" 
              rel="noopener noreferrer"
              className="font-medium text-[var(--text-secondary)] hover:text-[var(--accent-secondary)] transition-colors"
            >
              Dr. Eric Larson
            </a>
            <span className="text-[var(--border-color)]">·</span>
            <span className="font-medium text-[var(--text-secondary)]">Ahmed Abdul Naoman</span>
          </div>
          <p className="mt-2 text-xs text-[var(--text-muted)]">
            <a 
              href="https://www.smu.edu/lyle" 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-[var(--accent-secondary)] transition-colors"
            >
              SMU Lyle School of Engineering
            </a>
          </p>
        </footer>
      </div>
    </main>
  )
}
