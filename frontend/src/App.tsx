import React from 'react';
import StockList from './components/StockList';
import StockAnalysis from './components/StockAnalysis';
import Chatbot from './components/Chatbot';
import './styles.css';

const App: React.FC = () => {
  return (
    <div className="container">
      <h1>Grostock - 股票分析平台</h1>
      <StockList />
      <StockAnalysis />
      <Chatbot />
    </div>
  );
};

export default App;