import { NodeProps, Node, Handle, Position } from "@xyflow/react"
import { ColumnNodeDta } from "../hooks/useLineage"

export type ColumnNodeData = Node<ColumnNodeDta>

// ReactFlow is scaling everything by the factor of 2
const NODE_WIDTH = 320
const NODE_ROW_HEIGHT = 40

export function ColumnNode({ data }: NodeProps<ColumnNodeData>) {
    // Important styles is a nasty hack to use Handles (required for edges calculations), but do not show them in the UI.
    // ref: https://github.com/wbkd/react-flow/discussions/2698
    const handleStyles = {
        height: '1px',
        width: '1px',
        minWidth: '0',
        minHeight: '0',
        cursor: 'grab',
        border: '0',
        opacity: '0',
      }
  
    return (
      <>
        <div style={{ width: NODE_WIDTH, borderRadius: '0.5rem', overflow: 'hidden'}}>
            <header style={{
                fontSize: '0.75rem',
                lineHeight: '1.25rem',
                fontWeight: 'bolder',
                padding: '0 0.5rem',
                textAlign: 'center',
                backgroundColor: '#1E293B',
                color: '#D1D5DB'
            }}>
                {data.tableName}
            </header>
            <div
            style={{
                fontSize: '8px',
                lineHeight: '2rem',
                position: 'relative',
                display: 'flex',
                justifyContent: 'space-between',
                backgroundColor: '#E5E7EB'
            }}
            >
                <span style={{
                    fontSize: '1rem',
                    fontWeight: 'bold',
                    width: '100%',
                    padding: '0.75 0.5rem',
                    textAlign: 'center',
                    color: '#1E293B',
                    textOverflow: 'ellipsis',
                }}
                >
                    {data.columnName}
                </span>
            </div>
            <Handle
                type="target"
                id={data.id}
                position={Position.Left}
                style={handleStyles}
            />
            <Handle
                type="source"
                id={data.id}
                position={Position.Right}
                style={handleStyles}
            />
        </div>
      </>
    )
  }
