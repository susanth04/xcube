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
}

export default function StatePanel({ sceneData }: StatePanelProps) {
  const robotCount = Object.keys(sceneData.robots || {}).length
  const objectCount = Object.keys(sceneData.objects || {}).length
  const totalCount = robotCount + objectCount

  return (
    <div className="flex flex-col rounded-lg bg-white border border-slate-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-200 bg-slate-50">
        <h2 className="font-semibold text-slate-900">Scene State</h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-4 min-h-0">
        {/* Current Scene */}
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase">Scene</p>
          <p className="text-sm font-mono text-slate-900 mt-1">{sceneData.current_scene || '—'}</p>
        </div>

        {/* Robots */}
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase">Robots ({robotCount})</p>
          <div className="mt-2 space-y-1 max-h-24 overflow-y-auto">
            {robotCount === 0 ? (
              <p className="text-xs text-slate-400">No robots</p>
            ) : (
              Object.entries(sceneData.robots || {}).map(([id, data]) => (
                <div key={id} className="bg-slate-100 rounded px-2 py-1">
                  <p className="text-xs font-semibold text-slate-700">{id}</p>
                  <p className="text-xs text-slate-500 font-mono">
                    [{data.position[0].toFixed(1)}, {data.position[1].toFixed(1)}, {data.position[2].toFixed(1)}]
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Objects */}
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase">Objects ({objectCount})</p>
          <div className="mt-2 space-y-1 max-h-24 overflow-y-auto">
            {objectCount === 0 ? (
              <p className="text-xs text-slate-400">No objects</p>
            ) : (
              Object.entries(sceneData.objects || {}).map(([id, data]) => (
                <div key={id} className="bg-slate-100 rounded px-2 py-1">
                  <p className="text-xs font-semibold text-slate-700">{id}</p>
                  <p className="text-xs text-slate-500 font-mono">
                    [{data.position[0].toFixed(1)}, {data.position[1].toFixed(1)}, {data.position[2].toFixed(1)}]
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Statistics */}
        <div className="border-t border-slate-200 pt-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-600">Total Objects</span>
            <span className="text-sm font-mono font-semibold text-purple-600">{totalCount}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
