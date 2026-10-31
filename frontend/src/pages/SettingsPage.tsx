import React, { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon,
  Server,
  Sliders,
  Cpu,
  ShieldAlert,
  CheckCircle2,
  RefreshCw,
  HardDrive,
  ExternalLink,
} from 'lucide-react';
import { api } from '../services/api';
import { HealthStatus } from '../types';
import { StatusBadge } from '../components/StatusBadge';

export const SettingsPage: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [savedMsg, setSavedMsg] = useState<string | null>(null);

  // Local settings state
  const [defaultConf, setDefaultConf] = useState<number>(0.25);
  const [defaultImgSize, setDefaultImgSize] = useState<number>(640);

  const fetchHealth = async () => {
    try {
      setLoading(true);
      const data = await api.getHealth();
      setHealth(data);
    } catch (err) {
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const handleSaveDefaults = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('rescue_default_conf', defaultConf.toString());
    localStorage.setItem('rescue_default_img_size', defaultImgSize.toString());
    setSavedMsg('Operational inference preferences saved to browser storage.');
    setTimeout(() => setSavedMsg(null), 3000);
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Page Header */}
      <div className="p-6 rounded-2xl border border-rescue-800 bg-rescue-900/60 backdrop-blur-md">
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <SettingsIcon className="w-6 h-6 text-slate-300" />
          Application & Inference Settings
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Configure default computer vision heuristics, hardware accelerators, and API endpoints.
        </p>
      </div>

      {savedMsg && (
        <div className="p-4 rounded-xl border border-emerald-500/40 bg-emerald-950/30 text-emerald-300 flex items-center gap-3 text-xs font-mono">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>{savedMsg}</span>
        </div>
      )}

      {/* Backend & Hardware Diagnostics */}
      <div className="p-6 rounded-2xl border border-rescue-800 bg-rescue-900/60 space-y-5">
        <div className="flex items-center justify-between border-b border-rescue-800 pb-3">
          <div className="flex items-center gap-2">
            <Server className="w-5 h-5 text-alert-cyan" />
            <h3 className="font-bold text-sm text-white">System Diagnostics & Hardware Status</h3>
          </div>
          <button
            onClick={fetchHealth}
            className="p-1.5 rounded-lg border border-rescue-700 bg-rescue-800 text-slate-300 hover:text-white"
            title="Refresh Diagnostics"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
          <div className="p-4 rounded-xl border border-rescue-800 bg-rescue-950">
            <div className="text-slate-500 mb-1">API CONNECTION</div>
            <StatusBadge status={health ? 'ONLINE' : 'OFFLINE'} size="sm" />
          </div>

          <div className="p-4 rounded-xl border border-rescue-800 bg-rescue-950">
            <div className="text-slate-500 mb-1">COMPUTE DEVICE</div>
            <div className="font-bold text-alert-cyan uppercase text-sm">
              {health?.active_device || 'Detecting...'}
            </div>
            <div className="text-[10px] text-slate-500 truncate">{health?.device_info}</div>
          </div>

          <div className="p-4 rounded-xl border border-rescue-800 bg-rescue-950">
            <div className="text-slate-500 mb-1">LOADED CHECKPOINT</div>
            <div className="font-bold text-alert-orange text-sm truncate">
              {health?.active_model || 'None'}
            </div>
          </div>

          <div className="p-4 rounded-xl border border-rescue-800 bg-rescue-950">
            <div className="text-slate-500 mb-1">API VERSION</div>
            <div className="font-bold text-slate-200 text-sm">
              {health?.version || 'v1.0.0'}
            </div>
          </div>
        </div>
      </div>

      {/* Inference Defaults Configuration */}
      <form
        onSubmit={handleSaveDefaults}
        className="p-6 rounded-2xl border border-rescue-800 bg-rescue-900/60 space-y-5"
      >
        <div className="flex items-center gap-2 border-b border-rescue-800 pb-3">
          <Sliders className="w-5 h-5 text-alert-orange" />
          <h3 className="font-bold text-sm text-white">Default Inference Heuristics</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs font-mono">
          <div className="space-y-2">
            <label className="text-slate-300 block">Default Confidence Threshold ({(defaultConf * 100).toFixed(0)}%)</label>
            <input
              type="range"
              min="0.10"
              max="0.80"
              step="0.05"
              value={defaultConf}
              onChange={(e) => setDefaultConf(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-rescue-800 rounded-lg appearance-none cursor-pointer accent-alert-orange"
            />
            <p className="text-[11px] text-slate-500">
              Initial slider value loaded when opening the Detection Workspace.
            </p>
          </div>

          <div className="space-y-2">
            <label className="text-slate-300 block">Default Input Resolution (ImgSize)</label>
            <select
              value={defaultImgSize}
              onChange={(e) => setDefaultImgSize(parseInt(e.target.value))}
              className="w-full bg-rescue-950 border border-rescue-800 rounded-lg px-3 py-2 text-white focus:outline-none"
            >
              <option value={320}>320px (Rapid Scanning / Low Memory)</option>
              <option value={640}>640px (Standard Optical Balance)</option>
              <option value={1280}>1280px (High Resolution Aerials)</option>
            </select>
            <p className="text-[11px] text-slate-500">
              YOLO input resolution used to resize incoming imagery.
            </p>
          </div>
        </div>

        <div className="flex justify-end pt-3 border-t border-rescue-800">
          <button
            type="submit"
            className="py-2.5 px-6 rounded-xl font-bold text-xs uppercase font-mono text-white bg-alert-orange hover:bg-orange-600 shadow-glow-orange transition"
          >
            Save Heuristics
          </button>
        </div>
      </form>

      {/* OpenAPI Swagger Documentation Link */}
      <div className="p-6 rounded-2xl border border-rescue-800 bg-rescue-900/40 flex items-center justify-between">
        <div className="space-y-1">
          <div className="text-sm font-bold text-white">Interactive Swagger OpenAPI Documentation</div>
          <p className="text-xs text-slate-400">
            Inspect all FastAPI REST endpoints, schemas, and live test forms.
          </p>
        </div>
        <a
          href={`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/docs`}
          target="_blank"
          rel="noreferrer"
          className="px-4 py-2.5 rounded-xl border border-rescue-700 bg-rescue-800 hover:bg-rescue-750 text-xs font-mono text-alert-cyan flex items-center gap-1.5 transition"
        >
          <span>Open /docs</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  );
};
