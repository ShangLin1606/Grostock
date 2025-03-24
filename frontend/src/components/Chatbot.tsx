import React, { useState } from 'react';
import { chatWithBot } from '../api';

const Chatbot: React.FC = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<{ user: string; bot: string }[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const response = await chatWithBot(query);
      setMessages([...messages, { user: query, bot: response }]);
      setQuery('');
    } catch (error) {
      console.error('Error chatting with bot:', error);
      setMessages([...messages, { user: query, bot: '抱歉，發生錯誤，請稍後再試。' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleMarketSummary = async () => {
    setLoading(true);
    try {
      const response = await chatWithBot("請提供當天市場消息懶人包");
      setMessages([...messages, { user: "請提供當天市場消息懶人包", bot: response }]);
    } catch (error) {
      console.error('Error fetching market summary:', error);
      setMessages([...messages, { user: "請提供當天市場消息懶人包", bot: '抱歉，發生錯誤，請稍後再試。' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>智能問答機器人</h2>
      <div className="chat-container">
        {messages.map((msg, index) => (
          <div key={index}>
            <p><strong>你:</strong> {msg.user}</p>
            <p><strong>機器人:</strong> {msg.bot}</p>
          </div>
        ))}
      </div>
      <input
        type="text"
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="輸入問題（例如：請分析股票 2330 的價格和風險）"
        onKeyPress={e => e.key === 'Enter' && handleSend()}
      />
      <button onClick={handleSend} disabled={loading}>
        {loading ? '處理中...' : '發送'}
      </button>
      <button onClick={handleMarketSummary} disabled={loading}>
        {loading ? '處理中...' : '當天市場懶人包'}
      </button>
    </div>
  );
};

export default Chatbot;