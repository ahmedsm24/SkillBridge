import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Resume-to-Training Module Generator',
  description: 'AI-powered system that analyzes resumes and generates personalized training modules',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
