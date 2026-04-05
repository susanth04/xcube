'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'

interface Message {
  id: string
  type: 'user' | 'bot'
  text: string
}

interface ChatPanelProps {
  apiStatus: 'online' | 'offline' | 'loading'
  onSendMessage: (message: string) => Promise<any>
}

export default function ChatPanel({ apiStatus, onSendMessage }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    { id: '0', type: 'bot', text: '3D Simulation Ready!' },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = { id: Date.now().toString(), type: 'user', text: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await onSendMessage(input)
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        text: response?.actions?.length 
          ? `✓ Generated ${response.actions.length} action(s)`
          : 'Simulation updated',
      }
      setMessages(prev => [...prev, botMessage])
    } catch {
      setMessages(prev => [...prev, { id: (Date.now() + 2).toString(), type: 'bot', text: '❌ Failed to process command' }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col rounded-lg bg-white border border-slate-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-200 bg-slate-50">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-slate-900">Commands</h2>
          <div className="flex items-center gap-2">
            <div className={`h-2 w-2 rounded-full ${
              apiStatus === 'online' ? 'bg-green-500' :
              apiStatus === 'loading' ? 'bg-yellow-500' : 'bg-red-500'
            }`} />
            <span className="text-xs text-slate-500">
              {apiStatus === 'online' ? 'Online' : apiStatus === 'loading' ? 'Loading' : 'Offline'}
            </span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 min-h-0">
        {messages.map(msg => (
          <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
              msg.type === 'user' ? 'bg-purple-600 text-white' : 'bg-slate-100 text-slate-700'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2 px-3 py-2 bg-slate-100 rounded-lg">
              <Spinner className="w-3 h-3" />
              <span className="text-xs text-slate-500">Processing...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-4 py-3 border-t border-slate-200 bg-slate-50">
        <form onSubmit={handleSend} className="flex gap-2">
          <Input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Enter command..."
            className="flex-1 text-sm"
            disabled={isLoading || apiStatus === 'offline'}
          />
          <Button 
            type="submit" 
            size="sm"
            disabled={isLoading || !input.trim() || apiStatus === 'offline'}
          >
            {isLoading ? <Spinner className="w-3 h-3" /> : 'Send'}
          </Button>
        </form>
      </div>
    </div>
  )
}
