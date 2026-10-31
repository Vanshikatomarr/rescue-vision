import React, { useState, useEffect } from 'react';
import {
  MapPin,
  Plus,
  Search,
  Filter,
  Download,
  Trash2,
  Edit2,
  CheckCircle2,
  AlertTriangle,
  X,
  FileSpreadsheet,
  Globe,
  Radio,
} from 'lucide-react';
import { api } from '../services/api';
import { Incident } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { LeafletMap } from '../components/LeafletMap';

export const IncidentsPage: React.FC = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [search, setSearch] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [editingIncident, setEditingIncident] = useState<Incident | null>(null);

  // Form State
  const [title, setTitle] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [locationName, setLocationName] = useState<string>('');
  const [latitude, setLatitude] = useState<string>('');
  const [longitude, setLongitude] = useState<string>('');
  const [severity, setSeverity] = useState<string>('HIGH');
  const [status, setStatus] = useState<string>('OPEN');
  const [notes, setNotes] = useState<string>('');

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      const data = await api.getIncidents(search, statusFilter, severityFilter);
      setIncidents(data);
      if (data.length > 0 && !selectedIncident) {
        setSelectedIncident(data[0]);
      }
    } catch (err) {
      console.error('Failed to load incidents', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [search, statusFilter, severityFilter]);

  const handleOpenCreateModal = () => {
    setEditingIncident(null);
    setTitle('');
    setDescription('');
    setLocationName('');
    setLatitude('');
    setLongitude('');
    setSeverity('HIGH');
    setStatus('OPEN');
    setNotes('');
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (inc: Incident) => {
    setEditingIncident(inc);
    setTitle(inc.title);
    setDescription(inc.description);
    setLocationName(inc.location_name);
    setLatitude(inc.latitude !== null ? inc.latitude.toString() : '');
    setLongitude(inc.longitude !== null ? inc.longitude.toString() : '');
    setSeverity(inc.severity);
    setStatus(inc.status);
    setNotes(inc.notes);
    setIsModalOpen(true);
  };

  const handleSaveIncident = async (e: React.FormEvent) => {
    e.preventDefault();
    const lat = latitude ? parseFloat(latitude) : null;
    const lng = longitude ? parseFloat(longitude) : null;

    try {
      if (editingIncident) {
        await api.updateIncident(editingIncident.id, {
          title,
          description,
          location_name: locationName,
          latitude: lat,
          longitude: lng,
          severity: severity as any,
          status: status as any,
          notes,
        });
      } else {
        await api.createIncident({
          title,
          description,
          location_name: locationName,
          latitude: lat,
          longitude: lng,
          severity: severity as any,
          status: status as any,
          notes,
        });
      }
      setIsModalOpen(false);
      fetchIncidents();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to save incident');
    }
  };

  const handleDeleteIncident = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this rescue incident record?')) {
      try {
        await api.deleteIncident(id);
        fetchIncidents();
        if (selectedIncident?.id === id) {
          setSelectedIncident(null);
        }
      } catch (err) {
        alert('Failed to delete incident');
      }
    }
  };

  const handleExportCsv = () => {
    window.open(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/incidents/export/csv`, '_blank');
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl border border-rescue-800 bg-rescue-900/60 backdrop-blur-md">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <MapPin className="w-6 h-6 text-alert-cyan" />
            Disaster Incident Records & Map
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Log, track, and locate ground rescue operations with OpenStreetMap tactical GIS.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleExportCsv}
            className="px-3.5 py-2 rounded-xl border border-rescue-700 bg-rescue-800 text-xs font-semibold text-slate-200 hover:text-white flex items-center gap-2 transition"
          >
            <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
            Export CSV
          </button>
          <button
            onClick={handleOpenCreateModal}
            className="px-4 py-2 rounded-xl bg-alert-orange hover:bg-orange-600 text-xs font-bold text-white shadow-glow-orange flex items-center gap-2 transition"
          >
            <Plus className="w-4 h-4" />
            Log New Incident
          </button>
        </div>
      </div>

      {/* Map Section */}
      <div className="rounded-2xl border border-rescue-800 p-4 bg-rescue-900/40">
        <div className="flex items-center justify-between mb-3 px-2">
          <div className="flex items-center gap-2 text-xs font-mono text-slate-300">
            <Globe className="w-4 h-4 text-alert-cyan" />
            <span>OPENSTREETMAP TACTICAL GEO-PINNING</span>
          </div>
          <span className="text-[11px] text-slate-500 font-mono">
            {incidents.filter((i) => i.latitude !== null).length} Geo-tagged Sites
          </span>
        </div>
        <div className="h-80 w-full rounded-xl overflow-hidden">
          <LeafletMap
            incidents={incidents}
            selectedIncident={selectedIncident}
            onSelectIncident={(inc) => setSelectedIncident(inc)}
          />
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 rounded-xl border border-rescue-800 bg-rescue-900/50">
        <div className="md:col-span-2 relative">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
          <input
            type="text"
            placeholder="Search incidents by title, description, or location..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-rescue-950 border border-rescue-800 rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-alert-cyan"
          />
        </div>

        <div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full bg-rescue-950 border border-rescue-800 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none"
          >
            <option value="">All Statuses</option>
            <option value="OPEN">OPEN</option>
            <option value="IN_PROGRESS">IN_PROGRESS</option>
            <option value="RESOLVED">RESOLVED</option>
            <option value="CLOSED">CLOSED</option>
          </select>
        </div>

        <div>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="w-full bg-rescue-950 border border-rescue-800 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none"
          >
            <option value="">All Severities</option>
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>
        </div>
      </div>

      {/* Incidents Table */}
      <div className="rounded-2xl border border-rescue-800 bg-rescue-900/60 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-rescue-950 text-slate-400 font-mono border-b border-rescue-800">
              <tr>
                <th className="py-3 px-4">Title & Location</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Human Candidates</th>
                <th className="py-3 px-4">Coordinates</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-rescue-800/60 text-slate-300">
              {incidents.length > 0 ? (
                incidents.map((inc) => (
                  <tr
                    key={inc.id}
                    onClick={() => setSelectedIncident(inc)}
                    className={`hover:bg-rescue-800/40 cursor-pointer transition ${
                      selectedIncident?.id === inc.id ? 'bg-rescue-800/30' : ''
                    }`}
                  >
                    <td className="py-3 px-4">
                      <div className="font-bold text-white text-sm">{inc.title}</div>
                      <div className="text-[11px] text-slate-400 flex items-center gap-1 mt-0.5">
                        <MapPin className="w-3 h-3 text-alert-cyan" />
                        {inc.location_name || 'Unspecified location'}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={inc.severity} size="sm" />
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={inc.status} size="sm" />
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-alert-orange text-sm">
                      {inc.detection_count}
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-400">
                      {inc.latitude !== null && inc.longitude !== null
                        ? `${inc.latitude.toFixed(4)}, ${inc.longitude.toFixed(4)}`
                        : 'No GPS coords'}
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenEditModal(inc);
                        }}
                        className="p-1.5 rounded-lg bg-rescue-800 hover:bg-rescue-700 text-slate-300 hover:text-white"
                        title="Edit Incident"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteIncident(inc.id);
                        }}
                        className="p-1.5 rounded-lg bg-rescue-800 hover:bg-red-900/60 text-slate-300 hover:text-red-400"
                        title="Delete Incident"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-slate-500 font-mono">
                    No incidents match search criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal for Create/Edit */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-rescue-900 border border-rescue-700 rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-rescue-800 pb-3">
              <h3 className="font-bold text-white text-base">
                {editingIncident ? 'Edit Incident Record' : 'Log New Rescue Incident'}
              </h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveIncident} className="space-y-4 text-xs font-mono">
              <div className="space-y-1">
                <label className="text-slate-400 block">Incident Title *</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Earthquake Collapsed Plaza - Zone 3"
                  className="w-full bg-rescue-950 border border-rescue-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-alert-orange"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-400 block">Location Name</label>
                <input
                  type="text"
                  value={locationName}
                  onChange={(e) => setLocationName(e.target.value)}
                  placeholder="e.g. District 4 River Basin"
                  className="w-full bg-rescue-950 border border-rescue-800 rounded-lg px-3 py-2 text-white focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-slate-400 block">Latitude (optional)</label>
                  <input
                    type="number"
                    step="any"
                    value={latitude}
                    onChange={(e) => setLatitude(e.target.value)}
                    placeholder="e.g. 28.6139"
                    className="w-full bg-rescue-950 border border-rescue-800 rounded-lg px-3 py-2 text-white focus:outline-none"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-slate-400 block">Longitude (optional)</label>
                  <input
                    type="number"
                    step="any"
                    value={longitude}
                    onChange={(e) => setLongitude(e.target.value)}
                    placeholder="e.g. 77.2090"
                    className="w-full bg-rescue-950 border border-rescue-800 rounded-lg px-3 py-2 text-white focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-slate-400 block">Severity</label>
                  <select
                    value={severity}
                    onChange={(e) => setSeverity(e.target.value)}
                    className="w-full bg-rescue-950 border border-rescue-800 rounded-lg px-3 py-2 text-white focus:outline-none"
                  >
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-slate-400 block">Status</label>
                  <select
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                    className="w-full bg-rescue-950 border border-rescue-800 rounded-lg px-3 py-2 text-white focus:outline-none"
                  >
                    <option value="OPEN">OPEN</option>
                    <option value="IN_PROGRESS">IN_PROGRESS</option>
                    <option value="RESOLVED">RESOLVED</option>
                    <option value="CLOSED">CLOSED</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-slate-400 block">Description & Ground Notes</label>
                <textarea
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Operational details, acoustic sensors, thermal signs..."
                  className="w-full bg-rescue-950 border border-rescue-800 rounded-lg px-3 py-2 text-white focus:outline-none"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-rescue-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-lg bg-rescue-800 text-slate-300 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-lg bg-alert-orange hover:bg-orange-600 text-white font-bold"
                >
                  Save Incident
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
