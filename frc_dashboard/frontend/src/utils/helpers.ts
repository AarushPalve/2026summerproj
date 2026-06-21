/**
 * Utility functions for the FRC Dashboard frontend
 */

/**
 * Format a number as a percentage with specified decimal places
 * @param value - The number to format
 * @param decimals - Number of decimal places (default: 1)
 * @returns Formatted percentage string
 */
export const formatPercentage = (value: number, decimals: number = 1): string => {
  return `${(value * 100).toFixed(decimals)}%`;
};

/**
 * Format a number with specified decimal places
 * @param value - The number to format
 * @param decimals - Number of decimal places (default: 2)
 * @returns Formatted number string
 */
export const formatNumber = (value: number, decimals: number = 2): string => {
  return value.toFixed(decimals);
};

/**
 * Generate a color based on a value (for visualizations)
 * @param value - The value to convert to color (0-1 range)
 * @returns CSS color string
 */
export const getValueColor = (value: number): string => {
  const hue = Math.floor(120 * (1 - value)); // Red (0) to Green (120)
  return `hsl(${hue}, 75%, 50%)`;
};

/**
 * Generate alliance colors
 * @param alliance - 'red' or 'blue'
 * @returns Object with color values
 */
export const getAllianceColors = (alliance: 'red' | 'blue') => {
  if (alliance === 'red') {
    return {
      main: '#f44336',
      light: '#ef9a9a',
      dark: '#c62828',
      text: 'white'
    };
  } else {
    return {
      main: '#2196f3',
      light: '#90caf9',
      dark: '#0d47a1',
      text: 'white'
    };
  }
};

/**
 * Format team number with proper padding
 * @param teamNumber - The team number
 * @returns Formatted team string
 */
export const formatTeamNumber = (teamNumber: number): string => {
  return `Team ${teamNumber}`;
};

/**
 * Calculate win probability difference
 * @param prob1 - First probability
 * @param prob2 - Second probability
 * @returns Difference as percentage points
 */
export const calculateProbabilityDifference = (prob1: number, prob2: number): number => {
  return Math.abs(prob1 - prob2) * 100;
};

/**
 * Generate a random ID
 * @returns Random string ID
 */
export const generateId = (): string => {
  return Math.random().toString(36).substring(2, 9);
};

/**
 * Debounce function
 * @param func - Function to debounce
 * @param wait - Wait time in milliseconds
 * @returns Debounced function
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null;

  return function(...args: Parameters<T>): void {
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(() => func(...args), wait);
  };
};

/**
 * Format bytes to human-readable size
 * @param bytes - Size in bytes
 * @returns Human-readable size string
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Capitalize first letter of string
 * @param str - Input string
 * @returns Capitalized string
 */
export const capitalize = (str: string): string => {
  if (!str) return str;
  return str.charAt(0).toUpperCase() + str.slice(1);
};

/**
 * Truncate string with ellipsis
 * @param str - Input string
 * @param maxLength - Maximum length
 * @returns Truncated string
 */
export const truncate = (str: string, maxLength: number): string => {
  if (str.length <= maxLength) return str;
  return str.substring(0, maxLength) + '...';
};