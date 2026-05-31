import SiteNav from "../components/SiteNav";
import Workbench from "../components/Workbench";
import SafetyBand from "../components/SafetyBand";

export default function WorkbenchPage() {
  return (
    <main className="shell">
      <SiteNav />
      <section className="intro" aria-labelledby="page-title">
        <div>
          <p className="eyebrow">Privacy-first inference workbench</p>
          <h1 id="page-title">FaceRatioOps</h1>
          <p className="lede">
            Upload one local face image to inspect landmark detection, technical geometric ratios,
            and quality warnings from the API.
          </p>
        </div>
        <div className="ops-strip" aria-label="Operational endpoints">
          <a href="/health">/health</a>
          <a href="/model-info">/model-info</a>
          <a href="/metrics">/metrics</a>
          <a href="/docs">/docs</a>
        </div>
      </section>

      <Workbench />

      <SafetyBand />
    </main>
  );
}
