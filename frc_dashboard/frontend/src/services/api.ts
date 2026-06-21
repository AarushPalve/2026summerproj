import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// API base URL
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api/v1';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => response.data,
  (error: AxiosError<any>) => {
    if (error.response) {
      // Server responded with a status code outside 2xx
      return Promise.reject({
        message: error.response.data?.message || 'Request failed',
        status: error.response.status,
        data: error.response.data
      });
    } if (error.request) {
      // Request was made but no response received
      return Promise.reject({
        message: 'No response received from server',
        status: 0
      });
    }
    // Something happened in setting up the request
    return Promise.reject({
      message: error.message || 'Request setup error'
    });
  }
);

// Health check
export const checkBackendHealth = async (): Promise<boolean> => {
  try {
    const response: { status: string; version?: string } = await api.get('/health');
    return response.status === 'healthy';
  } catch (error) {
    return false;
  }
};

// Check ML pipeline health
export const checkMLHealth = async (): Promise<{
  status: string;
  message: string;
  has_rf_model?: boolean;
}> => {
  return api.get('/predictions/health');
};

// Upload match data
export const uploadMatchData = async (file: File): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/matches/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });

  return response;
};

// Get all teams
export const getAllTeams = async (): Promise<any> => {
  return api.get('/teams');
};

// Get specific team
export const getTeam = async (teamNumber: number): Promise<any> => {
  return api.get(`/teams/${teamNumber}`);
};

// Get team rankings
export const getTeamRankings = async (params: {
  sortBy?: string;
  order?: string;
  limit?: number;
}): Promise<any> => {
  return api.get('/teams/rankings', { params });
};

// Compare teams
export const compareTeams = async (teams: number[]): Promise<any> => {
  return api.get('/teams/compare', { params: { teams: teams.join(',') } });
};

// Get team statistics
export const getTeamStats = async (): Promise<any> => {
  return api.get('/teams/stats');
};

// Predict match outcome
export interface PredictionRequest {
  red_mean_features: number[];
  red_std_features: number[];
  blue_mean_features: number[];
  blue_std_features: number[];
  is_qm?: boolean;
  is_sf?: boolean;
  is_f?: boolean;
}

export const predictMatch = async (request: PredictionRequest): Promise<any> => {
  return api.post('/predictions', request);
};

// Batch predict matches
export const batchPredict = async (requests: PredictionRequest[]): Promise<any> => {
  return api.post('/predictions/batch', requests);
};

// Get match components
export const getMatchComponents = async (): Promise<any> => {
  return api.get('/matches/components');
};

// Get system information
export const getSystemInfo = async (): Promise<any> => {
  return api.get('/stats/system');
};

// Get calculation statistics
export const getCalculationStats = async (): Promise<any> => {
  return api.get('/stats/calculations');
};

// Get metric distributions
export const getDistributions = async (): Promise<any> => {
  return api.get('/stats/distribution');
};

export default api;
