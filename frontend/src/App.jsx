import { useState, useEffect } from "react";
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


  const [metrics, setMetrics] = useState(null);
  const [apiError, setApiError] = useState("");

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch(
          "/api/metrics"
        );

        if (!response.ok) {
          throw new Error("Could not fetch metrics");
        }

        const data = await response.json();
        setMetrics(data);
        console.log("IceStream API data:", data);
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
            <h2>Ready to Connect</h2>
            <span className="metric-note">
              Backend integration pending
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