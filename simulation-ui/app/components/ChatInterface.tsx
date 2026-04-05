'use client';

import React, { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  text: string;
  type: 'user' | 'assistant' | 'info' | 'error';
  timestamp: Date;
}

interface ChatInterfaceProps {
  onSendPrompt: (prompt: string) => void;
  isLoading: boolean;
  apiStatus: 'online' | 'offline';
  physicsStatus: 'enabled' | 'disabled';
}

export default function ChatInterface({
  onSendPrompt,
  isLoading,
  apiStatus,
  physicsStatus,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: '🎮 3D Simulation Ready! Describe your scenario...',
      type: 'info',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (input.trim()) {
      const userMessage: Message = {
        id: Date.now().toString(),
        text: input,
        type: 'user',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      onSendPrompt(input);
      setInput('');

      // Add loading indicator
      const loadingMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Processing...',
        type: 'info',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, loadingMessage]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const addMessage = (text: string, type: 'user' | 'assistant' | 'info' | 'error') => {
    setMessages((prev) => [
      ...prev.filter((m) => m.type !== 'info' || m.text !== 'Processing...'),
      {
        id: Date.now().toString(),
        text,
        type,
        timestamp: new Date(),
      },
    ]);
  };

  React.useImperativeHandle(
    React.createRef(),
    () => ({
      addMessage,
    })
  );

  const getMessageColor = (type: string) => {
    switch (type) {
      case 'user':
        return 'bg-blue-500 text-white ml-auto';
      case 'error':
        return 'bg-red-100 text-red-800 border border-red-400';
      case 'info':
        return 'bg-gray-100 text-gray-800 italic';
      default:
        return 'bg-gray-200 text-gray-800';
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white px-4 py-3 flex justify-between items-center">
        <h2 className="text-lg font-semibold">💬 Chat Interface</h2>
        <span className={`text-xs px-2 py-1 rounded ${
          apiStatus === 'online' ? 'bg-green-500' : 'bg-red-500'
        }`}>
          {apiStatus === 'online' ? '🟢 Online' : '🔴 Offline'}
        </span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-xs px-3 py-2 rounded-lg text-sm break-words ${getMessageColor(
                msg.type
              )}`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4 space-y-2">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe your simulation scenario..."
            disabled={isLoading}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
        <div className="text-xs text-gray-500">
          Physics: {physicsStatus === 'enabled' ? '✓ Enabled' : '✗ Disabled'}
        </div>
      </div>
    </div>
  );
}
