import re
from pathlib import Path

LOG_PATTERN = re.compile(
    r"\[(?P<time>.*?)\]\s+"
    r"(?P<level>\w+)\s+\|\s+"
    r"(?P<logger>.*?)\s+\|\s+"
    r"(?P<method>.*?)\s+\|\s+"
    r"(?P<status>.*?)\s+\|\s+"
    r"(?P<client_ip>.*?)\s+\|\s+"
    # r"(?P<country>.*?)\s+\|\s+"
    r"(?P<message>.*)"
)


def read_logs(
    file_path: str,
    limit: int = 100,
    level: str | None = None,
):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError("Log file not found")

    logs = []

    with path.open("r", encoding="utf-8") as f:
        for line in f.readlines()[-limit:]:
            match = LOG_PATTERN.match(line.strip())
            if not match:
                continue

            log = match.groupdict()

            if level and log["level"] != level.upper():
                continue

            logs.append(log)

    return logs
