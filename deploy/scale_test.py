"""Step-by-step checks for the scaling stack (docker-compose.scale.yml).

Run from the project root after `docker compose -f docker-compose.scale.yml up -d --build`:
    python deploy/scale_test.py
Stdlib only. DB checks run psql inside the containers and roll back their test data.
"""

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from collections import Counter

BASE = "http://localhost:8080"
COMPOSE = ["docker", "compose", "-f", "docker-compose.scale.yml"]
ADMIN = {"email": "admin123@gmail.com", "password": "12345678"}
failures: list[str] = []


def check(ok: bool, message: str) -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {message}")
    if not ok:
        failures.append(message)


def http(method: str, path: str, token: str | None = None, body: dict | None = None):
    """Return (status, headers, json body) without raising on 4xx/5xx."""
    request = urllib.request.Request(
        BASE + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json"},
    )
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, response.headers, json.loads(response.read() or "null")
    except urllib.error.HTTPError as error:
        return error.code, error.headers, json.loads(error.read() or "null")


def psql(service: str, sql: str) -> tuple[int, str]:
    result = subprocess.run(
        [*COMPOSE, "exec", "-T", service, "psql", "-U", "postgres", "-d", "hospital_db",
         "-At", "-v", "ON_ERROR_STOP=1"],
        input=sql, capture_output=True, text=True,
    )
    return result.returncode, result.stdout + result.stderr


def step_load_balancer(token: str) -> None:
    print("\nStep 1: Load balancer (nginx round-robin over api1 + api2)")
    upstreams = Counter(http("GET", "/health")[1]["X-Upstream"] for _ in range(20))
    print(f"  distribution: {dict(upstreams)}")
    check(len(upstreams) == 2, "20 requests spread over 2 API instances")

    subprocess.run([*COMPOSE, "stop", "api1"], capture_output=True, check=True)
    try:
        statuses = [http("GET", "/health")[0] for _ in range(10)]
        check(all(s == 200 for s in statuses), f"failover with api1 down: {statuses}")
    finally:
        subprocess.run([*COMPOSE, "start", "api1"], capture_output=True, check=True)
    for _ in range(30):  # wait until both instances answer again
        if len({http("GET", "/health")[1]["X-Upstream"] for _ in range(4)}) == 2:
            break
        time.sleep(1)


def create_doctor(token: str) -> int:
    tag = uuid.uuid4().hex[:8]
    email = f"scale.{tag}@hospital.com"
    status, _, _ = http("POST", "/api/v1/doctors/", token, {
        "full_name": f"Dr. Scale {tag}", "specialization": "Cardiology", "email": email,
        "phone": "03" + str(uuid.uuid4().int)[:9], "salary": "100000.00",
    })
    check(status == 201, "create doctor on primary")
    for _ in range(20):  # list is served by the replica; allow for replication lag
        items = http("GET", f"/api/v1/doctors/?search={email}", token)[2]["items"]
        if items:
            check(True, "new doctor visible through replica-backed list endpoint")
            return int(items[0]["id"])
        time.sleep(0.1)
    check(False, "new doctor visible through replica-backed list endpoint")
    sys.exit(1)


def step_caching(token: str, doctor_id: int) -> None:
    print("\nStep 2: Caching (Redis, shared by both API instances)")
    path = f"/api/v1/doctors/{doctor_id}"
    first = http("GET", path, token)[1]
    second = http("GET", path, token)[1]
    print(f"  1st: {first['X-Cache']} via {first['X-Upstream']}, "
          f"2nd: {second['X-Cache']} via {second['X-Upstream']}")
    check(first["X-Cache"] == "MISS" and second["X-Cache"] == "HIT", "MISS then HIT")
    check(first["X-Upstream"] != second["X-Upstream"], "HIT served by the other instance")

    http("PUT", path, token, {"full_name": "Dr. Updated Name"})
    status, headers, body = http("GET", path, token)
    check(headers["X-Cache"] == "MISS" and body["full_name"] == "Dr. Updated Name",
          "update invalidates cache (fresh data, MISS)")


def step_queue(token: str) -> None:
    print("\nStep 3: Queue + async job (Redis queue -> RQ worker)")
    started = time.perf_counter()
    status, _, body = http("POST", "/api/v1/jobs/patient-report", token)
    elapsed_ms = (time.perf_counter() - started) * 1000
    check(status == 202, f"job queued, API answered in {elapsed_ms:.0f} ms")
    job = {}
    for _ in range(50):
        job = http("GET", f"/api/v1/jobs/{body['job_id']}", token)[2]
        if job["status"] in ("finished", "failed"):
            break
        time.sleep(0.2)
    print(f"  job: {job}")
    check(job.get("status") == "finished", "worker finished the job and stored the result")
    check(http("GET", "/api/v1/jobs/does-not-exist", token)[0] == 404, "unknown job -> 404")


