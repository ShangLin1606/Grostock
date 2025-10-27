import { useState, useEffect } from 'react';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { chatWithAdvisor } from '../../utils/api';

function Advisor() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const suggestedQuestions = [
    '請分析台積電的投資價值',
    '半導體行業的未來趨勢',
    '台股今日表現如何',
  ];

  async function handleSubmit(e) {
    e.preventDefault();
    if (!query.trim()) return;

    const newMessages = [...messages, { type: 'user', text: query }];
    setMessages(newMessages);
    setLoading(true);
    setError(null);

    try {
      console.log(`發送 AI 投顧查詢: ${query}`);
      const responseData = await chatWithAdvisor(query);
      const responseText = typeof responseData === 'string' ? responseData : responseData?.response || '無法獲取回應，請稍後再試';
      setMessages([...newMessages, { type: 'bot', text: responseText }]);
      console.log('AI 投顧回應成功:', responseText);
    } catch (error) {
      console.error(`AI 投顧查詢失敗: ${error.message}`);
      const errorMessage = error.message.includes('RateLimitError') ?
        '抱歉，AI 投顧 API 配額已用盡，請聯繫管理員檢查 XAI_API_KEY 或增加配額。' :
        `抱歉，處理查詢時發生錯誤，請稍後再試。錯誤: ${error.message}`;
      setMessages([...newMessages, { type: 'bot', text: errorMessage }]);
      setError(errorMessage);
    } finally {
      setLoading(false);
      setQuery('');
    }
  }

  function handleSuggestedQuestion(q) {
    setQuery(q);
    handleSubmit({ preventDefault: () => {} });
  }

  function clearHistory() {
    setMessages([]);
    setError(null);
  }

  useEffect(() => {
    if (messages.length > 0) {
      const chatContainer = document.querySelector('.chat-container');
      if (chatContainer) {
        try {
          chatContainer.scrollTop = chatContainer.scrollHeight;
        } catch (err) {
          console.error('滾動到底部失敗:', err.message);
        }
      }
    }
  }, [messages]);

  return (
    <div className="card">
      <h1 className="text-3xl font-bold mb-6 text-text">AI 投顧</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2">
          <div className="bg-card p-4 rounded-lg shadow h-[500px] overflow-y-auto flex flex-col chat-container">
            {messages.length === 0 && !error && !loading && (
              <div className="flex-grow flex items-center justify-center text-neutral">
                開始與 AI 投顧對話吧！
              </div>
            )}
            {error && (
              <div className="text-neutral p-4">{error}</div>
            )}
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`mb-4 flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
              >
                <div className="flex items-start space-x-2">
                  {msg.type === 'bot' && (
                    <img src="/ai-avatar.png" alt="AI" className="w-8 h-8 rounded-full" />
                  )}
                  <div className={msg.type === 'user' ? 'chat-bubble-user' : 'chat-bubble-bot'}>
                    {msg.text || '無法顯示回應'}
                  </div>
                  {msg.type === 'user' && (
                    <img src="/user-avatar.png" alt="User" className="w-8 h-8 rounded-full" />
                  )}
                </div>
              </div>
            ))}
            {loading && <LoadingSpinner message="AI 投顧思考中..." />}
          </div>
          <form onSubmit={handleSubmit} className="flex mt-4">
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="輸入您的問題..."
              className="flex-grow p-2 border rounded-l-md bg-gray-600 text-text border-gray-500"
              disabled={loading}
            />
            <button type="submit" className="btn rounded-l-none" disabled={loading}>送出</button>
          </form>
          <button onClick={clearHistory} className="btn mt-2 bg-gray-600 hover:bg-gray-700" disabled={loading}>
            清除對話
          </button>
        </div>
        <div className="md:col-span-1">
          <div className="bg-card p-4 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4 text-text">AI 投顧簡介</h2>
            <p className="text-neutral mb-4">
              Grostock AI 投顧使用先進的自然語言處理和市場分析技術，為您提供即時的股票分析、投資建議和市場洞察。試試以下問題：
            </p>
            <div className="space-y-2">
              {suggestedQuestions.map((q, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestedQuestion(q)}
                  className="w-full text-left p-2 bg-gray-600 hover:bg-gray-500 rounded-md text-text transition"
                  disabled={loading}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Advisor;