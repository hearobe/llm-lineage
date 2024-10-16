import { useMutation } from "@tanstack/react-query";

const triggerLineageTrace = async () => {
  const baseURL = 'http://localhost:8000/request-lineage-trace';
  const response = await fetch(`${baseURL}`, {
    method: "POST"
  })
  if (!response.ok) {
    throw new Error(String(response.status))
  }
  return response
}

export { triggerLineageTrace }
