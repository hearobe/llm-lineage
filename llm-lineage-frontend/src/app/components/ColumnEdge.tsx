import React, { FC } from 'react';
import {
  EdgeProps,
  getBezierPath,
  EdgeLabelRenderer,
  BaseEdge,
  Edge,
  MarkerType,
} from '@xyflow/react';
import { Tooltip } from '@chakra-ui/react';
import { InfoIcon } from '@chakra-ui/icons'
import { marker } from 'framer-motion/client';

export type ColumnEdgeData = Edge<{
  transformationSummary: string
}>


export function ColumnEdge({ 
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data 
}: EdgeProps<ColumnEdgeData>) {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  if(data === undefined) {
    return
  }

  return (
    <>
      <BaseEdge id={id} path={edgePath} style={{strokeWidth: '2', markerEnd: {type: MarkerType.Arrow} as any}} />
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            padding: 10,
            borderRadius: 5,
            fontSize: 12,
            fontWeight: 700,
            pointerEvents: 'all',
          }}
          className="nodrag nopan"
        >
          <Tooltip hasArrow label={data.transformationSummary} fontSize='sm' portalProps={{ appendToParentPortal: false }}>
            <InfoIcon />
          </Tooltip>
        </div>
      </EdgeLabelRenderer>
    </>
  );
};
