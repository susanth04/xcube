'use client'

interface SessionPanelProps {
  sessionId: string
  apiStatus: 'online' | 'offline' | 'loading'
  onQuickCommand?: (command: string) => Promise<any>
}

export default function SessionPanel({
  sessionId,
  apiStatus,
  onQuickCommand,
}: SessionPanelProps) {
  const quickCommands = [
    { label: 'Warehouse + Robot', prompt: 'Create a warehouse with a robot' },
    { label: 'Add Shelves', prompt: 'Add three shelves' },
    { label: 'Circle Formation', prompt: 'Create 5 robots moving in a circle' },
  ]

  return (
    <div className="flex flex-col rounded-lg bg-white dark:bg-slate-950 border border-border shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-border bg-gradient-to-r from-slate-50 dark:from-slate-900 to-slate-50 dark:to-slate-900">
        <h2 className="font-semibold text-foreground text-lg">Session & Commands</h2>
        <p className="text-xs text-muted-foreground mt-1">Quick actions</p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6 min-h-0">
        {/* Session ID */}
        <div>
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Session ID</p>
          <p className="text-xs text-foreground font-mono mt-3 bg-muted dark:bg-slate-900 px-3 py-2 rounded break-all">
            {sessionId}
          </p>
        </div>

        {/* Status Indicators */}
        <div className="border-t border-border pt-6 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-foreground font-medium">API Status</span>
            <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
              apiStatus === 'online' ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-100' :
              apiStatus === 'loading' ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-100' :
              'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-100'
            }`}>
              {apiStatus === 'online' ? 'Online' : apiStatus === 'loading' ? 'Loading' : 'Offline'}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-foreground font-medium">Renderer</span>
            <span className="text-xs px-2.5 py-1 rounded-full font-medium bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-100">
              React Three Fiber
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-foreground font-medium">Version</span>
            <span className="text-xs text-muted-foreground font-mono">2.0.0</span>
          </div>
        </div>

        {/* Quick Commands */}
        <div className="border-t border-border pt-6 space-y-3">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Quick Commands</p>
          <div className="space-y-2">
            {quickCommands.map((cmd) => (
              <button
                key={cmd.label}
                onClick={() => onQuickCommand?.(cmd.prompt)}
                disabled={apiStatus === 'offline'}
                className="w-full px-3 py-2 rounded-md text-xs font-medium text-foreground bg-muted hover:bg-muted/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
