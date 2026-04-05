'use client'

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

interface StatePanelProps {
  sceneData: SceneData
  fps: number
}

export default function StatePanel({ sceneData, fps }: StatePanelProps) {
  const robotCount = Object.keys(sceneData.robots || {}).length
  const objectCount = Object.keys(sceneData.objects || {}).length
  const totalCount = robotCount + objectCount

  return (
    <div className="flex flex-col rounded-lg bg-white dark:bg-slate-950 border border-border shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-border bg-gradient-to-r from-slate-50 dark:from-slate-900 to-slate-50 dark:to-slate-900">
        <h2 className="font-semibold text-foreground text-lg">Scene State</h2>
        <p className="text-xs text-muted-foreground mt-1">Real-time simulation state</p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-5 min-h-0">
        {/* Current Scene */}
        <div>
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Scene Name</p>
          <p className="text-sm font-mono text-foreground mt-2">{sceneData.current_scene || '—'}</p>
        </div>

        {/* Robots */}
        <div>
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Robots ({robotCount})</p>
          <div className="mt-3 space-y-2 max-h-40 overflow-y-auto">
            {robotCount === 0 ? (
              <p className="text-xs text-muted-foreground">No robots</p>
            ) : (
              Object.entries(sceneData.robots || {}).map(([id, data]) => (
                <div key={id} className="bg-muted/50 rounded p-2">
                  <p className="text-xs font-semibold text-foreground">{id}</p>
                  <p className="text-xs text-muted-foreground font-mono">
                    [{data.position[0].toFixed(1)}, {data.position[1].toFixed(1)}, {data.position[2].toFixed(1)}]
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Objects */}
        <div>
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Objects ({objectCount})</p>
          <div className="mt-3 space-y-2 max-h-40 overflow-y-auto">
            {objectCount === 0 ? (
              <p className="text-xs text-muted-foreground">No objects</p>
            ) : (
              Object.entries(sceneData.objects || {}).map(([id, data]) => (
                <div key={id} className="bg-muted/50 rounded p-2">
                  <p className="text-xs font-semibold text-foreground">{id}</p>
                  <p className="text-xs text-muted-foreground font-mono">
                    [{data.position[0].toFixed(1)}, {data.position[1].toFixed(1)}, {data.position[2].toFixed(1)}]
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Statistics */}
        <div className="border-t border-border pt-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-foreground font-medium">Total Objects</span>
            <span className="text-sm font-mono font-semibold text-primary">{totalCount}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-foreground font-medium">FPS</span>
            <span className="text-sm font-mono font-semibold text-primary">{fps}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
