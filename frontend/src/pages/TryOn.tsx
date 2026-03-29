import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Camera as CameraIcon, Loader2, RefreshCw, Check } from 'lucide-react';
import Camera from '../components/Camera';
import { api } from '../services/api';
import { Product, TryOnJob } from '../types';
import toast from 'react-hot-toast';

type Step = 'camera' | 'prompt' | 'processing' | 'result';

export default function TryOn() {
  const { productId } = useParams<{ productId: string }>();
  const navigate = useNavigate();

  const [product, setProduct] = useState<Product | null>(null);
  const [step, setStep] = useState<Step>('camera');
  const [showCamera, setShowCamera] = useState(true); // Auto-open camera on mount
  const [capturedPhoto, setCapturedPhoto] = useState<Blob | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string>('');
  const [customPrompt, setCustomPrompt] = useState('');
  const [currentJob, setCurrentJob] = useState<TryOnJob | null>(null);
  const [progress, setProgress] = useState(0);
  const [showRegeneratePrompt, setShowRegeneratePrompt] = useState(false);
  const [regeneratePrompt, setRegeneratePrompt] = useState('');

  const ENABLE_CUSTOM_PROMPT = true; // Config param

  useEffect(() => {
    if (productId) {
      loadProduct(productId);
    }
  }, [productId]);

  const loadProduct = async (id: string) => {
    try {
      const data = await api.getProduct(id);
      setProduct(data);
    } catch (error) {
      toast.error('Failed to load product');
      navigate('/');
    }
  };

  const handleCapture = (blob: Blob) => {
    setCapturedPhoto(blob);
    setPhotoPreview(URL.createObjectURL(blob));
    setShowCamera(false);

    if (ENABLE_CUSTOM_PROMPT) {
      setStep('prompt');
    } else {
      startTryOn(blob);
    }
  };

  const startTryOn = async (photo: Blob, prompt?: string) => {
    if (!productId) return;

    try {
      setStep('processing');
      setProgress(0);

      // Start job
      const { job_id } = await api.startTryOn(productId, photo, prompt);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + Math.random() * 15, 95));
      }, 1000);

      // Poll for result
      const job = await api.pollJobStatus(job_id, (updatedJob) => {
        setCurrentJob(updatedJob);
      });

      clearInterval(progressInterval);
      setProgress(100);
      setCurrentJob(job);

      if (job.status === 'completed') {
        setStep('result');
        toast.success('Try-on complete!', { icon: '✨' });
      } else {
        toast.error(job.error_message || 'Try-on failed');
        setStep('camera');
      }
    } catch (error) {
      console.error(error);
      toast.error('Failed to process try-on');
      setStep('camera');
    }
  };

  const handleSubmitPrompt = () => {
    if (capturedPhoto) {
      startTryOn(capturedPhoto, customPrompt || undefined);
    }
  };

  const handleRegenerateClick = () => {
    setShowRegeneratePrompt(true);
  };

  const handleRegenerateSubmit = async () => {
    if (!currentJob || !regeneratePrompt.trim()) {
      toast.error('Please enter styling instructions');
      return;
    }

    try {
      setShowRegeneratePrompt(false);
      setStep('processing');
      setProgress(0);

      const { job_id } = await api.regenerateTryOn(currentJob.job_id, regeneratePrompt);

      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + Math.random() * 15, 95));
      }, 1000);

      const job = await api.pollJobStatus(job_id, (updatedJob) => {
        setCurrentJob(updatedJob);
      });

      clearInterval(progressInterval);
      setProgress(100);
      setCurrentJob(job);

      if (job.status === 'completed') {
        setStep('result');
        setRegeneratePrompt(''); // Reset prompt
        toast.success('Regeneration complete!');
      } else {
        toast.error('Regeneration failed');
      }
    } catch (error) {
      console.error(error);
      toast.error('Failed to regenerate');
    }
  };

  const handleRetake = () => {
    setCapturedPhoto(null);
    setPhotoPreview('');
    setCustomPrompt('');
    setStep('camera');
    setCurrentJob(null);
    setShowCamera(true); // Auto-open camera for "Try Another"
  };

  if (!product) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-gray-700 hover:text-gray-900"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="font-medium">Back</span>
          </button>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-6">
        {/* Product Info */}
        <div className="bg-white rounded-lg p-4 mb-6 shadow-sm flex items-center gap-4">
          <img
            src={product.image_url}
            alt={product.name}
            className="w-16 h-16 object-cover rounded"
          />
          <div>
            <h2 className="font-semibold text-gray-900">{product.name}</h2>
            <p className="text-sm text-gray-600">₹{product.price.toLocaleString('en-IN')}</p>
          </div>
        </div>

        {/* Camera Step */}
        {step === 'camera' && (
          <div className="space-y-4">
            {photoPreview ? (
              <div className="bg-white rounded-lg overflow-hidden shadow-sm">
                <img src={photoPreview} alt="Captured" className="w-full" />
              </div>
            ) : null}

            <button
              onClick={() => setShowCamera(true)}
              className="w-full bg-primary-600 text-white py-4 rounded-lg font-semibold flex items-center justify-center gap-3 hover:bg-primary-700 transition-colors"
            >
              <CameraIcon className="w-6 h-6" />
              {photoPreview ? 'Retake Photo' : 'Open Camera'}
            </button>
          </div>
        )}

        {/* Prompt Step */}
        {step === 'prompt' && (
          <div className="space-y-4">
            <div className="bg-white rounded-lg overflow-hidden shadow-sm">
              <img src={photoPreview} alt="Captured" className="w-full" />
            </div>

            <div className="bg-white rounded-lg p-4 shadow-sm">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Custom Styling (Optional)
              </label>
              <textarea
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="E.g., 'Make it look casual' or 'Add a jacket'"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                rows={3}
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleRetake}
                className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
              >
                Retake
              </button>
              <button
                onClick={handleSubmitPrompt}
                className="flex-1 bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors"
              >
                Generate Try-On
              </button>
            </div>
          </div>
        )}

        {/* Processing Step */}
        {step === 'processing' && (
          <div className="bg-white rounded-lg p-8 shadow-sm text-center space-y-4">
            <Loader2 className="w-12 h-12 animate-spin text-primary-600 mx-auto" />
            <h3 className="text-xl font-semibold">Generating Your Try-On</h3>
            <p className="text-gray-600">
              Creating a photorealistic image of you wearing this item...
            </p>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-sm text-gray-500">{Math.round(progress)}%</p>
          </div>
        )}

        {/* Result Step */}
        {step === 'result' && currentJob?.result_image_url && (
          <div className="space-y-4">
            <div className="bg-white rounded-lg overflow-hidden shadow-sm">
              <img
                src={currentJob.result_image_url}
                alt="Try-on result"
                className="w-full"
              />
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3">
              <Check className="w-5 h-5 text-green-600" />
              <p className="text-green-800 font-medium">Try-on complete!</p>
            </div>

            {!showRegeneratePrompt ? (
              <button
                onClick={handleRegenerateClick}
                className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Regenerate with Different Style
              </button>
            ) : (
              <div className="bg-white rounded-lg p-4 shadow-sm space-y-3">
                <label className="block text-sm font-medium text-gray-700">
                  Enter new styling instructions:
                </label>
                <textarea
                  value={regeneratePrompt}
                  onChange={(e) => setRegeneratePrompt(e.target.value)}
                  placeholder="E.g., 'Make it more formal' or 'Add accessories'"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  rows={3}
                  autoFocus
                />
                <div className="flex gap-3">
                  <button
                    onClick={() => setShowRegeneratePrompt(false)}
                    className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleRegenerateSubmit}
                    className="flex-1 bg-primary-600 text-white py-2 rounded-lg font-semibold hover:bg-primary-700 transition-colors"
                  >
                    Regenerate
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Camera Modal */}
      {showCamera && (
        <Camera onCapture={handleCapture} onClose={() => setShowCamera(false)} />
      )}
    </div>
  );
}
