import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import AlgorithmId, RunRequest, RunResponse, RunStatus


def database_path() -> Path:
    configured = os.environ.get("SAR_RUNS_DB")
    return Path(configured) if configured else Path("data/runs.sqlite3")


def connect() -> sqlite3.Connection:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            algorithm TEXT NOT NULL,
            status TEXT NOT NULL,
            stage TEXT NOT NULL,
            progress INTEGER NOT NULL,
            request_json TEXT NOT NULL,
            result_json TEXT,
            error TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    return connection


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_run(run_id: str, request: RunRequest) -> RunResponse:
    now = now_iso()
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO runs (
                run_id, algorithm, status, stage, progress, request_json,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                request.algorithm.value,
                RunStatus.QUEUED.value,
                "Queued",
                0,
                json.dumps(request.to_registry_dict(), sort_keys=True),
                now,
                now,
            ),
        )
    return get_run(run_id)


def update_run(
    run_id: str,
    *,
    status: RunStatus | None = None,
    stage: str | None = None,
    progress: int | None = None,
    result: dict[str, Any] | None = None,
    error: str | None = None,
) -> None:
    updates: list[str] = ["updated_at = ?"]
    values: list[Any] = [now_iso()]
    for column, value in (
        ("status", status.value if status else None),
        ("stage", stage),
        ("progress", progress),
        ("result_json", json.dumps(result, sort_keys=True) if result is not None else None),
        ("error", error),
    ):
        if value is not None:
            updates.append(f"{column} = ?")
            values.append(value)
    values.append(run_id)
    with connect() as connection:
        cursor = connection.execute(
            f"UPDATE runs SET {', '.join(updates)} WHERE run_id = ?",
            values,
        )
        if cursor.rowcount != 1:
            raise KeyError(f"Run {run_id} does not exist")


def get_run(run_id: str) -> RunResponse:
    with connect() as connection:
        row = connection.execute(
            "SELECT * FROM runs WHERE run_id = ?",
            (run_id,),
        ).fetchone()
    if row is None:
        raise KeyError(f"Run {run_id} does not exist")
    return RunResponse(
        run_id=row["run_id"],
        algorithm=AlgorithmId(row["algorithm"]),
        status=RunStatus(row["status"]),
        stage=row["stage"],
        progress=row["progress"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        request=json.loads(row["request_json"]),
        result=json.loads(row["result_json"]) if row["result_json"] else None,
        error=row["error"],
    )


def get_request(run_id: str) -> RunRequest:
    with connect() as connection:
        row = connection.execute(
            "SELECT request_json FROM runs WHERE run_id = ?",
            (run_id,),
        ).fetchone()
    if row is None:
        raise KeyError(f"Run {run_id} does not exist")
    return RunRequest.model_validate(json.loads(row["request_json"]))
