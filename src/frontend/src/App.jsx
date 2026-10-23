import { useEffect, useMemo, useState } from "react";
import { createRun, getRun } from "./api.js";
import { algorithms, defaultParameters } from "./algorithms.js";
import MapView from "./MapView.jsx";
import Sidebar from "./Sidebar.jsx";

const POLL_INTERVAL_MS = 3000;

export default function App() {
  const [selectedAlgorithmId, setSelectedAlgorithmId] = useState(algorithms[0].id);
  const [parameters, setParameters] = useState(() => defaultParameters(algorithms[0]));
  const [aoiText, setAoiText] = useState("");
  const [dateStart, setDateStart] = useState("");
  const [dateEnd, setDateEnd] = useState("");
  const [polarisation, setPolarisation] = useState("VV");
  const [runs, setRuns] = useState([]);
  const [visibleLayerKeys, setVisibleLayerKeys] = useState([]);
  const [requestError, setRequestError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const selectedAlgorithm = useMemo(
    () => algorithms.find(({ id }) => id === selectedAlgorithmId) ?? algorithms[0],
    [selectedAlgorithmId],
  );
  const activeRun = runs.find(({ status }) => ["queued", "processing"].includes(status));
  const mapLayers = runs.flatMap((run) =>
    (run.result?.layers ?? [])
      .filter(({ id }) => visibleLayerKeys.includes(`${run.run_id}:${id}`))
      .map((layer) => ({ ...layer, key: `${run.run_id}:${layer.id}` })),
  );
  const aoiBounds = runs.find((run) => run.result?.aoi_bounds)?.result?.aoi_bounds;

  useEffect(() => {
    if (!activeRun) return undefined;

    let cancelled = false;
    let timeoutId;

    async function poll() {
      try {
        const updatedRun = await getRun(activeRun.run_id);
        if (cancelled) return;
        setRequestError("");
        setRuns((currentRuns) =>
          currentRuns.map((run) =>
            run.run_id === updatedRun.run_id ? updatedRun : run,
          ),
        );
        if (["queued", "processing"].includes(updatedRun.status)) {
          timeoutId = window.setTimeout(poll, POLL_INTERVAL_MS);
        }
      } catch (error) {
        if (cancelled) return;
        setRequestError(`Could not check the analysis status: ${error.message}`);
        timeoutId = window.setTimeout(poll, POLL_INTERVAL_MS);
      }
    }

    timeoutId = window.setTimeout(poll, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [activeRun?.run_id, activeRun?.status]);

  function selectAlgorithm(algorithm) {
    setSelectedAlgorithmId(algorithm.id);
    setParameters(defaultParameters(algorithm));
  }

  async function handleRun() {
    setRequestError("");
    if (!aoiText.trim() || !dateStart || !dateEnd) {
      setRequestError("Provide an AOI GeoJSON polygon and both Sentinel-1 dates.");
      return;
    }

    let aoiCoordinates;
    try {
      aoiCoordinates = JSON.parse(aoiText);
    } catch {
      setRequestError("AOI must be valid GeoJSON.");
      return;
    }

    setIsSubmitting(true);
    try {
      const run = await createRun({
        algorithm: selectedAlgorithm.id,
        aoi_coordinates: aoiCoordinates,
        date_start: dateStart,
        date_end: dateEnd,
        polarisation,
        parameters,
      });
      setRuns((currentRuns) => [run, ...currentRuns]);
    } catch (error) {
      setRequestError(`Could not start the analysis: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  }

  function toggleLayer(layerKey) {
    setVisibleLayerKeys((currentKeys) =>
      currentKeys.includes(layerKey)
        ? currentKeys.filter((key) => key !== layerKey)
        : [...currentKeys, layerKey],
    );
  }

  return (
    <main className="app-shell">
      <Sidebar
        algorithms={algorithms}
        selectedAlgorithm={selectedAlgorithm}
        parameters={parameters}
        aoiText={aoiText}
        dateStart={dateStart}
        dateEnd={dateEnd}
        polarisation={polarisation}
        onAoiChange={setAoiText}
        onDateStartChange={setDateStart}
        onDateEndChange={setDateEnd}
        onPolarisationChange={setPolarisation}
        onSelectAlgorithm={selectAlgorithm}
        onParameterChange={(key, value) =>
          setParameters((current) => ({ ...current, [key]: value }))
        }
        onRun={handleRun}
        isSubmitting={isSubmitting}
        activeRun={activeRun}
        runs={runs}
        visibleLayerKeys={visibleLayerKeys}
        onToggleLayer={toggleLayer}
        requestError={requestError}
        onDismissError={() => setRequestError("")}
      />
      <section className="map-area" aria-label="Analysis map">
        <div className="map-label">
          <span className="map-label-dot" />
          {mapLayers.length ? `${mapLayers.length} result layer(s)` : "Map"}
        </div>
        <MapView layers={mapLayers} aoiBounds={aoiBounds} />
      </section>
    </main>
  );
}
