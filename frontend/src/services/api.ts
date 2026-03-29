import axios from 'axios';
import { Product, TryOnJob, TryOnStartResponse } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export const api = {
  // Products
  getProducts: async (category?: string): Promise<Product[]> => {
    const params = category ? { category } : {};
    const response = await axios.get(`${API_BASE}/products`, { params });
    return response.data;
  },

  getProduct: async (id: string): Promise<Product> => {
    const response = await axios.get(`${API_BASE}/products/${id}`);
    return response.data;
  },

  // Try-on
  startTryOn: async (
    productId: string,
    personImage: Blob,
    customPrompt?: string
  ): Promise<TryOnStartResponse> => {
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('person_image', personImage, 'photo.jpg');
    if (customPrompt) {
      formData.append('custom_prompt', customPrompt);
    }

    const response = await axios.post(`${API_BASE}/tryon/start`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getJobStatus: async (jobId: string): Promise<TryOnJob> => {
    const response = await axios.get(`${API_BASE}/tryon/status/${jobId}`);
    return response.data;
  },

  regenerateTryOn: async (
    jobId: string,
    customPrompt: string
  ): Promise<TryOnStartResponse> => {
    const formData = new FormData();
    formData.append('custom_prompt', customPrompt);

    const response = await axios.post(
      `${API_BASE}/tryon/regenerate/${jobId}`,
      formData
    );
    return response.data;
  },

  // Polling helper
  pollJobStatus: async (
    jobId: string,
    onUpdate: (job: TryOnJob) => void,
    interval: number = 2000,
    maxAttempts: number = 60
  ): Promise<TryOnJob> => {
    let attempts = 0;

    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const job = await api.getJobStatus(jobId);
          onUpdate(job);

          if (job.status === 'completed' || job.status === 'failed') {
            resolve(job);
          } else if (attempts >= maxAttempts) {
            reject(new Error('Polling timeout'));
          } else {
            attempts++;
            setTimeout(poll, interval);
          }
        } catch (error) {
          reject(error);
        }
      };

      poll();
    });
  },
};
