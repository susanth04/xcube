'use client'

import { Canvas } from '@react-three/fiber'
import { PerspectiveCamera, OrbitControls, Grid } from '@react-three/drei'
import { Suspense, useMemo } from 'react'

interface Scene3DProps {
  sceneState?: {
    current_scene?: string
    robots?: Record<string, { position: [number, number, number] }>
    objects?: Record<string, { position: [number, number, number] }>
  }
}

function Robot({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      <mesh position={[0, 0, 0.4]}>
        <sphereGeometry args={[0.4, 16, 16]} />
        <meshStandardMaterial color="#ff4444" />
      </mesh>
      <mesh position={[0, 0, 0.8]}>
        <sphereGeometry args={[0.15, 12, 12]} />
        <meshStandardMaterial color="#ffaa00" />
      </mesh>
      <mesh position={[-0.4, 0, 0.2]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.2, 0.2, 0.1, 12]} />
        <meshStandardMaterial color="#222222" />
      </mesh>
      <mesh position={[0.4, 0, 0.2]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.2, 0.2, 0.1, 12]} />
        <meshStandardMaterial color="#222222" />
      </mesh>
    </group>
  )
}

function SimObject({ position }: { position: [number, number, number] }) {
  return (
    <mesh position={position}>
      <boxGeometry args={[0.8, 0.8, 0.8]} />
      <meshStandardMaterial color="#4488ff" />
    </mesh>
  )
}

function SceneContent({ sceneState }: { sceneState?: Scene3DProps['sceneState'] }) {
  const robots = useMemo(() => {
    if (!sceneState?.robots) return []
    return Object.entries(sceneState.robots)
  }, [sceneState?.robots])

  const objects = useMemo(() => {
    if (!sceneState?.objects) return []
    return Object.entries(sceneState.objects)
  }, [sceneState?.objects])

  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[20, 20, 20]} intensity={0.8} />

      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[50, 50]} />
        <meshStandardMaterial color="#2a2a4e" />
      </mesh>

      <Grid 
        args={[50, 50]} 
        cellSize={1} 
        cellColor="#444466" 
        sectionSize={5} 
        sectionColor="#333355" 
        fadeDistance={50} 
      />

      {robots.map(([id, data]) => (
        <Robot key={id} position={data.position} />
      ))}

      {objects.map(([id, data]) => (
        <SimObject key={id} position={data.position} />
      ))}
    </>
  )
}

export default function Scene3D({ sceneState }: Scene3DProps) {
  return (
    <div className="w-full h-full bg-slate-900 rounded-lg overflow-hidden">
      <Suspense fallback={<div className="w-full h-full flex items-center justify-center text-white text-sm">Loading...</div>}>
        <Canvas 
          frameloop="demand"
          gl={{ antialias: false, powerPreference: 'low-power' }}
        >
          <PerspectiveCamera makeDefault position={[10, 10, 10]} fov={75} />
          <color attach="background" args={['#1a1a2e']} />
          <SceneContent sceneState={sceneState} />
          <OrbitControls />
        </Canvas>
      </Suspense>
    </div>
  )
}
