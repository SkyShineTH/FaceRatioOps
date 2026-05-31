// The exact safety-boundary copy from the original workbench. Keep wording verbatim:
// it is the project's stated brand boundary and is covered by tests.
export default function SafetyBand() {
  return (
    <section className="safety-band" aria-label="Safety boundaries">
      <p>
        This workbench does not perform identity matching, attractiveness scoring, demographic
        prediction, health inference, medical advice, or cosmetic recommendations.
      </p>
      <p>
        Image data is selected locally, submitted to the API for analysis, and is not permanently
        stored by FaceRatioOps.
      </p>
    </section>
  );
}