def step_db_scaling() -> None:
    print("\nStep 4: DB scaling (primary + streaming read replica)")
    _, out = psql("db-primary", "SELECT state FROM pg_stat_replication;")
    check(out.strip() == "streaming", f"primary streams WAL to replica: {out.strip()!r}")
    _, out = psql("db-replica", "SELECT pg_is_in_recovery();")
    check(out.strip() == "t", "replica is in recovery (hot standby)")
    code, out = psql("db-replica", "CREATE TABLE should_fail (id int);")
    check(code != 0 and "read-only" in out, "replica rejects writes")


INDEX_SQL = """
BEGIN;
INSERT INTO doctors (full_name, specialization, email, phone, salary)
SELECT 'Dr. Bulk ' || g, 'Spec ' || (g % 50), 'bulk' || g || '@idx.test', 'B' || g, 1000
FROM generate_series(1, 100000) g;
ANALYZE doctors;
EXPLAIN ANALYZE SELECT * FROM doctors WHERE email = 'bulk77777@idx.test';
SELECT '---';
DROP INDEX ix_doctors_email;
EXPLAIN ANALYZE SELECT * FROM doctors WHERE email = 'bulk77777@idx.test';
SELECT '---';
EXPLAIN SELECT * FROM doctors WHERE full_name ILIKE '%bulk 7%';
ROLLBACK;
"""


def plan_summary(plan: str) -> str:
    lines = plan.strip().splitlines()
    timing = next((l for l in lines if l.startswith("Execution Time")), "")
    node = next((l for l in lines if "Scan" in l), lines[0])
    return f"{node.split('(')[0].strip()} | {timing}"


def step_indexing() -> None:
    print("\nStep 5: Indexing (100k doctors, rolled back afterwards)")
    code, out = psql("db-primary", INDEX_SQL)
    if code != 0:
        check(False, f"index test SQL failed: {out}")
        return
    with_index, without_index, search = out.split("---")[:3]
    print(f"  with index:    {plan_summary(with_index)}")
    print(f"  without index: {plan_summary(without_index)}")
    print(f"  ILIKE search:  {plan_summary(search)}")
    check("Index Scan" in with_index, "email lookup uses ix_doctors_email")
    check("Seq Scan" in without_index, "dropping the index forces a full table scan")
    if "Seq Scan" in search:
        print("  note: ILIKE '%...%' search can't use B-tree indexes (needs pg_trgm GIN)")


SHARD_SQL = """
BEGIN;
CREATE TABLE appointments_demo (id bigserial, patient_id int NOT NULL, note text)
PARTITION BY HASH (patient_id);
CREATE TABLE appointments_demo_p0 PARTITION OF appointments_demo FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE appointments_demo_p1 PARTITION OF appointments_demo FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE appointments_demo_p2 PARTITION OF appointments_demo FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE appointments_demo_p3 PARTITION OF appointments_demo FOR VALUES WITH (MODULUS 4, REMAINDER 3);
INSERT INTO appointments_demo (patient_id, note) SELECT g % 10000, 'visit' FROM generate_series(1, 100000) g;
SELECT tableoid::regclass || '=' || count(*) FROM appointments_demo GROUP BY tableoid ORDER BY 1;
SELECT '---';
EXPLAIN SELECT * FROM appointments_demo WHERE patient_id = 42;
ROLLBACK;
"""


def step_sharding() -> None:
    print("\nStep 6: Sharding (hash partitioning by patient_id, rolled back afterwards)")
    code, out = psql("db-primary", SHARD_SQL)
    if code != 0:
        check(False, f"sharding test SQL failed: {out}")
        return
    counts, plan = out.split("---")[:2]
    counts = [l for l in counts.splitlines() if "=" in l]
    print(f"  rows per shard: {counts}")
    sizes = [int(c.split("=")[1]) for c in counts]
    check(len(sizes) == 4 and min(sizes) > 20000, "100k rows spread evenly over 4 shards")
    scanned = [p for p in ("_p0", "_p1", "_p2", "_p3") if p in plan]
    check(len(scanned) == 1, f"query for one patient hits only shard {scanned}")


def main() -> None:
    status, _, body = http("POST", "/api/v1/auth/login", body=ADMIN)
    if status != 200:
        sys.exit(f"login failed ({status}): {body}. Is the stack running?")
    token = body["access_token"]

    step_load_balancer(token)
    doctor_id = create_doctor(token)
    step_caching(token, doctor_id)
    step_queue(token)
    step_db_scaling()
    step_indexing()
    step_sharding()

    http("DELETE", f"/api/v1/doctors/{doctor_id}", token)
    print(f"\n{'ALL PASSED' if not failures else f'{len(failures)} FAILED: {failures}'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
