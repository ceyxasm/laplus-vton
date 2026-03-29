import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Catalog from './pages/Catalog';
import ProductDetail from './pages/ProductDetail';
import TryOn from './pages/TryOn';

function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-center" />
      <Routes>
        <Route path="/" element={<Catalog />} />
        <Route path="/product/:id" element={<ProductDetail />} />
        <Route path="/tryon/:productId" element={<TryOn />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
