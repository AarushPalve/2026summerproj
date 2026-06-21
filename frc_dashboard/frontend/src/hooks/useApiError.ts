import { useState } from 'react';
import { AxiosError } from 'axios';

/**
 * Custom hook for handling API errors
 * @returns Object with error state and handlers
 */
export const useApiError = () => {
  const [error, setError] = useState<string | null>(null);

  const handleError = (err: unknown) => {
    let errorMessage = 'An unknown error occurred';

    if (err instanceof Error) {
      errorMessage = err.message;
    } else if (typeof err === 'string') {
      errorMessage = err;
    } else if (
      typeof err === 'object' &&
      err !== null &&
      'message' in err &&
      typeof err.message === 'string'
    ) {
      errorMessage = err.message;
    } else if (
      typeof err === 'object' &&
      err !== null &&
      'response' in err &&
      typeof err.response === 'object' &&
      err.response !== null &&
      'data' in err.response &&
      typeof err.response.data === 'object' &&
      err.response.data !== null &&
      'message' in err.response.data &&
      typeof err.response.data.message === 'string'
    ) {
      errorMessage = err.response.data.message;
    }

    setError(errorMessage);
    return errorMessage;
  };

  const clearError = () => {
    setError(null);
  };

  return {
    error,
    setError,
    handleError,
    clearError
  };
};