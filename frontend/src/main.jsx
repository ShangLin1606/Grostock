import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App.jsx';
import Home from './pages/home/Home.jsx';
import StockList from './pages/stockList/StockList.jsx';
import StockDetail from './pages/stockDetail/StockDetail.jsx';
import Strategy from './pages/strategy/Strategy.jsx';
import Advisor from './pages/aiAdvisor/Advisor.jsx';
import Heatmap from './pages/heatmap/Heatmap.jsx';
import About from './pages/about/About.jsx';
import './styles/tailwind.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />}>
        <Route index element={<Home />} />
        <Route path="stocks" element={<StockList />} />
        <Route path="stocks/:stockId" element={<StockDetail />} />
        <Route path="strategy" element={<Strategy />} />
        <Route path="advisor" element={<Advisor />} />
        <Route path="heatmap" element={<Heatmap />} />
        <Route path="about" element={<About />} />
      </Route>
    </Routes>
  </BrowserRouter>
);