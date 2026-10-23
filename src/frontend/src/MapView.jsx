import { useEffect } from "react";
import L from "leaflet";
import {
  GeoJSON,
  MapContainer,
  TileLayer,
  ZoomControl,
  useMap,
} from "react-leaflet";

function MapBounds({ layers, aoiBounds }) {
  const map = useMap();
  useEffect(() => {
    const featureCollection = {
      type: "FeatureCollection",
      features: layers
        .filter(({ type }) => type === "geojson")
        .flatMap(({ data }) =>
          data.type === "FeatureCollection"
            ? data.features
            : data.type === "Feature"
              ? [data]
              : [],
        ),
    };
    const bounds = featureCollection.features.length
      ? L.geoJSON(featureCollection).getBounds()
      : aoiBounds
        ? L.latLngBounds(
            [aoiBounds[1], aoiBounds[0]],
            [aoiBounds[3], aoiBounds[2]],
          )
        : null;
    if (bounds?.isValid()) map.fitBounds(bounds, { padding: [36, 36], maxZoom: 13 });
  }, [map, layers, aoiBounds]);
  return null;
}

function featureStyle(feature) {
  const kind = feature.properties?.kind;
  if (kind === "road") return { color: "#52525b", weight: 2, opacity: 0.8 };
  const access = feature.properties?.access;
  if (access) {
    const fillColor =
      access === "isolated" || access === "inundated"
        ? "#dc2626"
        : access === "connected"
          ? "#16a34a"
          : "#71717a";
    return { color: "#ffffff", weight: 2, fillColor, fillOpacity: 1 };
  }
  return {
    color: "#2563eb",
    fillColor: "#60a5fa",
    fillOpacity: 0.25,
    weight: 1.5,
  };
}

function pointStyle(feature, latlng) {
  return L.circleMarker(latlng, { radius: 6, ...featureStyle(feature) });
}

function bindFeaturePopup(feature, layer) {
  const properties = feature.properties ?? {};
  const title = properties.name ?? properties.place ?? properties.kind ?? "Map feature";
  const content = document.createElement("div");
  content.textContent = String(title);
  if (properties.access) {
    const status = document.createElement("div");
    status.textContent = `Access: ${properties.access}`;
    content.append(status);
  }
  layer.bindPopup(content);
}

export default function MapView({ layers, aoiBounds }) {
  return (
    <MapContainer
      className="leaflet-map"
      center={[20, 0]}
      zoom={2}
      zoomControl={false}
      scrollWheelZoom
      aria-label="Analysis map"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <ZoomControl position="bottomright" />
      {layers.map((layer) =>
        layer.type === "xyz" ? (
          <TileLayer
            key={layer.key}
            attribution={layer.attribution ?? ""}
            url={layer.url}
            opacity={layer.opacity ?? 1}
          />
        ) : (
          <GeoJSON
            key={layer.key}
            data={layer.data}
            style={featureStyle}
            pointToLayer={pointStyle}
            onEachFeature={bindFeaturePopup}
          />
        ),
      )}
      <MapBounds layers={layers} aoiBounds={aoiBounds} />
    </MapContainer>
  );
}
