'use client'

import { useState, useEffect, useCallback } from 'react'

interface StreamViewerProps {
  streamUrl?: string
  healthUrl?: string
  fallbackMessage?: string
}

export default function StreamViewer({ 
  streamUrl = 'http://localhost:8002/stream',
  healthUrl = 'http://localhost:8002/health',
  fallbackMessage = 'Waiting for Gazebo stream...'
}: StreamViewerProps) {
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [streamKey, setStreamKey] = useState(0)

  // Check health endpoint to determine connection status
  const checkHealth = useCallback(async () => {
    try {
      const response = await fetch(healthUrl, { mode: 'cors' })
      if (response.ok) {
        setConnected(true)
        setError(null)
      } else {
        setConnected(false)
        setError('Server not healthy')
      }
    } catch {
      setConnected(false)
      setError('Cannot connect to stream server')
    }
  }, [healthUrl])

  useEffect(() => {
    // Initial check
    checkHealth()
    
    // Poll health every 3 seconds
    const interval = setInterval(checkHealth, 3000)
    
    return () => clearInterval(interval)
  }, [checkHealth])

  // Retry stream on error
  const handleImageError = () => {
    setTimeout(() => {
      setStreamKey(k => k + 1)
    }, 2000)
  }

  return (
    <div className="w-full h-full bg-slate-900 rounded-lg overflow-hidden relative">
      {/* MJPEG Stream - always render when connected */}
      {connected && (
        <img
          key={streamKey}
          src={`${streamUrl}?t=${streamKey}`}
          alt="Gazebo Simulation"
          className="w-full h-full object-contain"
          onError={handleImageError}
        />
      )}
      
      {/* Fallback / Loading state */}
      {!connected && (
        <div className="absolute inset-0 flex flex-col items-center justify-center text-white">
          <div className="w-8 h-8 border-2 border-white/30 border-t-white rounded-full animate-spin mb-3" />
          <p className="text-sm text-white/70">{error || fallbackMessage}</p>
          <p className="text-xs text-white/50 mt-1">Stream: {streamUrl}</p>
        </div>
      )}
      
      {/* Status indicator */}
      <div className="absolute top-3 right-3 flex items-center gap-2 bg-black/50 px-2 py-1 rounded text-xs text-white">
        <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
        {connected ? 'Live' : 'Disconnected'}
      </div>
    </div>
  )
}
