"""Script to execute and smoke-test all 6 Jupyter notebooks end-to-end."""

import os
import sys
from pathlib import Path
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

NOTEBOOKS = [
    "00_setup_and_imports.ipynb",
    "01_ingest_rss_and_youtube.ipynb",
    "02_feature_engineering_and_hype_scores.ipynb",
    "03_echo_chamber_graph.ipynb",
    "04_interactive_dashboard.ipynb",
    "view_html_reports.ipynb",
]

def run_smoke_tests():
    print("=" * 65)
    print("  RUNNING NOTEBOOK SMOKE TESTS & END-TO-END EXECUTION")
    print("=" * 65)
    
    ep = ExecutePreprocessor(timeout=180, kernel_name="python3")
    results = {}
    
    for nb_name in NOTEBOOKS:
        nb_path = NOTEBOOKS_DIR / nb_name
        print(f"\n[EXEC] Running {nb_name} ...", flush=True)
        
        with open(nb_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
            
        try:
            # Execute notebook with working directory set to notebooks/
            ep.preprocess(nb, {"metadata": {"path": str(NOTEBOOKS_DIR)}})
            
            # Save executed notebook with rendered outputs
            with open(nb_path, "w", encoding="utf-8") as f:
                nbformat.write(nb, f)
                
            print(f"[PASS] {nb_name} completed with 0 errors! Outputs saved.")
            results[nb_name] = "PASS"
        except Exception as e:
            err_msg = str(e).encode('ascii', errors='replace').decode('ascii')
            print(f"[FAIL] {nb_name} failed with error: {err_msg}")
            results[nb_name] = f"FAIL"
            
    print("\n" + "=" * 65)
    print("  SMOKE TEST SUMMARY")
    print("=" * 65)
    all_passed = True
    for nb_name, status in results.items():
        print(f"  {nb_name:42s} : {status}")
        if not status.startswith("PASS"):
            all_passed = False
            
    print("=" * 65)
    if all_passed:
        print("[SUCCESS] All notebooks executed cleanly with 0 errors!\n")
        return 0
    else:
        print("[ERROR] Some notebooks failed execution. Please review errors above.\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_smoke_tests())
