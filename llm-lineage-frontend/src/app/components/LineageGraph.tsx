'use client'

import React, { useCallback, useEffect, useMemo } from 'react'
import { useLineage, Lineage } from '../hooks/useLineage'
import dagre from '@dagrejs/dagre'
import { addEdge, Background, Controls, MarkerType, ReactFlow, useEdgesState, useNodesState } from '@xyflow/react'
import { ColumnNode } from './ColumnNode'

import '@xyflow/react/dist/style.css'
import { ColumnEdge } from './ColumnEdge'

const getLayoutedElements = (data: Lineage) => {
  var g = new dagre.graphlib.Graph();

  // Set an object for the graph label
  // g.setGraph({});

  // Default to assigning a new object as a label for each new edge.
  g.setDefaultEdgeLabel(function() { return {}; });
  g.setGraph({
    rankdir: 'LR',
    align: 'UR',
    nodesep: 25,
    ranksep: 50,
  })

  const nodes = data.nodes ?? []
  nodes.forEach(node => {
    g.setNode(node.id, {
      label: node.columnName,  
      width: 320,              
      height: 52               
    });
  });

  const edges = data.edges ?? []
  edges.forEach(edge => {
    g.setEdge(edge.startId, edge.endId)
  })

  dagre.layout(g)

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = g.node(node.id)
    return {
      id: node.id,
      type: 'column',
      position: {
        x: nodeWithPosition.x,
        y: nodeWithPosition.y
      },
      data: {
        label: node.id,
        id: node.id,
        columnName: node.columnName,
        tableName: node.tableName
      }
    }
  })

  const layoutedEdges = edges.map((edge) => {
    return {
      id: edge.startId + '-' + edge.endId,
      type: 'columnEdge',
      source: edge.startId,
      target: edge.endId,
      sourceHandle: edge.startId,
      targetHandle: edge.endId,
      markerEnd: {
        type: MarkerType.Arrow,
        width: 15,
        height: 15,
      },
      data: {
        transformationSummary: edge.transformationSummary
      },
      style: {
        strokeWidth: 2,
      },
    }
  })

  return { layoutedNodes, layoutedEdges }
}

export function LineageGraph ({ data }: { data: Lineage }) {
  // const { data, isPending, isFetching, isError, error } = useLineage('district_frl_eligible_percent', 'dim_districts')
  const { layoutedNodes, layoutedEdges } = useMemo(() => getLayoutedElements(data), [data])

  // if (isPending) return <div>Loading</div>

  const [nodes, setNodes, onNodesChange] = useNodesState(layoutedNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(layoutedEdges);
  useEffect(() => {
    if (layoutedNodes.length) {
      setNodes(layoutedNodes);
    }
  }, [layoutedNodes]);

  useEffect(() => {
    if (layoutedEdges.length) {
      setEdges(layoutedEdges);
    }
  }, [layoutedEdges]);

  const onConnect = useCallback(
    (params: any) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  const nodeTypes = useMemo(() => ({ column: ColumnNode }), []);
  const edgeTypes = useMemo(() => ({ columnEdge: ColumnEdge}), [])

  return(
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
      >
        <Background />
        <Controls position='top-left'/>
      </ReactFlow>
    </div>
  )
}
