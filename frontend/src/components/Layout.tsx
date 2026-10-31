import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export const Layout: React.FC = () => (
  <div className="light-rescue min-h-screen bg-slate-50 text-slate-900 flex flex-col">
    <Header />
    <Sidebar />
    <main className="flex-1 w-full overflow-x-hidden px-4 py-6 md:px-8 lg:px-10 lg:py-8 tactical-grid">
      <div className="mx-auto max-w-[1600px]"><Outlet /></div>
    </main>
  </div>
);
