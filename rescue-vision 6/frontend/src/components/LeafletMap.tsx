import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { Incident } from '../types';

interface LeafletMapProps {
  incidents: Incident[];
  selectedIncident?: Incident | null;
  onSelectIncident?: (incident: Incident) => void;
}

export const LeafletMap: React.FC<LeafletMapProps> = ({
  incidents,
  selectedIncident,
  onSelectIncident,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersGroupRef = useRef<L.LayerGroup | null>(null);

  // Filter valid incidents with coordinates
  const validIncidents = incidents.filter(
    (inc) => inc.latitude !== null && inc.longitude !== null && !isNaN(inc.latitude) && !isNaN(inc.longitude)
  );

  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      // Initialize map centered by default or first coordinate
      const defaultCenter: [number, number] = validIncidents.length > 0 && validIncidents[0].latitude && validIncidents[0].longitude
        ? [validIncidents[0].latitude, validIncidents[0].longitude]
        : [28.6139, 77.2090]; // Default fallback

      const map = L.map(mapContainerRef.current, {
        center: defaultCenter,
        zoom: validIncidents.length > 0 ? 10 : 3,
        zoomControl: true,
      });

      // Dark style tile layer from CartoDB or OpenStreetMap
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19,
      }).addTo(map);

      const markersGroup = L.layerGroup().addTo(map);
      mapInstanceRef.current = map;
      markersGroupRef.current = markersGroup;
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update markers when incidents change
  useEffect(() => {
    if (!mapInstanceRef.current || !markersGroupRef.current) return;

    markersGroupRef.current.clearLayers();

    validIncidents.forEach((inc) => {
      if (inc.latitude === null || inc.longitude === null) return;

      const isCritical = inc.severity === 'CRITICAL' || inc.severity === 'HIGH';
      const markerColor = isCritical ? '#ef4444' : '#ff6a00';

      const customIcon = L.divIcon({
        className: 'custom-incident-pin',
        html: `
          <div style="
            background: ${markerColor};
            width: 22px;
            height: 22px;
            border-radius: 50%;
            border: 2px solid #ffffff;
            box-shadow: 0 0 12px ${markerColor};
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: bold;
            color: #000;
          ">
            ${inc.detection_count || '!'}
          </div>
        `,
        iconSize: [22, 22],
        iconAnchor: [11, 11],
      });

      const marker = L.marker([inc.latitude, inc.longitude], { icon: customIcon });

      const popupContent = `
        <div style="font-family: inherit; font-size: 13px; line-height: 1.4;">
          <div style="font-weight: bold; color: #ff6a00; font-size: 14px; margin-bottom: 4px;">
            ${inc.title}
          </div>
          <div style="color: #94a3b8; font-size: 11px; margin-bottom: 6px;">
            📍 ${inc.location_name || 'Coordinates: ' + inc.latitude.toFixed(4) + ', ' + inc.longitude.toFixed(4)}
          </div>
          <div style="display: flex; gap: 6px; font-size: 10px; font-family: monospace; margin-bottom: 6px;">
            <span style="background: rgba(255, 106, 0, 0.2); color: #ff6a00; padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(255, 106, 0, 0.4);">
              SEVERITY: ${inc.severity}
            </span>
            <span style="background: rgba(0, 229, 255, 0.2); color: #00e5ff; padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(0, 229, 255, 0.4);">
              STATUS: ${inc.status}
            </span>
          </div>
          <div style="color: #f1f5f9; font-weight: 600; font-size: 12px;">
            🚨 ${inc.detection_count} Human Presence Candidate(s)
          </div>
        </div>
      `;

      marker.bindPopup(popupContent);
      marker.on('click', () => {
        if (onSelectIncident) onSelectIncident(inc);
      });

      markersGroupRef.current?.addLayer(marker);
    });

    // Fit bounds if markers exist
    if (validIncidents.length > 0 && mapInstanceRef.current) {
      const bounds = L.latLngBounds(
        validIncidents.map((i) => [i.latitude as number, i.longitude as number])
      );
      mapInstanceRef.current.fitBounds(bounds, { padding: [40, 40], maxZoom: 13 });
    }
  }, [incidents]);

  // Center on selected incident if provided
  useEffect(() => {
    if (selectedIncident && selectedIncident.latitude && selectedIncident.longitude && mapInstanceRef.current) {
      mapInstanceRef.current.setView([selectedIncident.latitude, selectedIncident.longitude], 12);
    }
  }, [selectedIncident]);

  return (
    <div className="relative w-full h-full min-h-[360px] rounded-xl overflow-hidden border border-rescue-800 bg-rescue-950">
      <div ref={mapContainerRef} className="w-full h-full min-h-[360px]" />
      {validIncidents.length === 0 && (
        <div className="absolute inset-0 bg-rescue-950/80 backdrop-blur-sm flex flex-col items-center justify-center p-6 text-center z-[1000]">
          <p className="text-slate-400 font-mono text-sm">NO GEO-TAGGED INCIDENTS LOGGED</p>
          <p className="text-xs text-slate-500 mt-1 max-w-sm">
            Incidents with valid latitude and longitude coordinates will automatically pin onto this operational tactical map.
          </p>
        </div>
      )}
    </div>
  );
};
