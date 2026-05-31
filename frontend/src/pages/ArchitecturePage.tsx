import SiteNav from "../components/SiteNav";
import ArchitectureDiagram from "../components/ArchitectureDiagram";
import SafetyBand from "../components/SafetyBand";

export default function ArchitecturePage() {
  return (
    <main className="shell">
      <SiteNav />
      <section className="intro" aria-labelledby="arch-title">
        <div>
          <p className="eyebrow">Production deployment topology</p>
          <h1 id="arch-title">Architecture</h1>
          <p className="lede">
            How a request flows from the public edge to inference, and how the monitoring pipeline
            observes the service. Hover or focus a node to explore it.
          </p>
        </div>
        <div className="ops-strip" aria-label="Operational endpoints">
          <a href="/health">/health</a>
          <a href="/metrics">/metrics</a>
          <a href="/docs">/docs</a>
        </div>
      </section>

      <ArchitectureDiagram />

      <SafetyBand />
    </main>
  );
}
