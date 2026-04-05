'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'

interface Message {
  id: string
  type: 'user' | 'bot'
  text: string
  timestamp: Date
}

interface ChatPanelProps {
  apiStatus: 'online' | 'offline' | 'loading'
  onSendMessage: (message: string) => Promise<any>
}

export default function ChatPanel({ apiStatus, onSendMessage }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      type: 'bot',
      text: '3D Simulation Ready!',
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      text: input,
      timestamp: new Date(),
    }

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
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        type: 'bot',
        text: '❌ Failed to process command',
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col rounded-lg bg-white border border-border shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-border bg-gradient-to-r from-slate-50 to-slate-50">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-semibold text-foreground text-lg">Commands</h2>
            <p className="text-xs text-muted-foreground mt-1">Real-time environment control</p>
          </div>
          <div className="flex items-center gap-2">
            <div className={`h-2 w-2 rounded-full ${
              apiStatus === 'online' ? 'bg-green-500' :
              apiStatus === 'loading' ? 'bg-yellow-500' :
              'bg-red-500'
            }`} />
            <span className="text-xs font-medium text-muted-foreground">
              {apiStatus === 'online' ? 'Online' : apiStatus === 'loading' ? 'Loading' : 'Offline'}
            </span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4 min-h-0">
        {messages.map(msg => (
          <div 
            key={msg.id} 
            className={`flex gap-3 ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-xs px-4 py-3 rounded-lg ${
              msg.type === 'user'
                ? 'bg-primary text-white text-sm'
                : 'bg-muted text-foreground text-sm'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="flex items-center gap-2 px-4 py-3 bg-muted rounded-lg">
              <Spinner className="w-3 h-3" />
              <span className="text-xs text-muted-foreground">Processing...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-6 py-4 border-t border-border bg-gradient-to-r from-slate-50 to-slate-50">
        <form onSubmit={handleSend} className="flex gap-2">
          <Input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Enter command..."
            className="flex-1 text-sm h-10"
            disabled={isLoading || apiStatus === 'offline'}
          />
          <Button 
            type="submit" 
            size="sm"
            disabled={isLoading || !input.trim() || apiStatus === 'offline'}
            className="px-4 h-10 font-medium"
          >
            {isLoading ? <Spinner className="w-3.5 h-3.5" /> : 'Send'}
          </Button>
        </form>
        <p className="text-xs text-muted-foreground mt-2">Press Enter or click Send</p>
      </div>
    </div>
  )
}
