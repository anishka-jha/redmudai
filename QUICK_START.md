# Jaldi start / host karne ka easiest tareeka

Code copy-paste karne ki zarurat nahi: ZIP extract karke `redmudai` folder VS Code mein open karo. Files ready hain.

## Sabse fast demo: browser version

`vercel/index.html` double-click karo. Full simulation browser mein chalega; Python, npm, API key, ya backend ki zarurat nahi. Sliders, optimization, graphs aur download kaam karte hain. Yeh Python model ke same equations use karta hai.

## GitHub par push

VS Code mein `redmudai` folder open karo → Source Control → Initialize Repository → Stage All → Commit → Publish to GitHub. Account sign-in complete karo. Public repository choose karoge to source public ho jayega. Agar already Git repository use kar rahe ho to usmein yeh files add karke commit/push karo; dubara initialize mat karo.

Command-line alternative (new folder, Git installed):

```powershell
git init
git add .
git commit -m "Add RedMudAI presentation MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/redmudai.git
git push -u origin main
```

`YOUR_USERNAME` replace karo, aur pehle GitHub par empty `redmudai` repo banao. Existing remote ho to `git remote add` repeat mat karo.

## Vercel: full working browser version

Vercel dashboard → Add New → Project → GitHub repo import.

| Setting | Value |
|---|---|
| Root Directory | `vercel` |
| Framework Preset | Other |
| Build Command | Leave empty / override disabled |
| Output Directory | `.` |
| Install Command | None; no dependencies |

Deploy click karo. Vercel ka generated URL browser mein open karo aur sliders test karo. Presentation audience ke liye signed-out browser se production URL verify karo; agar protection enabled hai to project sharing/protection setting review karo.

## Render: original Streamlit version

Render dashboard → New → Web Service → same GitHub repo select.

| Setting | Value |
|---|---|
| Runtime | Python 3 |
| Root Directory | Empty (repository root) |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true --browser.gatherUsageStats false` |
| Environment variable | `PYTHON_VERSION=3.12.8` |
| Health Check Path | `/_stcore/health` |
| Instance plan | Free, if offered |

Alternative: New → Blueprint → repo select. Included `render.yaml` fills these settings. Review plan before creating; no paid subscription is needed for the prepared free configuration.

Render URL `https://...onrender.com` milega. Free services may sleep; presentation se pehle open karke wake-up hone do. Vercel browser version server-free fallback hai.

## Local Streamlit

VS Code terminal mein:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Then http://localhost:8501 open karo. `start.ps1` bhi same setup/run steps automate karta hai.

## Exactly kya bolna / dikhana hai

1. Defaults: 30% solids, 1000 kg slurry, 3 bar, 30 min, Balanced.
2. Modeled outputs: about **80.3%** water recovery, **561.8 kg** recovered water, **31.5%** wet-cake moisture, **0.2030 kWh** illustrative energy.
3. Time 60 min karo: recovery aur energy badhenge, recovery curve flatten hoga.
4. Goal badlo: Max recovery, Min energy, Balanced ke grid points compare karo. Current inputs aur grid optimum alag results hain.
5. Mass balance dikhao: 1000 kg = 561.8 kg recovered water + 438.2 kg wet cake; dry solids 300 kg.
6. Equations/assumptions dikhao. Bolo: “This is an illustrative unvalidated simulation, not a trained AI model. We need filtration experiments and measured energy to calibrate and validate it.”

“Optimal” sirf chosen bounds aur objective ka best grid point hai. Retention floor, kinetics, efficiency aur auxiliary power assumed/invented hain. No experimental or industrial validation. Detailed assumptions: README.md and app's Model & assumptions.

## Hosting references

- Render web services: https://render.com/docs/web-services
- Render Blueprint specification: https://render.com/docs/blueprint-spec
- Render free-service limitations: https://render.com/docs/free
- Vercel project setup: https://vercel.com/docs/projects/overview

No public URL has been created by preparing these files. A successful deployment and signed-out check are still required.
