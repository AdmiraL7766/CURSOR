@echo off
setlocal

REM Run from project root
cd /d "%~dp0"

echo ==========================================
echo AI Restaurant Recommender - Setup and Run
echo ==========================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Python not found in PATH.
  echo Install Python 3.10+ and enable "Add Python to PATH".
  echo Then re-run this script.
  exit /b 1
)

echo [1/5] Installing dependencies...
python -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Dependency installation failed.
  exit /b 1
)

echo.
echo [2/5] Running Phase 1 (data download + processing)...
python -m src.data.pipeline --project-root "."
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Phase 1 pipeline failed.
  exit /b 1
)

echo.
echo [3/5] Running Phase 2 (preference capture)...
python -m src.phase2.pipeline ^
  --location "Bellandur" ^
  --budget "1500" ^
  --cuisine "North Indian" ^
  --min-rating "3.5" ^
  --output-json "data\processed\phase2_preference.json"
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Phase 2 pipeline failed.
  exit /b 1
)

echo.
echo [4/5] Running Phase 3 (candidate retrieval)...
python -m src.phase3.pipeline ^
  --restaurants-csv "data\processed\restaurants_clean.csv" ^
  --preferences-json "data\processed\phase2_preference.json" ^
  --output-json "data\processed\phase3_candidates.json"
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Phase 3 pipeline failed.
  exit /b 1
)

echo.
echo [5/5] Running Phase 4+5 (LLM recommendation + formatting)...
python -m src.phase4.pipeline ^
  --phase3-json "data\processed\phase3_candidates.json" ^
  --output-json "data\processed\phase4_recommendations.json" ^
  --top-n 5
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Phase 4 pipeline failed.
  exit /b 1
)

python -m src.phase5.pipeline ^
  --phase4-json "data\processed\phase4_recommendations.json" ^
  --output-json "data\processed\final_response.json" ^
  --top-n 5
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Phase 5 pipeline failed.
  exit /b 1
)

echo.
echo ==========================================
echo Completed successfully!
echo Outputs:
echo - data\processed\restaurants_clean.csv
echo - data\processed\restaurants.db
echo - data\reports\phase1_data_quality.md
echo - data\processed\phase2_preference.json
echo - data\processed\phase3_candidates.json
echo - data\processed\phase4_recommendations.json
echo - data\processed\final_response.json
echo ==========================================
echo.
echo To start the API server:
echo   python -m uvicorn src.phase6.main:app --host 0.0.0.0 --port 8000

exit /b 0
