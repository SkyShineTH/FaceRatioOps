from bisect import bisect_left
from collections import Counter
from dataclasses import dataclass, field
from threading import Lock

MetricKey = tuple[str, str, int]

# Latency histogram bucket upper bounds in seconds. Spread covers fast static/health
# responses through the heavier MediaPipe `/analyze` path on a small Droplet.
DEFAULT_BUCKETS_SECONDS: tuple[float, ...] = (
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
)


@dataclass
class MetricsRegistry:
    buckets: tuple[float, ...] = DEFAULT_BUCKETS_SECONDS
    request_counts: Counter[MetricKey] = field(default_factory=Counter)
    duration_sum_seconds: Counter[MetricKey] = field(default_factory=Counter)
    # Per-key, non-cumulative bucket tallies; index len(buckets) is the +Inf overflow.
    _bucket_counts: dict[MetricKey, list[int]] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)

    def record_request(self, method: str, path: str, status_code: int, duration_seconds: float) -> None:
        key = (method.upper(), path, status_code)
        duration = max(duration_seconds, 0.0)
        # Smallest bucket whose upper bound is >= duration (Prometheus `le` semantics).
        index = bisect_left(self.buckets, duration)
        with self._lock:
            self.request_counts[key] += 1
            self.duration_sum_seconds[key] += duration
            tallies = self._bucket_counts.get(key)
            if tallies is None:
                tallies = [0] * (len(self.buckets) + 1)
                self._bucket_counts[key] = tallies
            tallies[index] += 1

    def render_prometheus(self) -> str:
        with self._lock:
            counts = dict(self.request_counts)
            sums = dict(self.duration_sum_seconds)
            bucket_counts = {key: list(tallies) for key, tallies in self._bucket_counts.items()}

        lines = [
            "# HELP faceratioops_http_requests_total Total HTTP requests handled.",
            "# TYPE faceratioops_http_requests_total counter",
        ]
        for key, count in sorted(counts.items()):
            lines.append(f"faceratioops_http_requests_total{_labels(key)} {count}")

        lines.extend(
            [
                "# HELP faceratioops_http_request_duration_seconds Request duration in seconds.",
                "# TYPE faceratioops_http_request_duration_seconds histogram",
            ]
        )
        for key in sorted(bucket_counts):
            tallies = bucket_counts[key]
            cumulative = 0
            for boundary, bucket_total in zip(self.buckets, tallies, strict=False):
                cumulative += bucket_total
                lines.append(
                    f"faceratioops_http_request_duration_seconds_bucket"
                    f"{_labels(key, le=format(boundary, 'g'))} {cumulative}"
                )
            cumulative += tallies[-1]
            lines.append(
                f"faceratioops_http_request_duration_seconds_bucket{_labels(key, le='+Inf')} {cumulative}"
            )
            lines.append(f"faceratioops_http_request_duration_seconds_count{_labels(key)} {cumulative}")
            lines.append(
                f"faceratioops_http_request_duration_seconds_sum{_labels(key)} {sums.get(key, 0.0):.6f}"
            )

        return "\n".join(lines) + "\n"


def _labels(key: MetricKey, le: str | None = None) -> str:
    method, path, status_code = key
    parts = [
        f'method="{_escape(method)}"',
        f'path="{_escape(path)}"',
        f'status="{status_code}"',
    ]
    if le is not None:
        parts.append(f'le="{_escape(le)}"')
    return "{" + ",".join(parts) + "}"


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')
