'use client'

import { Canvas } from '@react-three/fiber'
import { PerspectiveCamera, OrbitControls, Grid } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef, useEffect, useState, Suspense } from 'react'
import * as THREE from 'three'

interface Scene3DProps {
  sceneState?: {
    current_scene?: string
    robots?: Record<string, { position: [number, number, number] }>
    objects?: Record<string, { position: [number, number, number] }>
  }
}

function Robot({ id, position }: { id: string; position: [number, number, number] }) {
  const groupRef = useRef<THREE.Group>(null)

  useFrame(() => {
    if (groupRef.current) {
      groupRef.current.rotation.z += 0.01
    }
  })

  return (
    <group ref={groupRef} position={position}>
      {/* Main body - red sphere */}
      <mesh position={[0, 0, 0.4]}>
        <sphereGeometry args={[0.4, 32, 32]} />
        <meshStandardMaterial color="#ff4444" />
      </mesh>

      {/* Top indicator - gold sphere */}
      <mesh position={[0, 0, 0.8]}>
        <sphereGeometry args={[0.15, 16, 16]} />
        <meshStandardMaterial color="#ffaa00" />
      </mesh>

      {/* Wheels */}
      <mesh position={[-0.4, 0, 0.2]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.2, 0.2, 0.1, 16]} />
        <meshStandardMaterial color="#222222" />
      </mesh>
      <mesh position={[0.4, 0, 0.2]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.2, 0.2, 0.1, 16]} />
        <meshStandardMaterial color="#222222" />
      </mesh>
    </group>
  )
}

function SimObject({ id, position }: { id: string; position: [number, number, number] }) {
  const meshRef = useRef<THREE.Mesh>(null)

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.x += 0.005
      meshRef.current.rotation.y += 0.007
    }
  })

  return (
    <mesh ref={meshRef} position={position}>
      <boxGeometry args={[0.8, 0.8, 0.8]} />
      <meshStandardMaterial color="#4488ff" />
    </mesh>
  )
}

function AxesHelper() {
  return (
    <group>
      {/* X axis (red) */}
      <mesh position={[2.5, 0, 0]}>
        <boxGeometry args={[5, 0.1, 0.1]} />
        <meshBasicMaterial color="#ff0000" />
      </mesh>
      {/* Y axis (green) */}
      <mesh position={[0, 2.5, 0]}>
        <boxGeometry args={[0.1, 5, 0.1]} />
        <meshBasicMaterial color="#00ff00" />
      </mesh>
      {/* Z axis (blue) */}
      <mesh position={[0, 0, 2.5]}>
        <boxGeometry args={[0.1, 0.1, 5]} />
        <meshBasicMaterial color="#0000ff" />
      </mesh>
    </group>
  )
}

function SceneContent({ sceneState }: { sceneState?: Scene3DProps['sceneState'] }) {
  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.5} />
      <directionalLight position={[20, 20, 20]} intensity={0.8} castShadow />

      {/* Ground */}
      <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[50, 50]} />
        <meshStandardMaterial color="#2a2a4e" />
      </mesh>

      {/* Grid and helpers */}
      <Grid args={[50, 50]} cellSize={1} cellColor="#444466" sectionSize={5} sectionColor="#333355" fadeDistance={100} />
      <AxesHelper />

      {/* Robots */}
      {sceneState?.robots &&
        Object.entries(sceneState.robots).map(([id, data]) => (
          <Robot key={id} id={id} position={data.position} />
        ))}

      {/* Objects */}
      {sceneState?.objects &&
        Object.entries(sceneState.objects).map(([id, data]) => (
          <SimObject key={id} id={id} position={data.position} />
        ))}
    </>
  )
}

export default function Scene3D({ sceneState }: Scene3DProps) {
  return (
    <div className="w-full h-full bg-slate-900 rounded-lg overflow-hidden">
      <Suspense fallback={<div className="w-full h-full flex items-center justify-center text-white">Loading 3D scene...</div>}>
        <Canvas shadows>
          <PerspectiveCamera makeDefault position={[10, 10, 10]} fov={75} />
          <color attach="background" args={['#1a1a2e']} />
          <fog attach="fog" args={['#1a1a2e', 50, 100]} />
          <SceneContent sceneState={sceneState} />
          <OrbitControls />
        </Canvas>
      </Suspense>
    </div>
  )
}
