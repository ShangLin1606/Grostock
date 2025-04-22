import { useState } from 'react';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { chatWithAdvisor } from '../../utils/api';

function Advisor() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!query.trim()) return;

    setMessages([...messages, { type: 'user', text: query }]);
    setLoading(true);

    try {
      const response = await chatWithAdvisor(query);
      setMessages(prev => [...prev, { type: 'bot', text: response }]);
    } catch (error) {
      console.error('Error chatting with advisor:', error);
      setMessages(prev => [...prev, { type: 'bot', text: '抱歉，AI 投顧目前無法回應，請稍後再試。' }]);
    } finally {
      setLoading(false);
      setQuery('');
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">AI 投顧</h1>
      <div className="bg-white p-4 rounded-lg shadow mb-8 h-96 overflow-y-auto">
        {messages.map((msg, index) => (
          <div key={index} className={`mb-4 ${msg.type === 'user' ? 'text-right' : 'text-left'}`}>
            <span className={`inline-block p-2 rounded-lg ${msg.type === 'user' ? 'bg-blue-100' : 'bg-gray-100'}`}>
              {msg.text}
            </span>
          </div>
        ))}
        {loading && <LoadingSpinner message="AI 投顧思考中..." />}
      </div>
      <form onSubmit={handleSubmit} className="flex">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="輸入您的問題（如：請分析台積電的投資價值）"
          className="flex-grow p-2 border rounded-l-md"
        />
        <button type="submit" className="btn rounded-l-none">送出</button>
      </form>
    </div>
  );
}

export default Advisor;