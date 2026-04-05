'use client';

import React from 'react';

interface SessionInfoProps {
  sessionId: string;
  apiStatus: 'online' | 'offline';
  physicsStatus: 'enabled' | 'disabled';
  onQuickCommand: (prompt: string) => void;
}

export default function SessionInfo({
  sessionId,
  apiStatus,
  physicsStatus,
  onQuickCommand,
}: SessionInfoProps) {
  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white px-4 py-3">
        <h2 className="text-lg font-semibold">ℹ️ Session & Actions</h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Session Info */}
        <div className="space-y-2">
          <h3 className="font-semibold text-gray-700">Session Information</h3>
          <div className="bg-gray-50 p-3 rounded text-xs space-y-1 text-gray-600 font-mono">
            <div>Session ID: <br/><span className="text-gray-500">{sessionId}</span></div>
            <div>
              API Status:{' '}
              <span className={apiStatus === 'online' ? 'text-green-600 font-bold' : 'text-red-600 font-bold'}>
                {apiStatus === 'online' ? '✓ Online' : '✗ Offline'}
              </span>
            </div>
            <div>
              Physics:{' '}
              <span className={physicsStatus === 'enabled' ? 'text-green-600 font-bold' : 'text-orange-600 font-bold'}>
                {physicsStatus === 'enabled' ? '✓ Enabled' : '✗ Disabled'}
              </span>
            </div>
          </div>
        </div>

        {/* Quick Commands */}
        <div className="space-y-2">
          <h3 className="font-semibold text-gray-700">Quick Commands</h3>
          <div className="space-y-2">
            <button
              onClick={() => onQuickCommand('Create a warehouse with a robot')}
              className="w-full px-3 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition text-sm font-medium"
            >
              🏭 Warehouse + Robot
            </button>
            <button
              onClick={() => onQuickCommand('Add three shelves')}
              className="w-full px-3 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition text-sm font-medium"
            >
              📦 Add Shelves
            </button>
            <button
              onClick={() => onQuickCommand('Create scene with 5 robots moving in a circle')}
              className="w-full px-3 py-2 bg-pink-500 text-white rounded-lg hover:bg-pink-600 transition text-sm font-medium"
            >
              🔄 Circle Formation
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
