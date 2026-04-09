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
    bench_s2a_hash, bench_s2a_linear, bench_s2a_binary,
    bench_s2b_hash, bench_s2b_linear, bench_s2b_binary,
    bench_s3_hash, bench_s3_fuzzy,
)

app = FastAPI(title="DSA Benchmark API")

# Mount static folder
app.mount("/static", StaticFiles(directory="web"), name="static")

@app.get("/")
def read_root():
    return FileResponse("web/index.html")

DATA_DIR = Path("data")
DATASET_FILES = {
    "1": DATA_DIR / "students_1K.xlsx",
    "2": DATA_DIR / "students_5K.xlsx",
    "3": DATA_DIR / "students_10K.xlsx",
}

# State
db = {
    "records": [],
    "ht_chain": None,
    "ht_open": None
}

class LoadDatasetReq(BaseModel):
    size: str

@app.post("/api/dataset")
def api_load_dataset(req: LoadDatasetReq):
    size = req.size
    if size not in DATASET_FILES:
        raise HTTPException(status_code=400, detail="Invalid dataset size")
        
    records = load_xlsx(DATASET_FILES[size])
    ht_chain, ht_open = build_hash_tables(records, load_factor=0.5)
    
    db["records"] = records
    db["ht_chain"] = ht_chain
    db["ht_open"] = ht_open
    
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
        if req.algo == "hash":
            return bench_s2a_hash(db["records"], req.department, req.min_gpa, req.max_gpa)
        elif req.algo == "linear":
            return bench_s2a_linear(db["records"], req.department, req.min_gpa, req.max_gpa)
        elif req.algo == "binary":
            return bench_s2a_binary(db["records"], req.department, req.min_gpa, req.max_gpa)
    elif req.scenario == "2B":
        if req.algo == "hash":
            return bench_s2b_hash(req.min_gpa, req.max_gpa)
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
        
    if req.algo == "hash":
        return bench_s3_hash(db["ht_chain"], req.query)
    elif req.algo == "fuzzy":
        return bench_s3_fuzzy(db["records"], req.query)
    raise HTTPException(status_code=400, detail="Invalid algo")


if __name__ == "__main__":
    print("Starting Web UI on http://localhost:8000")
    uvicorn.run("web:app", host="0.0.0.0", port=8000, reload=True)