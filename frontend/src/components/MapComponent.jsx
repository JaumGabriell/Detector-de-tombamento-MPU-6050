import { useEffect, useRef, useState } from "react";
import "leaflet/dist/leaflet.css";

export default function MapComponent({ location }) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markerRef = useRef(null);
  const [L, setL] = useState(null);

  const hasPosition = location.latitude && location.longitude;
  const position = hasPosition
    ? [location.latitude, location.longitude]
    : [-22.4256, -45.4528];

  // Carrega Leaflet dinamicamente
  useEffect(() => {
    import("leaflet").then((leaflet) => {
      // Fix para ícone do Leaflet
      delete leaflet.default.Icon.Default.prototype._getIconUrl;
      leaflet.default.Icon.Default.mergeOptions({
        iconRetinaUrl:
          "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
        iconUrl:
          "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
        shadowUrl:
          "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
      });
      setL(leaflet.default);
    });
  }, []);

  // Inicializa o mapa
  useEffect(() => {
    if (!L || !mapRef.current || mapInstanceRef.current) return;

    mapInstanceRef.current = L.map(mapRef.current).setView(position, 17);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(mapInstanceRef.current);

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [L]);

  // Atualiza posição do marcador
  useEffect(() => {
    if (!L || !mapInstanceRef.current) return;

    if (hasPosition) {
      mapInstanceRef.current.setView(
        position,
        mapInstanceRef.current.getZoom(),
      );

      if (markerRef.current) {
        markerRef.current.setLatLng(position);
      } else {
        markerRef.current = L.marker(position)
          .addTo(mapInstanceRef.current)
          .bindPopup(
            `<strong>Carrinho IoT 01</strong><br/>
            Lat: ${location.latitude?.toFixed(6)}<br/>
            Lon: ${location.longitude?.toFixed(6)}<br/>
            Atualizado: ${location.lastUpdate}`,
          );
      }

      // Atualiza popup
      markerRef.current.setPopupContent(
        `<strong>Carrinho IoT 01</strong><br/>
        Lat: ${location.latitude?.toFixed(6)}<br/>
        Lon: ${location.longitude?.toFixed(6)}<br/>
        Atualizado: ${location.lastUpdate}`,
      );
    }
  }, [L, location, hasPosition, position]);

  return (
    <div
      ref={mapRef}
      style={{ height: "100%", minHeight: "400px", width: "100%" }}
    />
  );
}
