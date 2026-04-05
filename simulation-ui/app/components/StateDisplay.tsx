'use client';

import React from 'react';

interface SceneState {
  current_scene: string;
  robots: Record<string, { position: [number, number, number] }>;
  objects: Record<string, { position: [number, number, number] }>;
}

interface Action {
  type: string;
  [key: string]: any;
}

interface StateDisplayProps {
  sceneState: SceneState;
  actions: Action[];
  objectCount: number;
  fps: number;
}

export default function StateDisplay({
  sceneState,
  actions,
  objectCount,
  fps,
}: StateDisplayProps) {
  const robots = Object.entries(sceneState.robots || {});
  const objects = Object.entries(sceneState.objects || {});

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white px-4 py-3">
        <h2 className="text-lg font-semibold">📊 Simulation State & Statistics</h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Current Scene */}
        <div className="space-y-2">
          <h3 className="font-semibold text-gray-700">Current Scene</h3>
          <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
            {sceneState.current_scene || '—'}
          </div>
        </div>

        {/* Robots */}
        <div className="space-y-2">
          <h3 className="font-semibold text-gray-700">Robots</h3>
          <ul className="text-sm space-y-1">
            {robots.length > 0 ? (
              robots.map(([id, data]) => (
                <li key={id} className="text-gray-600">
                  → <strong>{id}</strong>: [
                  {data.position.map((p) => p.toFixed(1)).join(', ')}]
                </li>
              ))
            ) : (
              <li className="text-gray-400 italic">None</li>
            )}
          </ul>
        </div>

        {/* Objects */}
        <div className="space-y-2">
          <h3 className="font-semibold text-gray-700">Objects</h3>
          <ul className="text-sm space-y-1">
            {objects.length > 0 ? (
              objects.map(([id, data]) => (
                <li key={id} className="text-gray-600">
                  → <strong>{id}</strong>: [
                  {data.position.map((p) => p.toFixed(1)).join(', ')}]
                </li>
              ))
            ) : (
              <li className="text-gray-400 italic">None</li>
            )}
          </ul>
        </div>

        {/* Statistics */}
        <div className="space-y-2 pt-2 border-t border-gray-200">
          <h3 className="font-semibold text-gray-700">Statistics</h3>
          <div className="text-sm space-y-1 text-gray-600">
            <div>Total Objects: <strong>{objectCount}</strong></div>
            <div>FPS: <strong>{fps}</strong></div>
          </div>
        </div>
      </div>
    </div>
  );
}
