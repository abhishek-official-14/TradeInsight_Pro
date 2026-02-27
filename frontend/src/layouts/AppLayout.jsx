import { Outlet } from 'react-router-dom';
import { Navbar } from '../components/Navbar';

export const AppLayout = () => (
  <div className="app-shell">
    <Navbar />
    <main className="page-shell">
      <Outlet />
    </main>
  </div>
);
