import { useState, useEffect, useCallback } from 'react';
import { useApiError } from './useApiError';

/**
 * Custom hook for data fetching with loading and error states
 * @param fetchFunction - Async function to fetch data
 * @param dependencies - Dependencies array for useEffect
 * @returns Object with data, loading, error, and refetch function
 */
export const useDataFetching = <T,>(
  fetchFunction: () => Promise<T>,
  dependencies: any[] = []
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const { error, handleError, clearError } = useApiError();

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      clearError();
      const result = await fetchFunction();
      setData(result);
      return result;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [fetchFunction, handleError, clearError]);

  useEffect(() => {
    fetchData();
  }, dependencies); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    data,
    loading,
    error,
    refetch: fetchData,
    clearError
  };
};