import json
import sys
import subprocess
from pathlib import Path

def run_test():
    print("========================================")
    print(" Running End-to-End Test for Recommendation Pipeline")
    print(" Input: Bellandur, Budget: 2000, Rating: 4.0, Top 5 from LLM")
    print("========================================\n")
    
    # Files
    phase2_out = Path("data/processed/phase2_preference_test.json")
    phase3_out = Path("data/processed/phase3_candidates_test.json")
    phase4_out = Path("data/processed/phase4_recommendations_test.json")
    phase5_out = Path("data/processed/final_response_test.json")
    restaurants_csv = Path("data/processed/restaurants_clean.csv")
    
    # 1. Phase 2
    print("--> Running Phase 2 (Preference Capture)")
    cmd2 = [
        sys.executable, "-m", "src.phase2.pipeline",
        "--location", "Bellandur",
        "--budget", "2000",
        "--cuisine", "Any",
        "--min-rating", "4.0",
        "--output-json", str(phase2_out)
    ]
    subprocess.run(cmd2, check=True)
    print("    [Phase 2 Complete] Generated:", phase2_out)
    
    # 2. Phase 3
    print("\n--> Running Phase 3 (Candidate Retrieval)")
    cmd3 = [
        sys.executable, "-m", "src.phase3.pipeline",
        "--restaurants-csv", str(restaurants_csv),
        "--preferences-json", str(phase2_out),
        "--output-json", str(phase3_out)
    ]
    subprocess.run(cmd3, check=True)
    with open(phase3_out, "r") as f:
        data3 = json.load(f)
    print(f"    [Phase 3 Complete] Retrieved {len(data3.get('candidates', []))} candidates. Generated:", phase3_out)
    
    # 3. Phase 4
    print("\n--> Running Phase 4 (LLM Recommendation)")
    cmd4 = [
        sys.executable, "-m", "src.phase4.pipeline",
        "--phase3-json", str(phase3_out),
        "--output-json", str(phase4_out),
        "--top-n", "5"
    ]
    subprocess.run(cmd4, check=True)
    with open(phase4_out, "r") as f:
        data4 = json.load(f)
    print(f"    [Phase 4 Complete] Recommendations returned: {len(data4.get('recommendations', []))} (Mode: {data4.get('llm_mode')})")
    
    # 4. Phase 5
    print("\n--> Running Phase 5 (Final Formatting)")
    cmd5 = [
        sys.executable, "-m", "src.phase5.pipeline",
        "--phase4-json", str(phase4_out),
        "--output-json", str(phase5_out),
        "--top-n", "5"
    ]
    subprocess.run(cmd5, check=True, stdout=subprocess.DEVNULL)
    
    with open(phase5_out, "r") as f:
        final_data = json.load(f)
        
    print("\n========================================")
    print(" FINAL RECOMMENDATIONS OUTPUT")
    print("========================================")
    print(json.dumps(final_data, indent=2))
    print("========================================\n")


if __name__ == "__main__":
    try:
        run_test()
    except subprocess.CalledProcessError as e:
        print(f"Error during pipeline execution: {e}")
