import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import PriceChart from '../../components/charts/PriceChart';
import axios from 'axios';

function StockList() {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [selectedStock, setSelectedStock] = useState(null);
  const [historyData, setHistoryData] = useState({});
  const [predictionData, setPredictionData] = useState({});

  const industryMap = {
    'ETF': 'ETF',
    'Building Materials': '建材',
    'Packaged Foods': '包裝食品',
    'Beverages - Non-Alcoholic': '非酒精飲料',
    'Conglomerates': '綜合企業',
    'Farm Products': '農產品',
    'Confectioners': '糖果製造',
    'Specialty Chemicals': '特種化學品',
    'Chemicals': '化學品',
    'Textile Manufacturing': '紡織製造',
    'Apparel Manufacturing': '服裝製造',
    'Real Estate Services': '房地產服務',
    'Auto Parts': '汽車零部件',
    'Packaging & Containers': '包裝與容器',
    'Business Equipment & Supplies': '商業設備與用品',
    'Real Estate - Development': '房地產開發',
    'Leisure': '休閒',
    'Real Estate - Diversified': '多元化房地產',
    'Integrated Freight & Logistics': '綜合貨運與物流',
    'Apparel Retail': '服裝零售',
    'Electrical Equipment & Parts': '電氣設備與零件',
    'Specialty Industrial Machinery': '特種工業機械',
    'Thermal Coal': '熱能煤',
    'Metal Fabrication': '金屬製造',
    'Pollution & Treatment Controls': '污染與處理控制',
    'Tools & Accessories': '工具與配件',
    'Furnishings, Fixtures & Appliances': '家具、固定裝置與家電',
    'Electronics & Computer Distribution': '電子與電腦分銷',
    'Steel': '鋼鐵',
    'Computer Hardware': '電腦硬體',
    'Footwear & Accessories': '鞋類與配件',
    'Auto Manufacturers': '汽車製造',
    'Auto & Truck Dealerships': '汽車與卡車經銷',
    'Aerospace & Defense': '航空航天與國防',
    'Semiconductor Equipment & Materials': '半導體設備與材料',
    'Semiconductors': '半導體',
    'Communication Equipment': '通訊設備',
    'Electronic Components': '電子元件',
    'Scientific & Technical Instruments': '科學與技術儀器',
    'Consumer Electronics': '消費電子',
    'Solar': '太陽能',
    'Engineering & Construction': '工程與建築',
    'Marine Shipping': '海運',
    'Trucking': '卡車運輸',
    'Airlines': '航空公司',
    'Railroads': '鐵路',
    'Airports & Air Services': '機場與航空服務',
    'Lodging': '住宿',
    'Resorts & Casinos': '度假村與賭場',
    'Restaurants': '餐飲',
    'Travel Services': '旅遊服務',
    'Banks - Regional': '區域銀行',
    'Insurance - Diversified': '多元化保險',
    'Capital Markets': '資本市場',
    'Insurance - Property & Casualty': '財產與意外險',
    'Insurance - Reinsurance': '再保險',
    'Insurance - Life': '人壽保險',
    'Financial Conglomerates': '金融綜合企業',
    'Department Stores': '百貨公司',
    'Oil & Gas Equipment & Services': '油氣設備與服務',
    'Home Improvement Retail': '家居改善零售',
    'Grocery Stores': '雜貨店',
    'Internet Retail': '網路零售',
    'Software - Application': '應用軟體',
    'Software - Infrastructure': '基礎設施軟體',
    'Drug Manufacturers - Specialty & Generic': '特種與學名藥製造',
    'Agricultural Inputs': '農業投入',
    'Household & Personal Products': '家用與個人產品',
    'Biotechnology': '生物技術',
    'Medical Instruments & Supplies': '醫療儀器與用品',
    'Building Products & Equipment': '建築產品與設備',
    'Paper & Paper Products': '紙張與紙製品',
    'Copper': '銅',
    'Credit Services': '信貸服務',
    'Security & Protection Services': '安全與保護服務',
    'Electronic Gaming & Multimedia': '電子遊戲與多媒體',
    'Other Industrial Metals & Mining': '其他工業金屬與採礦',
    'Broadcasting': '廣播',
    'Utilities - Regulated Gas': '受監管天然氣公用事業',
    'Medical Distribution': '醫療分銷',
    'Medical Devices': '醫療設備',
    'Industrial Distribution': '工業分銷',
    'Waste Management': '廢棄物管理',
    'Utilities - Renewable': '可再生能源公用事業',
    'Luxury Goods': '奢侈品',
    'Recreational Vehicles': '休閒車輛',
    'Staffing & Employment Services': '人力資源與就業服務',
    'Advertising Agencies': '廣告代理',
    'Entertainment': '娛樂',
    'Consulting Services': '諮詢服務',
    'Medical Care Facilities': '醫療設施',
    'Asset Management': '資產管理',
    'Lumber & Wood Production': '木材與木製品',
    'Diagnostics & Research': '診斷與研究',
    'Unknown': '未知'
};

  useEffect(() => {
    async function fetchData() {
      try {
        console.log('開始獲取股票列表');
        const response = await axios.get('http://localhost:5001/stocks');
        console.log('股票列表 API 回應:', response.data);
        if (response.data.length === 0) {
          setError('資料庫中無活躍股票數據，請確認 stock_list 表是否有 is_active = TRUE 的記錄。');
        }
        const mappedStocks = response.data.map(stock => ({
          ...stock,
          industry: industryMap[stock.industry] || stock.industry || '未知'
        }));
        setStocks(mappedStocks);
        setLoading(false);
        console.log(`股票列表獲取成功，獲取 ${mappedStocks.length} 筆歷史數據`);

        for (const stock of mappedStocks) {
          try {
            const historyResponse = await axios.get(`http://localhost:5001/stocks/history?stock_id=${stock.stock_id}`);
            const predictionResponse = await axios.get(`http://localhost:5001/stocks/predictions?stock_id=${stock.stock_id}`);
            setHistoryData(prev => ({ ...prev, [stock.stock_id]: historyResponse.data }));
            setPredictionData(prev => ({ ...prev, [stock.stock_id]: predictionResponse.data }));
          } catch (err) {
            console.error(`股票 ${stock.stock_id} 歷史或預測數據獲取失敗: ${err.message}`);
          }
        }
      } catch (error) {
        console.error(`獲取股票列表失敗: ${error.message}`);
        setError(`無法連接到後端服務（http://localhost:5001/stocks），請檢查 Node.js 後端代理或資料庫連線。錯誤訊息: ${error.message}`);
        setStocks([]);
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const filteredStocks = stocks.filter(stock =>
    stock.stock_id.includes(search) || stock.stock_name.includes(search)
  );

  const handleStockClick = (stockId) => {
    setSelectedStock(selectedStock === stockId ? null : stockId);
  };

  if (loading) return <LoadingSpinner message="載入股票列表..." />;

  return (
    <div className="card">
      <h1 className="text-3xl font-bold mb-6 text-text">股票列表</h1>
      <input
        type="text"
        placeholder="搜尋股票 ID 或名稱..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        className="w-full p-2 mb-4 border rounded-md bg-gray-600 text-text border-gray-500"
      />
      {error ? (
        <p className="text-neutral">{error}</p>
      ) : stocks.length === 0 ? (
        <p className="text-neutral">無股票數據，請檢查資料庫或後端服務。</p>
      ) : (
        <div className="bg-gray-700 rounded-lg shadow overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-600">
              <tr>
                <th className="px-4 py-2 text-left text-text">股票 ID</th>
                <th className="px-4 py-2 text-left text-text">名稱</th>
                <th className="px-4 py-2 text-left text-text">行業</th>
                <th className="px-4 py-2 text-left text-text">預測趨勢</th>
                <th className="px-4 py-2 text-left text-text">操作</th>
              </tr>
            </thead>
            <tbody>
              {filteredStocks.map(stock => (
                <>
                  <tr key={stock.stock_id} className="border-t border-gray-600">
                    <td className="px-4 py-2 cursor-pointer" onClick={() => handleStockClick(stock.stock_id)}>{stock.stock_id}</td>
                    <td className="px-4 py-2">{stock.stock_name}</td>
                    <td className="px-4 py-2">{stock.industry}</td>
                    <td className="px-4 py-2">
                      {predictionData[stock.stock_id] && predictionData[stock.stock_id].trend ? (
                        predictionData[stock.stock_id].trend === 'up' ? (
                          <span className="text-up">預測上漲</span>
                        ) : predictionData[stock.stock_id].trend === 'down' ? (
                          <span className="text-down">預測下跌</span>
                        ) : (
                          <span className="text-neutral">預測持平</span>
                        )
                      ) : (
                        <span className="text-neutral">無預測數據</span>
                      )}
                    </td>
                    <td className="px-4 py-2">
                      <Link to={`/stocks/${stock.stock_id}`} className="text-primary hover:underline">查看詳情</Link>
                    </td>
                  </tr>
                  {selectedStock === stock.stock_id && historyData[stock.stock_id] && (
                    <tr>
                      <td colSpan="5" className="px-4 py-2">
                        <PriceChart data={{
                          actual: historyData[stock.stock_id].map(d => ({ date: d.date, price: d.price }))
                        }} />
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default StockList;