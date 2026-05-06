from app.inference.schemas import QualityReport


def build_quality_report(warnings: list[str], confidence: float | None) -> QualityReport:
    return QualityReport(warnings=warnings, confidence=confidence)
