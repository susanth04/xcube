'use client'

import { useState, useEffect, useRef } from 'react'
import ChatPanel from '@/components/chat-panel'
import StatePanel from '@/components/state-panel'
import SessionPanel from '@/components/session-panel'
import Scene3D from '@/components/scene-3d'

interface Robot {
  position: [number, number, number]
}

interface SceneObject {
  position: [number, number, number]
}

interface SceneData {
  current_scene?: string
  robots?: Record<string, Robot>
  objects?: Record<string, SceneObject>
}

interface SimulationState {
  fps: number
  sceneData: SceneData
}

export default function Dashboard() {
  const [sessionId] = useState(() => `session_${Date.now()}`)
  const [apiStatus, setApiStatus] = useState<'online' | 'offline' | 'loading'>('loading')
  const [simulationState, setSimulationState] = useState<SimulationState>({
    fps: 60,
    sceneData: {
      current_scene: undefined,
      robots: {},
      objects: {},
    },
  })
  const canvasRef = useRef<HTMLDivElement>(null)
  const frameCountRef = useRef(0)
  const lastFrameTimeRef = useRef(Date.now())

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/', {
          mode: 'cors',
        })
        if (response.ok) {
          setApiStatus('online')
        } else {
          setApiStatus('offline')
        }
      } catch {
        setApiStatus('offline')
      }
    }

    checkHealth()
    const interval = setInterval(checkHealth, 5000)
    return () => clearInterval(interval)
  }, [])

  // FPS counter
  useEffect(() => {
    const fpsInterval = setInterval(() => {
      const now = Date.now()
      const elapsed = now - lastFrameTimeRef.current
      if (elapsed >= 1000) {
        setSimulationState(prev => ({
          ...prev,
          fps: frameCountRef.current,
        }))
        frameCountRef.current = 0
        lastFrameTimeRef.current = now
      }
    }, 100)
    return () => clearInterval(fpsInterval)
  }, [])

  const handleSendMessage = async (message: string) => {
    try {
      setApiStatus('loading')
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: message, session_id: sessionId }),
        mode: 'cors',
      })

      if (!response.ok) throw new Error('API error')

      const data = await response.json()
      
      // Update scene data from API response
      if (data.scene_state) {
        setSimulationState(prev => ({
          ...prev,
          sceneData: data.scene_state,
        }))
      }
      
      setApiStatus('online')
      return data
    } catch (error) {
      console.error('Chat error:', error)
      setApiStatus('offline')
      return null
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-background/95">
      <div className="h-screen flex flex-col p-4 lg:p-6 gap-4 lg:gap-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-baseline gap-3">
            <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-foreground">
              Simulation
            </h1>
            <p className="text-sm text-muted-foreground font-medium tracking-wide">
              Real-time 3D Environment
            </p>
          </div>
          <div className="text-xs text-muted-foreground font-mono">
            {sessionId}
          </div>
        </div>

        {/* Main Grid */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 min-h-0">
          {/* 3D Canvas - Top Left */}
          <div className="rounded-lg bg-white border border-border shadow-sm overflow-hidden dark:bg-slate-950">
            <div ref={canvasRef} className="h-full w-full relative bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
              <Scene3D sceneState={simulationState.sceneData} />
              <div className="absolute top-3 right-3 bg-black/60 backdrop-blur-sm px-2.5 py-1.5 rounded text-white font-mono text-xs">
                {simulationState.fps} FPS
              </div>
            </div>
          </div>

          {/* Chat Panel - Top Right */}
          <ChatPanel 
            apiStatus={apiStatus} 
            onSendMessage={handleSendMessage}
          />
        </div>

        {/* Bottom Panels */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 h-1/3">
          {/* State Panel - Bottom Left */}
          <StatePanel sceneData={simulationState.sceneData} fps={simulationState.fps} />

          {/* Session Panel - Bottom Right */}
          <SessionPanel 
            sessionId={sessionId} 
            apiStatus={apiStatus}
            onQuickCommand={handleSendMessage}
          />
        </div>
      </div>
    </div>
  )
}
