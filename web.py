import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from data.loader import load_xlsx, build_hash_tables, sample_id
from engine.benchmark import (
    bench_s1_chain, bench_s1_open, bench_s1_linear, bench_s1_binary,
    bench_s2a_chain, bench_s2a_open, bench_s2a_linear, bench_s2a_binary,
    bench_s2b_hash, bench_s2b_linear, bench_s2b_binary,
    bench_s3_fuzzy, bench_s3_inverted,
)

app = FastAPI(title="DSA Benchmark API")

# Mount static folder
app.mount("/static", StaticFiles(directory="web"), name="static")

@app.get("/")
def read_root():
    response = FileResponse("web/index.html")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response

DATA_DIR = Path("data")
DATASET_FILES = {
    "1": DATA_DIR / "students_1K.xlsx",
    "2": DATA_DIR / "students_5K.xlsx",
    "3": DATA_DIR / "students_10K.xlsx",
}

# State
db = {
    "records":       [],
    "ht_chain":      None,
    "ht_open":       None,
    "ht_chain_dept": None,
    "ht_open_dept":  None,
    "inv_index":     None,  # thêm
}

class LoadDatasetReq(BaseModel):
    size: str

@app.post("/api/dataset")
def api_load_dataset(req: LoadDatasetReq):
    size = req.size
    if size not in DATASET_FILES:
        raise HTTPException(status_code=400, detail="Invalid dataset size")

    records = load_xlsx(DATASET_FILES[size])
    ht_chain, ht_open, ht_chain_dept, ht_open_dept, inv_index = build_hash_tables(records)  # unpack 5

    db["records"]       = records
    db["ht_chain"]      = ht_chain
    db["ht_open"]       = ht_open
    db["ht_chain_dept"] = ht_chain_dept
    db["ht_open_dept"]  = ht_open_dept
    db["inv_index"]     = inv_index  # thêm

    suggested = sample_id(records) if len(records) > 0 else "SV001"
    return {"count": len(records), "suggested_id": suggested}

class Scenario1Req(BaseModel):
    algo: str
    target_id: str

@app.post("/api/scenario1")
def api_scenario1(req: Scenario1Req):
    if not db["records"]:
        raise HTTPException(status_code=400, detail="Load dataset first")

    if req.algo == "chain":
        return bench_s1_chain(db["ht_chain"], req.target_id)
    elif req.algo == "open":
        return bench_s1_open(db["ht_open"], req.target_id)
    elif req.algo == "linear":
        return bench_s1_linear(db["records"], req.target_id)
    elif req.algo == "binary":
        return bench_s1_binary(db["records"], req.target_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid algo")

class Scenario2Req(BaseModel):
    algo: str
    scenario: str
    department: str = "CNTT"
    min_gpa: float
    max_gpa: float

@app.post("/api/scenario2")
def api_scenario2(req: Scenario2Req):
    if not db["records"]:
        raise HTTPException(status_code=400, detail="Load dataset first")

    if req.scenario == "2A":
        if req.algo == "chain":
            return bench_s2a_chain(db["ht_chain_dept"], req.department, req.min_gpa, req.max_gpa)
        elif req.algo == "open":
            return bench_s2a_open(db["ht_open_dept"], req.department, req.min_gpa, req.max_gpa)
        elif req.algo == "linear":
            return bench_s2a_linear(db["records"], req.department, req.min_gpa, req.max_gpa)
        elif req.algo == "binary":
            return bench_s2a_binary(db["records"], req.department, req.min_gpa, req.max_gpa)

    elif req.scenario == "2B":
        if req.algo in ("chain", "open", "hash"):
            return {"algo": "Hash lookup", "ms": None, "sort_ms": None,
                    "match_count": 0, "matches": [], "failed": True}
        elif req.algo == "linear":
            return bench_s2b_linear(db["records"], req.min_gpa, req.max_gpa)
        elif req.algo == "binary":
            return bench_s2b_binary(db["records"], req.min_gpa, req.max_gpa)

    raise HTTPException(status_code=400, detail="Invalid config")

class Scenario3Req(BaseModel):
    algo: str
    query: str

@app.post("/api/scenario3")
def api_scenario3(req: Scenario3Req):
    if not db["records"]:
        raise HTTPException(status_code=400, detail="Load dataset first")

    if req.algo == "fuzzy":
        return bench_s3_fuzzy(db["records"], req.query)
    elif req.algo == "inverted":                                # thêm
        return bench_s3_inverted(db["inv_index"], req.query)   # thêm
    raise HTTPException(status_code=400, detail="Invalid algo")


if __name__ == "__main__":
    print("Starting Web UI on http://localhost:8000")
    uvicorn.run("web:app", host="0.0.0.0", port=8000, reload=True)