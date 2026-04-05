import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: '3D Simulation Platform',
  description: 'Real-time 3D environment visualization and control',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
