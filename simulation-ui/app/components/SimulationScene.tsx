'use client';

import React, { useRef, useEffect, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Grid, AxesHelper, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';

interface SceneState {
  current_scene: string;
  robots: Record<string, { position: [number, number, number] }>;
  objects: Record<string, { position: [number, number, number] }>;
}

interface Robot {
  id: string;
  position: [number, number, number];
}

interface SimObject {
  id: string;
  position: [number, number, number];
}

function RobotMesh({ id, position }: Robot) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame(() => {
    if (groupRef.current) {
      groupRef.current.rotation.z += 0.01;
    }
  });

  return (
    <group ref={groupRef} position={position}>
      {/* Main body - red sphere */}
      <mesh castShadow receiveShadow>
        <sphereGeometry args={[0.4, 32, 32]} />
        <meshStandardMaterial color={0xff4444} />
      </mesh>

      {/* Top indicator - gold sphere */}
      <mesh castShadow position={[0, 0, 0.4]}>
        <sphereGeometry args={[0.15, 16, 16]} />
        <meshStandardMaterial color={0xffaa00} />
      </mesh>

      {/* Wheel 1 */}
      <mesh castShadow position={[-0.4, 0, 0.2]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.2, 0.2, 0.1, 16]} />
        <meshStandardMaterial color={0x222222} />
      </mesh>

      {/* Wheel 2 */}
      <mesh castShadow position={[0.4, 0, 0.2]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.2, 0.2, 0.1, 16]} />
        <meshStandardMaterial color={0x222222} />
      </mesh>
    </group>
  );
}

function ObjectMesh({ id, position }: SimObject) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.x += 0.005;
      meshRef.current.rotation.y += 0.007;
    }
  });

  return (
    <mesh
      ref={meshRef}
      castShadow
      receiveShadow
      position={position}
    >
      <boxGeometry args={[0.8, 0.8, 0.8]} />
      <meshStandardMaterial color={0x4488ff} />
    </mesh>
  );
}

function Ground() {
  return (
    <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
      <planeGeometry args={[50, 50]} />
      <meshStandardMaterial color={0x2a2a4e} />
    </mesh>
  );
}

function Lighting() {
  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight
        position={[20, 20, 20]}
        intensity={0.8}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />
    </>
  );
}

function SceneContent({ sceneState }: { sceneState: SceneState }) {
  return (
    <>
      <Lighting />
      <Ground />
      <AxesHelper args={[5]} />
      <Grid args={[50, 50]} cellSize={1} cellColor={0x444466} sectionSize={10} sectionColor={0x333355} />

      {/* Render robots */}
      {Object.entries(sceneState.robots || {}).map(([id, data]) => (
        <RobotMesh
          key={id}
          id={id}
          position={data.position}
        />
      ))}

      {/* Render objects */}
      {Object.entries(sceneState.objects || {}).map(([id, data]) => (
        <ObjectMesh
          key={id}
          id={id}
          position={data.position}
        />
      ))}
    </>
  );
}

export default function SimulationScene({ sceneState }: { sceneState: SceneState }) {
  return (
    <div className="w-full h-full relative">
      <Canvas
        shadows
        camera={{ position: [10, 10, 10], fov: 75 }}
        style={{ width: '100%', height: '100%' }}
      >
        <SceneContent sceneState={sceneState} />
        <OrbitControls />
      </Canvas>
    </div>
  );
}
