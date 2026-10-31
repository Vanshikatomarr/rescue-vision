import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Scan, MapPin, Cpu, Layers, BarChart3, Settings, Home, Route } from 'lucide-react';

const navItems = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/dashboard', label: 'Overview', icon: LayoutDashboard },
  { to: '/detect', label: 'Detection', icon: Scan },
  { to: '/routes', label: 'Rescue Planner', icon: Route },
  { to: '/incidents', label: 'Incidents', icon: MapPin },
  { to: '/training', label: 'Training', icon: Cpu },
  { to: '/models', label: 'Models', icon: Layers },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export const Sidebar: React.FC = () => (
  <nav aria-label="Main navigation" className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 shadow-sm backdrop-blur-md">
    <div className="mx-auto flex max-w-[1600px] items-center gap-1 overflow-x-auto px-3 py-2 md:px-8">
      {navItems.map(({ to, label, icon: Icon }) => (
        <NavLink key={to} to={to} end={to === '/'} className={({isActive}) =>
          `flex shrink-0 items-center gap-2 rounded-xl px-3.5 py-2.5 text-sm font-semibold transition-colors ${isActive
            ? 'bg-orange-50 text-orange-700 ring-1 ring-orange-200'
            : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}`
        }>
          <Icon className="h-4 w-4" /> <span>{label}</span>
        </NavLink>
      ))}
    </div>
  </nav>
);
