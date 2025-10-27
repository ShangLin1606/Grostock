import { Outlet } from 'react-router-dom';
import Navbar from './components/common/Navbar';
import Footer from './components/common/Footer';

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Navbar />
      <main className="flex-grow container py-8">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}

export default App;