function About() {
  console.log('進入關於我們頁面');
  return (
    <div className="card">
      <h1 className="text-3xl font-bold mb-6 text-primary">關於 Grostock</h1>
      <section className="bg-gray-700 p-6 rounded-lg shadow">
        <h2 className="text-2xl font-semibold mb-4 text-primary">我們的使命</h2>
        <p className="mb-4 text-gray-300">
          Grostock 致力於為投資者提供專業的財經數據分析與 AI 投顧服務，幫助您做出更明智的投資決策。
        </p>
        <h2 className="text-2xl font-semibold mb-4 text-primary">核心功能</h2>
        <ul className="list-disc pl-6 mb-4 text-gray-300">
          <li>即時股票價格與預測分析</li>
          <li>多策略信號與回測結果</li>
          <li>AI 投顧互動式問答</li>
          <li>股市熱力圖與新聞聲量分析</li>
          <li>投資組合管理與優化</li>
        </ul>
        <h2 className="text-2xl font-semibold mb-4 text-primary">聯繫我們</h2>
        <p className="text-gray-300">電郵: support@grostock.com | 電話: +886-2-1234-5678</p>
      </section>
    </div>
  );
}

export default About;