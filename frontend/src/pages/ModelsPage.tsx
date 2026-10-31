import React, { useState, useEffect } from 'react';
import {
  Layers,
  CheckCircle2,
  Cpu,
  ShieldCheck,
  Zap,
  RefreshCw,
  AlertCircle,
  FileCode,
} from 'lucide-react';
import { api } from '../services/api';
import { ModelRecord } from '../types';
import { StatusBadge } from '../components/StatusBadge';

export const ModelsPage: React.FC = () => {
  const [models, setModels] = useState<ModelRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [activatingId, setActivatingId] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchModels = async () => {
    try {
      setLoading(true);
      const data = await api.getModels();
      setModels(data);
    } catch (err: any) {
      setErrorMessage('Failed to load registered models.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const handleActivateModel = async (id: string, name: string) => {
    setActivatingId(id);
    setStatusMessage(null);
    setErrorMessage(null);

    try {
      const res = await api.activateModel(id);
      setStatusMessage(res.message);
      await fetchModels();
    } catch (err: any) {
      setErrorMessage(err?.response?.data?.detail || 'Checkpoint activation failed verification.');
    } finally {
      setActivatingId(null);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl border border-rescue-800 bg-rescue-900/60 backdrop-blur-md">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <Layers className="w-6 h-6 text-alert-cyan" />
            Model Registry & Checkpoint Management
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Deploy validated YOLO26 checkpoints into live inference. Every activation undergoes runtime weight verification.
          </p>
        </div>

        <button
          onClick={fetchModels}
          className="px-3.5 py-2 rounded-xl border border-rescue-700 bg-rescue-800 text-xs font-mono text-slate-300 hover:text-white flex items-center gap-2 transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh Registry
        </button>
      </div>

      {statusMessage && (
        <div className="p-4 rounded-xl border border-emerald-500/40 bg-emerald-950/30 text-emerald-300 flex items-center gap-3 text-xs font-mono">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>{statusMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div className="p-4 rounded-xl border border-red-500/40 bg-red-950/30 text-red-300 flex items-center gap-3 text-xs font-mono">
          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Models Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {models.map((model) => (
          <div
            key={model.id}
            className={`p-6 rounded-2xl border transition-all duration-200 flex flex-col justify-between space-y-5 ${
              model.is_active
                ? 'border-alert-orange/60 bg-rescue-900/90 shadow-glow-orange/20 ring-1 ring-alert-orange/40'
                : 'border-rescue-800 bg-rescue-900/60 hover:border-slate-600'
            }`}
          >
            <div className="space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-widest text-alert-cyan">
                    {model.base_family}
                  </span>
                  <h3 className="text-lg font-bold text-white mt-0.5">{model.name}</h3>
                  <span className="text-xs font-mono text-slate-400">Version: {model.version}</span>
                </div>

                {model.is_active ? (
                  <span className="px-2.5 py-1 rounded-full border border-alert-orange bg-alert-orange/20 text-alert-orange text-xs font-mono font-bold flex items-center gap-1 shadow-glow-orange">
                    <Zap className="w-3 h-3 fill-current" />
                    ACTIVE
                  </span>
                ) : (
                  <span className="px-2.5 py-1 rounded-full border border-rescue-700 bg-rescue-800 text-slate-400 text-xs font-mono">
                    STANDBY
                  </span>
                )}
              </div>

              {/* Evaluation Metrics Strip */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono bg-rescue-950 p-3 rounded-xl border border-rescue-800">
                <div>
                  <div className="text-[10px] text-slate-500">mAP@0.50</div>
                  <div className="font-bold text-emerald-400">
                    {model.map50 !== null && model.map50 !== undefined
                      ? `${(model.map50 * 100).toFixed(1)}%`
                      : 'N/A'}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-500">mAP@0.50:0.95</div>
                  <div className="font-bold text-slate-200">
                    {model.map50_95 !== null && model.map50_95 !== undefined
                      ? `${(model.map50_95 * 100).toFixed(1)}%`
                      : 'N/A'}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-500">PRECISION</div>
                  <div className="font-bold text-alert-cyan">
                    {model.precision !== null && model.precision !== undefined
                      ? `${(model.precision * 100).toFixed(1)}%`
                      : 'N/A'}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-500">RECALL</div>
                  <div className="font-bold text-alert-orange">
                    {model.recall !== null && model.recall !== undefined
                      ? `${(model.recall * 100).toFixed(1)}%`
                      : 'N/A'}
                  </div>
                </div>
              </div>

              {/* Checkpoint File Path */}
              <div className="text-[11px] font-mono text-slate-400 bg-rescue-950/60 p-2.5 rounded-lg border border-rescue-800/80 truncate">
                <FileCode className="w-3.5 h-3.5 text-slate-500 inline mr-1.5" />
                <span className="truncate">{model.checkpoint_path}</span>
              </div>
            </div>

            {/* Action Button */}
            <div>
              {model.is_active ? (
                <div className="py-2.5 px-4 rounded-xl border border-emerald-500/30 bg-emerald-950/30 text-emerald-400 text-xs font-mono font-bold text-center flex items-center justify-center gap-1.5">
                  <ShieldCheck className="w-4 h-4" />
                  Primary Inference Model
                </div>
              ) : (
                <button
                  onClick={() => handleActivateModel(model.id, model.name)}
                  disabled={activatingId === model.id}
                  className="w-full py-2.5 px-4 rounded-xl border border-rescue-700 bg-rescue-800 hover:bg-alert-orange hover:border-alert-orange text-xs font-mono font-bold text-white transition flex items-center justify-center gap-2 group"
                >
                  {activatingId === model.id ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin text-alert-orange" />
                      Validating & Hot-Swapping...
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4 text-alert-orange group-hover:text-white" />
                      Activate For Inference
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
