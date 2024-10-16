'use client'

import { useQuery } from '@tanstack/react-query'

export type ColumnNodeDta = {
    id: string
    columnName: string
    tableName: string
}

export type ColumnEdgeDta = {
    startId: string
    startColumnName: string
    startTableName: string
    endId: string
    endColumnName: string
    endTableName: string
    transformationSummary: string
}

export type Lineage = {
  nodes: ColumnNodeDta[]
  edges: ColumnEdgeDta[]
}

const fetchLineage = async (column_name: string, table_name: string): Promise<Lineage> => {
  const baseURL = 'http://localhost:8000/lineage';
  const params = new URLSearchParams({
    column_name: column_name,
    table_name: table_name
  });
  const response = await fetch(`${baseURL}?${params}`)
  if (!response.ok) {
    throw new Error(String(response.status))
  }
  const data = await response.json()
  return data
}

const useLineage = (input: {columnName: string, tableName: string}) => {
  return useQuery({
    queryKey: ['lineage', input],
    queryFn: () => fetchLineage(input.columnName, input.tableName),
    initialData: {
      nodes: [],
      edges: []
    },
    enabled: false, // Disable the query from automatically running
    retry: false,
  })
}

export { useLineage, fetchLineage }
