from collections import Counter
from dataclasses import dataclass, field
from threading import Lock

MetricKey = tuple[str, str, int]


@dataclass
class MetricsRegistry:
    request_counts: Counter[MetricKey] = field(default_factory=Counter)
    request_duration_seconds: Counter[MetricKey] = field(default_factory=Counter)
    _lock: Lock = field(default_factory=Lock)

    def record_request(self, method: str, path: str, status_code: int, duration_seconds: float) -> None:
        key = (method.upper(), path, status_code)
        with self._lock:
            self.request_counts[key] += 1
            self.request_duration_seconds[key] += max(duration_seconds, 0.0)

    def render_prometheus(self) -> str:
        with self._lock:
            counts = dict(self.request_counts)
            durations = dict(self.request_duration_seconds)

        lines = [
            "# HELP faceratioops_http_requests_total Total HTTP requests handled.",
            "# TYPE faceratioops_http_requests_total counter",
        ]
        for key, count in sorted(counts.items()):
            lines.append(f"faceratioops_http_requests_total{_labels(key)} {count}")

        lines.extend(
            [
                "# HELP faceratioops_http_request_duration_seconds_sum Total request duration in seconds.",
                "# TYPE faceratioops_http_request_duration_seconds_sum counter",
            ]
        )
        for key, duration in sorted(durations.items()):
            lines.append(f"faceratioops_http_request_duration_seconds_sum{_labels(key)} {duration:.6f}")

        return "\n".join(lines) + "\n"


def _labels(key: MetricKey) -> str:
    method, path, status_code = key
    return f'{{method="{_escape(method)}",path="{_escape(path)}",status="{status_code}"}}'


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')
