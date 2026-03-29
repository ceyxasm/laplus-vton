export interface Product {
  id: string;
  name: string;
  category: string;
  description: string;
  price: number;
  image_url: string;
  sizes: string[];
  colors: string[];
}

export interface TryOnJob {
  job_id: string;
  product_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result_image_url?: string;
  error_message?: string;
  created_at: number;
  completed_at?: number;
}

export interface TryOnStartResponse {
  job_id: string;
  status: string;
}
