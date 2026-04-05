'use client'

import { useState, useEffect } from 'react'
import ChatPanel from '@/components/chat-panel'
import StatePanel from '@/components/state-panel'
import SessionPanel from '@/components/session-panel'
import StreamViewer from '@/components/stream-viewer'

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

export default function Dashboard() {
  const [sessionId, setSessionId] = useState('')
  const [apiStatus, setApiStatus] = useState<'online' | 'offline' | 'loading'>('loading')
  const [sceneData, setSceneData] = useState<SceneData>({
    current_scene: undefined,
    robots: {},
    objects: {},
  })

  useEffect(() => {
    setSessionId(`session_${Date.now()}`)
  }, [])

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/', { mode: 'cors' })
        setApiStatus(response.ok ? 'online' : 'offline')
      } catch {
        setApiStatus('offline')
      }
    }

    checkHealth()
    const interval = setInterval(checkHealth, 5000)
    return () => clearInterval(interval)
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
      
      if (data.scene_state) {
        setSceneData(data.scene_state)
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
    <div className="min-h-screen bg-slate-50">
      <div className="h-screen flex flex-col p-4 gap-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-baseline gap-3">
            <h1 className="text-2xl font-bold text-slate-900">Simulation</h1>
            <p className="text-sm text-slate-500">Gazebo Stream</p>
          </div>
          <div className="text-xs text-slate-400 font-mono" suppressHydrationWarning>{sessionId || 'loading...'}</div>
        </div>

        {/* Main Grid */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 min-h-0">
          {/* Gazebo Stream */}
          <div className="rounded-lg bg-white border border-slate-200 shadow-sm overflow-hidden">
            <StreamViewer streamUrl="http://localhost:8002/stream" />
          </div>

          {/* Chat Panel */}
          <ChatPanel apiStatus={apiStatus} onSendMessage={handleSendMessage} />
        </div>

        {/* Bottom Panels */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 h-64">
          <StatePanel sceneData={sceneData} />
          <SessionPanel sessionId={sessionId} apiStatus={apiStatus} onQuickCommand={handleSendMessage} />
        </div>
      </div>
    </div>
  )
}
