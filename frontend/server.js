const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');
require('dotenv').config();

const app = express();
const port = 5001;

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
});

pool.connect((err, client, release) => {
  if (err) {
    console.error('資料庫連線失敗:', err.message);
    return;
  }
  console.log('成功連接到 PostgreSQL 資料庫');
  release();
});

app.use(express.json());
app.use(cors({
  origin: ['http://localhost:5000', 'http://localhost:5173'],
  methods: ['GET', 'POST'],
  credentials: true,
}));

app.get('/stocks', async (req, res) => {
  try {
    console.log('收到 /stocks 請求');
    const result = await pool.query('SELECT stock_id, stock_name, industry, popularity_score FROM stock_list WHERE is_active = TRUE ORDER BY stock_id');
    console.log(`查詢到 ${result.rows.length} 筆股票數據`);
    if (result.rows.length === 0) {
      console.warn('stock_list 表無 is_active = TRUE 的記錄，請檢查資料庫數據');
    }
    res.json(result.rows);
  } catch (error) {
    console.error('查詢股票列表失敗:', error.message);
    res.status(500).json({ error: `無法獲取股票列表: ${error.message}` });
  }
});

app.get('/stocks/history', async (req, res) => {
  const { stock_id } = req.query;
  try {
    console.log(`收到 /stocks/history 請求，股票: ${stock_id}`);
    const result = await pool.query(`
      SELECT date, price
      FROM stock_prices
      WHERE stock_id = $1 AND date >= CURRENT_DATE - INTERVAL '30 days'
      ORDER BY date
    `, [stock_id]);
    console.log(`查詢到 ${result.rows.length} 筆歷史股價數據`);
    res.json(result.rows);
  } catch (error) {
    console.error(`查詢股票 ${stock_id} 歷史股價失敗:`, error.message);
    res.status(500).json({ error: `無法獲取歷史股價: ${error.message}` });
  }
});

app.get('/stocks/predictions', async (req, res) => {
  const { stock_id } = req.query;
  try {
    console.log(`收到 /stocks/predictions 請求，股票: ${stock_id}`);
    const result = await pool.query(`
      SELECT signal
      FROM predictions
      WHERE stock_id = $1 AND date = (SELECT MAX(date) FROM predictions)
    `, [stock_id]);
    console.log(`查詢到 ${result.rows.length} 筆預測數據`);
    res.json(result.rows[0] || { signal: 0 });
  } catch (error) {
    console.error(`查詢股票 ${stock_id} 預測數據失敗:`, error.message);
    res.status(500).json({ error: `無法獲取預測數據: ${error.message}` });
  }
});

app.listen(port, () => {
  console.log(`前端後端代理運行於 http://localhost:${port}`);
});