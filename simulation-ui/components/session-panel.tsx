'use client'

interface SessionPanelProps {
  sessionId: string
  apiStatus: 'online' | 'offline' | 'loading'
  onQuickCommand?: (command: string) => Promise<any>
}

export default function SessionPanel({ sessionId, apiStatus, onQuickCommand }: SessionPanelProps) {
  const quickCommands = [
    { label: 'Warehouse + Robot', prompt: 'Create a warehouse with a robot' },
    { label: 'Add Shelves', prompt: 'Add three shelves' },
    { label: 'Circle Formation', prompt: 'Create 5 robots moving in a circle' },
  ]

  return (
    <div className="flex flex-col rounded-lg bg-white border border-slate-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-200 bg-slate-50">
        <h2 className="font-semibold text-slate-900">Session</h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-4 min-h-0">
        {/* Session ID */}
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase">Session ID</p>
          <p className="text-xs text-slate-700 font-mono mt-1 bg-slate-100 px-2 py-1 rounded break-all">
            {sessionId}
          </p>
        </div>

        {/* Status */}
        <div className="border-t border-slate-200 pt-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-600">API Status</span>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
              apiStatus === 'online' ? 'bg-green-100 text-green-700' :
              apiStatus === 'loading' ? 'bg-yellow-100 text-yellow-700' :
              'bg-red-100 text-red-700'
            }`}>
              {apiStatus === 'online' ? 'Online' : apiStatus === 'loading' ? 'Loading' : 'Offline'}
            </span>
          </div>
        </div>

        {/* Quick Commands */}
        <div className="border-t border-slate-200 pt-3 space-y-2">
          <p className="text-xs font-semibold text-slate-500 uppercase">Quick Commands</p>
          <div className="space-y-1">
            {quickCommands.map((cmd) => (
              <button
                key={cmd.label}
                onClick={() => onQuickCommand?.(cmd.prompt)}
                disabled={apiStatus === 'offline'}
                className="w-full px-2 py-1.5 rounded text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-left"
              >
                {cmd.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
