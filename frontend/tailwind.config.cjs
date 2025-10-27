module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6', // 深藍（按鈕、連結）
        up: '#F43F5E', // 鮮紅（漲，熱力圖）
        down: '#10B981', // 亮綠（跌，熱力圖）
        neutral: '#9CA3AF', // 淺灰（次要文字）
        background: '#1E293B', // 深藍灰（背景）
        card: '#2D3748', // 深灰（卡片）
        text: '#F3F4F6', // 近白（主要文字）
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
};

