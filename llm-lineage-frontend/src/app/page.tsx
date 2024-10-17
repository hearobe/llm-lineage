'use client'

import styles from "./page.module.css";
import { LineageGraph } from "./components/LineageGraph";
import { useMutation } from "@tanstack/react-query";
import { Button, ChakraProvider, Flex, Heading, Input, Spacer, useToast } from '@chakra-ui/react'
import { useEffect, useState } from "react";
import { useLineage } from "./hooks/useLineage";
import { triggerLineageTrace } from "./hooks/useTraceLineage";


export default function Home() {
  const [formData, setFormData] = useState({ columnName: '', tableName: '' }); // State for form data
  const [submitData, setSubmitData] = useState<{ columnName: string, tableName: string } | null>(null)

  const { data, error, isError, isLoading, refetch } = useLineage(submitData ?? {columnName: '', tableName: ''});
  const mutation = useMutation({
    mutationFn: triggerLineageTrace
  })
  const toast = useToast()
  
  useEffect(() => {
    if (isError || mutation.isError) {
      const errorCode = error?.message ?? mutation.error?.message as string
      console.log(errorCode)
      if (errorCode === "409") {
        toast({
          title: 'Lineage trace in progress',
          description: "Please wait till the lineage trace has completed",
          status: 'error',
          duration: 9000,
          isClosable: true,
        })
      } else if (errorCode === "404") {
        toast({
          title: 'Column not found',
          description: "Please enter a column that exists in the database",
          status: 'error',
          duration: 9000,
          isClosable: true,
        })
      }
    }
  }, [isError, mutation.isError, error, mutation.error])

  
  
  const handleSubmit = (e: { preventDefault: () => void; }) => {
    e.preventDefault();
    // Only trigger the useLineage hook if both inputs are filled
    if (formData) {
      setSubmitData(formData); // Trigger the query by setting submitData
      refetch()
    }
  };

  const handleChange = (e:any) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className={styles.page}>
        <ChakraProvider>
          <div style={{ width: '100vw', height: '100vh', position: 'fixed' }}>
            <Flex style={{ 
              height: '64px',
              padding:'12px',
              backgroundColor: '#e1e2e3',
              alignItems: 'center',
              borderBottomColor: '#1E293B',
              borderBottomWidth: '4px'
            }}>
              <Heading size='md' color='#1E293B'>LLM LINEAGE</Heading>
              <Spacer />
              <Flex>
                <Input name="columnName" value={formData.columnName} onChange={handleChange} placeholder='Column name' variant='filled' size='md' width='256px' marginX='4px'/>
                <Input name="tableName" value={formData.tableName} onChange={handleChange} placeholder='Table name' variant='filled' size='md' width='256px' marginX='4px'/>
                <Button onClick={handleSubmit} marginX='4px' colorScheme='blue' variant='solid'>Search</Button>
                <Button marginX='4px' onClick={() => {
                    mutation.mutate()
                  }}
                >Trace lineage</Button>
              </Flex>
            </Flex>
            <LineageGraph data={data}/>
          </div>
        </ChakraProvider>
    </div>
  );
}
