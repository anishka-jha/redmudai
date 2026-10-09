# RedMudAI — Water Recovery Lab

Presentation MVP: Streamlit interface with a transparent, illustrative filtration surrogate and mass balance. **Unvalidated, no trained AI, no industrial performance claims.** No API keys, database, or user data collection are needed.

## Run in VS Code on Windows

Open this folder in VS Code. In its terminal, use your installed Python:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open http://localhost:8501. Keep the terminal running. If `py` is unavailable, replace it with the full path to your installed Python executable. A Windows Store `python` alias may fail even if another Python installation exists.

## Two-minute presentation demo

1. Start at 30% solids, 1,000 kg slurry, 3 bar, 30 minutes, Balanced.
2. Say: “This prototype compares illustrative filtration scenarios. It has no measured red-mud dataset or trained AI model.”
3. Explain the four outputs: percent of initial water recovered, kilograms recovered, water percentage in the wet cake, and illustrative electricity.
4. Increase filtration time to 60 minutes. Show increased recovery and diminishing returns on the graph. Explain why energy also increases.
5. Switch between Max recovery, Min energy, and Balanced. The current batch settings stay as entered; the recommended grid point changes separately.
6. Open Mass balance: feed equals recovered water plus wet cake, with all dry solids conserved.
7. Open Model & assumptions and show the equations. Say: “Next we need experiments to calibrate filtration behavior and measured electricity to validate the tradeoffs.”
8. Download the JSON results if asked. Do not present these figures as laboratory results or reuse-quality certification.

## Model assumptions

Inputs are mass-based solids %, batch kg, pressure bar, and time minutes. Dry solids are retained. Water density is 1,000 kg/m³. Retained water approaches 0.35 kg/kg dry solids. This floor, the 18-minute coefficient, concentration exponent 1.5, loading exponent 0.5, and square-root pressure response are invented demonstration parameters.

Recovery is `removable_water * (1 - exp(-time * sqrt(pressure) / tau))`, where `tau = 18 * (solids_pct/30)^1.5 * (batch_kg/1000)^0.5`. This is a bounded surrogate, not a mechanistic cake-filtration model. Fixed filter area/loading scaling is assumed. No filtrate solids, evaporation, chemistry, temperature, permeability, cake compression, or reuse suitability is modeled.

Energy is pressure-volume work divided by an assumed 60% efficiency plus 0.25 kW auxiliary power multiplied by runtime. It excludes many real equipment energy terms and is not calibrated. The app shows exact formulas.

## Goal definitions

The search evaluates 480 candidates: 0.5–10 bar in 0.5-bar increments and 5–120 min in 5-min increments.

- **Max recovery:** highest recovery in that grid.
- **Min energy:** lowest energy among points achieving at least 80% of the grid's maximum recovery. This constraint avoids a trivial negligible-filtration solution.
- **Balanced:** maximize `0.65 * recovery / maximum_recovery - 0.35 * (energy - minimum_energy)/(maximum_energy - minimum_energy)`. These weights are illustrative. Normalization depends on the search bounds.

“Optimal” means only the best candidate under this model, bounds and score. A maximum at the pressure/time boundary is expected under a monotone recovery model. It is not a plant operating recommendation. Slurry quantity changes assumed loading and therefore recovery; energy has both volume-dependent and fixed auxiliary components.

## Deploy to Streamlit Community Cloud

Official guide: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

1. Sign in to GitHub and create a repository named `redmudai`. Upload the **contents of this folder** to the repository root. Include `app.py`, `model.py`, `requirements.txt`, and `.streamlit/config.toml`. No secrets are required. Making a repository public publishes its source code.
2. Sign in at https://share.streamlit.io using your account and authorize GitHub access as requested by Streamlit.
3. Choose **Create app**, select the repository and branch (usually `main`), and set **Main file path** to `app.py`.
4. In Advanced settings select **Python 3.12**. Pick an available app subdomain if offered; its availability cannot be guaranteed in advance.
5. Deploy. Wait for the app to load, then open its generated `https://…streamlit.app` URL in a signed-out browser to verify public access. If app sharing is private, change the sharing setting to public.
6. Rehearse the same default scenario at the public URL. Open it before the presentation to allow a sleeping app to wake. Keep the local version available as a fallback.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest test_model.py
```

Tests cover mass conservation, bounded/nonnegative outputs, monotonic recovery, invalid inputs, and optimization score selection. Streamlit AppTest can additionally check UI rendering and widget reruns. Numerical/software tests do **not** validate the physical parameters.
