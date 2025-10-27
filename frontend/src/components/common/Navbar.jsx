import { Link, useLocation } from 'react-router-dom';

function Navbar() {
  const location = useLocation();
  const navItems = [
    { path: '/', label: '首頁' },
    { path: '/stocks', label: '股票列表' },
    // { path: '/strategy', label: '策略分析' },
    { path: '/advisor', label: 'AI 投顧' },
    // { path: '/heatmap', label: '熱力圖' },
    // { path: '/portfolio', label: '投資組合' },
    { path: '/market', label: '市場概覽' },
    { path: '/about', label: '關於我們' },
  ];

  return (
    <nav className="bg-gray-900 text-text shadow-md">
      <div className="container flex items-center justify-between py-4">
        <Link to="/" className="text-2xl font-bold text-primary">Grostock</Link>
        <ul className="flex space-x-6">
          {navItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`hover:text-primary transition ${
                  location.pathname === item.path ? 'text-primary font-semibold' : 'text-neutral'
                }`}
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;