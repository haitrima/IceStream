import { useState, useEffect } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, ReferenceLine, Legend
} from "recharts";
import "./App.css";

function App() {
  const [activePage, setActivePage] = useState("Overview");

  const pages = [
    "Overview",
    "Pipeline",
    "Data Quality",
    "Quarantine",
    "Incident Logs",
  ];


  const [metrics, setMetrics] = useState({
  total_transactions: 100,
  valid_transactions: 91,
  quality_errors: 9,
  error_rate_percent: 9,
  quarantined_records: 9,
  circuit_breaker_triggered: true,
  pipeline_status: "PAUSED",
  downstream_processed: false,
  pipeline_reason: "Data-quality error rate 9.00% reached the 2.00% threshold.",
  threshold_percent: 2,
});
  const [errorRateHistory, setErrorRateHistory] = useState([
  { time: "10:00", errorRate: 1 },
  { time: "10:01", errorRate: 3 },
  { time: "10:02", errorRate: 5 },
  { time: "10:03", errorRate: 9 },
  { time: "10:04", errorRate: 4 },
]);
  const [apiError, setApiError] = useState("");
  const transactionChartData = [
  {
    name: "Transactions",
    Valid: metrics?.valid_transactions ?? 91,
    "Quality Errors": metrics?.quality_errors ?? 9,
  },
];

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch(
  "/api/metrics");

        if (!response.ok) {
          throw new Error("Could not fetch metrics");
        }

        const data = await response.json();
        setMetrics(data);
        setErrorRateHistory((previous) => [
  ...previous,
  {
    time: new Date().toLocaleTimeString(),
    errorRate: data.error_rate_percent,
  },
].slice(-20));
        console.log("IceStream API data:", data);
        console.log("Chart history:", errorRateHistory);
        setApiError("");
      } catch (error) {
        setApiError("Unable to connect to the IceStream API.");
        console.error("Metrics fetch failed:", error);
      }
    };

    fetchMetrics();
    const intervalId = setInterval(fetchMetrics, 5000);

    return () => clearInterval(intervalId);
  }, []);

  
  return (
    <div className="app">
      <aside className="sidebar">
        <h2>❄ IceStream</h2>
        <p className="subtitle">LAKEHOUSE OBSERVABILITY</p>

        <nav>
          {pages.map((page) => (
            <button
              key={page}
              className={
                activePage === page ? "nav-item active" : "nav-item"
              }
              onClick={() => setActivePage(page)}
            >
              {page}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <span className="status-dot" />
          Monitoring workspace
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">DATA ARCHITECTURE & RELIABILITY</p>
            <h1>{activePage}</h1>
            <p className="muted">
              Real-time checkout data quality and pipeline monitoring
            </p>
          </div>
          <div className="system-status">
            <span className="status-dot" /> UI Online
          </div>
        </header>

        <section className="metrics-grid">
        <article className="metric-card">
  <p>Pipeline Status</p>
  <h2>
    {metrics ? metrics.pipeline_status : "Connecting..."}
  </h2>
  <span className="metric-note">
    {metrics
      ? metrics.pipeline_reason
      : "Waiting for backend response"}
  </span>
</article>

          <article className="metric-card">
  <p>Transactions</p>
  <h2>{metrics ? metrics.total_transactions : 0}</h2>
  <span className="metric-note">
    {metrics ? "API data connected" : "Waiting for API"}
  </span>
</article>

          <article className="metric-card">
            <p>Data Quality Errors</p>
            <h2>{metrics ? metrics.quality_errors : 0}</h2>
            <span className="metric-note">
              Awaiting quality checks
            </span>
          </article>

          <article className="metric-card">
            <p>Quarantined Records</p>
            <h2>{metrics ? metrics.quarantined_records : 0}</h2>
            <span className="metric-note">
              No records processed yet
            </span>
          </article>
          <article className="metric-card">
  <p>Error Rate</p>
  <h2>
    {metrics ? `${metrics.error_rate_percent}%` : "—"}
  </h2>
  <span className="metric-note">
    Threshold: {metrics ? metrics.threshold_percent : 2}%
  </span>
</article>
<article className="metric-card">
  <p>Circuit Breaker</p>
  <h2>
    {metrics?.circuit_breaker_triggered
      ? "TRIGGERED"
      : "NORMAL"}
  </h2>
  <span className="metric-note">
    {metrics?.circuit_breaker_triggered
      ? "Pipeline protection activated"
      : "No threshold breach detected"}
  </span>
</article>
        </section>
        <section className="charts-grid">
  <article className="panel chart-panel">
    <div className="panel-heading">
      <div>
        <h2>Transaction Quality</h2>
        <p className="muted">
          Valid transactions vs. quality errors
        </p>
      </div>
    </div>

    <div className="chart-container">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={transactionChartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="Valid" fill="#16a34a" />
          <Bar dataKey="Quality Errors" fill="#dc2626" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  </article>
</section>
<section className="charts-grid">
  <article className="panel chart-panel">
    <div className="panel-heading">
      <div>
        <h2>Error Rate Over Time</h2>
        <p className="muted">
          Error rate compared with the 2% safety threshold
        </p>
      </div>
    </div>

    <div className="chart-container">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={errorRateHistory}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis unit="%" />
          <Tooltip />
          <Legend />
          <ReferenceLine
            y={2}
            stroke="#dc2626"
            strokeDasharray="5 5"
            label="2% Threshold"
          />
          <Line
            type="monotone"
            dataKey="errorRate"
            name="Error Rate"
            stroke="#2563eb"
            strokeWidth={3}
            dot={true}
          />
        </LineChart>
      </ResponsiveContainer>
         {errorRateHistory.length === 0 && (
        <p className="metric-note">
          No successful API readings yet. Waiting for backend data.
        </p>
      )}
    </div>
  </article>
</section>

        <section className="content-grid">
          <article className="panel pipeline-panel">
            <div className="panel-heading">
              <div>
                <h2>Data Pipeline Architecture</h2>
                <p className="muted">
                  Target event-processing workflow
                </p>
              </div>
              <span className="tag">Architecture</span>
            </div>

            <div className="pipeline">
              {[
                ["01", "Checkout", "Transaction events"],
                ["02", "Kafka", "Event stream"],
                ["03", "Flink", "Quality checks"],
                ["04", "Iceberg", "Lakehouse tables"],
              ].map(([number, title, description], index) => (
                <div className="pipeline-group" key={number}>
                  <div className="pipeline-node">
                    <span>{number}</span>
                    <strong>{title}</strong>
                    <small>{description}</small>
                  </div>
                  {index < 3 && (
                    <span className="pipeline-arrow">→</span>
                  )}
                </div>
              ))}
            </div>

            <p className="architecture-note">
              Planned workflow — these services are not connected yet.
            </p>
          </article>

          <article className="panel">
            <div className="panel-heading">
              <div>
                <h2>Quality Rules</h2>
                <p className="muted">Planned monitoring checks</p>
              </div>
            </div>

            <div className="rule-row">
              <div>
                <strong>Null tax amount</strong>
                <p>Detect missing values</p>
              </div>
              <span className="tag warning">5% test injection</span>
            </div>

            <div className="rule-row">
              <div>
                <strong>Schema validation</strong>
                <p>Detect unexpected fields</p>
              </div>
              <span className="tag">Generator rule</span>
            </div>

            <div className="rule-row">
              <div>
                <strong>Circuit breaker</strong>
                <p>Target error threshold: 2%</p>
              </div>
              <span className="tag">Planned</span>
            </div>
          </article>
        </section>

        <section className="panel table-panel">
          <div className="panel-heading">
            <div>
              <h2>{activePage} Activity</h2>
              <p className="muted">
                Records will appear after backend integration
              </p>
            </div>
          </div>

          <div className="empty-state">
            <span className="empty-icon">◈</span>
            <h3>Waiting for data</h3>
            <p>
              The dashboard interface is ready. Next, we will connect
              the Python transaction generator and data-quality checks.
            </p>
          </div>
        </section>

        <footer>IceStream · Real-Time Lakehouse Observability</footer>
      </main>
    </div>
  );
}

export default App;