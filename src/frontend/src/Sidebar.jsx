function ParameterInput({ algorithm, parameter, value, onChange }) {
  const inputId = `${algorithm.id}-${parameter.key}`;
  const commonProps = {
    id: inputId,
    name: parameter.key,
    value,
    onChange: (event) =>
      onChange(
        parameter.key,
        parameter.type === "number" && event.target.value !== ""
          ? Number(event.target.value)
          : event.target.value,
      ),
  };

  return (
    <label className="field" htmlFor={inputId}>
      <span>{parameter.label}</span>
      {parameter.type === "select" ? (
        <select {...commonProps}>
          {parameter.options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      ) : (
        <input
          {...commonProps}
          type={parameter.type}
          placeholder={parameter.placeholder}
          min={parameter.min}
          max={parameter.max}
          step={parameter.step}
        />
      )}
    </label>
  );
}

function RunStatus({ status, stage, progress }) {
  const label = {
    queued: "Pending",
    processing: "Processing",
    completed: "Completed",
    failed: "Failed",
  }[status] ?? status;

  return (
    <span className={`status status-${status}`}>
      {["queued", "processing"].includes(status) && (
        <span className="status-spinner" aria-hidden="true" />
      )}
      {label}{status === "processing" ? ` · ${progress}%` : ""}
      {stage && ["queued", "processing"].includes(status) ? ` — ${stage}` : ""}
    </span>
  );
}

export default function Sidebar({
  algorithms,
  selectedAlgorithm,
  parameters,
  aoiText,
  dateStart,
  dateEnd,
  polarisation,
  onAoiChange,
  onDateStartChange,
  onDateEndChange,
  onPolarisationChange,
  onSelectAlgorithm,
  onParameterChange,
  onRun,
  isSubmitting,
  activeRun,
  runs,
  visibleLayerKeys,
  onToggleLayer,
  requestError,
  onDismissError,
}) {
  const categories = ["Thresholding", "Analysis"];
  const isRunning = isSubmitting || Boolean(activeRun);

  return (
    <aside className="sidebar">
      <header className="sidebar-header">
        <div className="brand-mark" aria-hidden="true">S</div>
        <div>
          <p className="eyebrow">SAR FLOOD PLATFORM</p>
          <h1>Analysis workspace</h1>
        </div>
        <div className="profile-mark" aria-label="Analyst profile">A</div>
      </header>

      <div className="sidebar-scroll">
        <section className="section-block">
          <div className="section-heading">
            <h2>Algorithm</h2>
            <span className="section-count">06</span>
          </div>
          {categories.map((category) => (
            <div className="algorithm-group" key={category}>
              <p className="group-label">{category}</p>
              {algorithms
                .filter((algorithm) => algorithm.category === category)
                .map((algorithm) => {
                  const selected = algorithm.id === selectedAlgorithm.id;
                  return (
                    <button
                      className={`algorithm-choice${selected ? " is-selected" : ""}`}
                      key={algorithm.id}
                      type="button"
                      aria-pressed={selected}
                      onClick={() => onSelectAlgorithm(algorithm)}
                    >
                      <span className="algorithm-issue">{algorithm.issue}</span>
                      <span className="algorithm-name">{algorithm.name}</span>
                      <span className="choice-indicator" aria-hidden="true" />
                    </button>
                  );
                })}
            </div>
          ))}
        </section>

        <section className="section-block configuration">
          <div className="section-heading">
            <h2>Configure</h2>
            <span className="algorithm-issue">{selectedAlgorithm.issue}</span>
          </div>
          <p className="algorithm-description">{selectedAlgorithm.description}</p>
          <div className="field-list shared-inputs">
            <label className="field" htmlFor="aoi-geojson">
              <span>Area of interest · GeoJSON</span>
              <textarea
                id="aoi-geojson"
                value={aoiText}
                onChange={(event) => onAoiChange(event.target.value)}
                placeholder='{"type":"Polygon","coordinates":[...]}'
                rows={4}
                spellCheck={false}
              />
            </label>
            <label className="field" htmlFor="date-start">
              <span>Sentinel-1 start date</span>
              <input
                id="date-start"
                type="date"
                value={dateStart}
                onChange={(event) => onDateStartChange(event.target.value)}
                required
              />
            </label>
            <label className="field" htmlFor="date-end">
              <span>Sentinel-1 end date</span>
              <input
                id="date-end"
                type="date"
                value={dateEnd}
                onChange={(event) => onDateEndChange(event.target.value)}
                required
              />
            </label>
            {selectedAlgorithm.id !== "DIP-17" && (
              <label className="field" htmlFor="polarisation">
                <span>Polarisation</span>
                <select
                  id="polarisation"
                  value={polarisation}
                  onChange={(event) => onPolarisationChange(event.target.value)}
                >
                  <option value="VV">VV</option>
                  <option value="VH">VH</option>
                </select>
              </label>
            )}
          </div>
          <div className="field-list">
            {selectedAlgorithm.parameters.map((parameter) => (
              <ParameterInput
                key={parameter.key}
                algorithm={selectedAlgorithm}
                parameter={parameter}
                value={parameters[parameter.key]}
                onChange={onParameterChange}
              />
            ))}
          </div>
        </section>

        {runs.length > 0 && (
          <section className="section-block results-section">
            <div className="section-heading">
              <h2>Analysis runs</h2>
              <span className="section-count">{String(runs.length).padStart(2, "0")}</span>
            </div>
            <ul className="run-list">
              {runs.map((run) => {
                const algorithm = algorithms.find(({ id }) => id === run.algorithm);
                return (
                  <li className="run-item" key={run.run_id}>
                    <div className="run-title">
                      <strong>{algorithm?.name ?? run.algorithm}</strong>
                      <small>{run.run_id.slice(0, 8)}</small>
                    </div>
                    <RunStatus
                      status={run.status}
                      stage={run.stage}
                      progress={run.progress}
                    />
                    {run.error && <p className="run-error">{run.error}</p>}
                    {(run.result?.layers ?? []).map((layer) => {
                      const key = `${run.run_id}:${layer.id}`;
                      return (
                        <label className="run-layer" key={key}>
                          <input
                            type="checkbox"
                            checked={visibleLayerKeys.includes(key)}
                            onChange={() => onToggleLayer(key)}
                            aria-label={`Toggle ${layer.name} map layer`}
                          />
                          <span className="run-title">
                            <strong>{layer.name}</strong>
                            <small>{layer.type === "xyz" ? "Raster tiles" : "GeoJSON"}</small>
                          </span>
                        </label>
                      );
                    })}
                    {run.result?.metrics && (
                      <dl className="run-metrics">
                        {Object.entries(run.result.metrics).map(([key, value]) => (
                          <div key={key}>
                            <dt>{key.replaceAll("_", " ")}</dt>
                            <dd>
                              {typeof value === "object"
                                ? JSON.stringify(value)
                                : String(value)}
                            </dd>
                          </div>
                        ))}
                      </dl>
                    )}
                  </li>
                );
              })}
            </ul>
          </section>
        )}
      </div>

      <footer className="sidebar-footer">
        {requestError && (
          <div className="alert" role="alert">
            <span>{requestError}</span>
            <button type="button" aria-label="Dismiss error" onClick={onDismissError}>×</button>
          </div>
        )}
        <button
          className="run-button"
          type="button"
          onClick={onRun}
          disabled={isRunning}
        >
          {isRunning && <span className="button-spinner" aria-hidden="true" />}
          {isRunning ? "Analysis running" : "Run analysis"}
          {!isRunning && <span aria-hidden="true">→</span>}
        </button>
      </footer>
    </aside>
  );
}
