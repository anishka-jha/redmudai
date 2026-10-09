import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from model import simulate, optimize, candidates, to_dict, GOALS

st.set_page_config(page_title='RedMudAI | Water Recovery Lab', page_icon='💧', layout='wide')
st.markdown('''<style>
.block-container {padding-top:2rem; max-width:1400px;}
h1 {letter-spacing:-1.5px;}
[data-testid="stMetric"] {background:white; border:1px solid #e2e8ed; border-radius:14px; padding:18px;}
[data-testid="stMetricValue"] {font-size:1.55rem;}
.hero {background:linear-gradient(115deg,#132f3b,#245866);color:white;padding:30px;border-radius:20px;margin-bottom:22px;}
.hero h1 {color:white;margin:6px 0;} .hero p {color:#cfe1e6;max-width:800px;}
.tag {font-size:12px;letter-spacing:2px;color:#efb39f;}
</style>''', unsafe_allow_html=True)
st.markdown('''<div class="hero"><div class="tag">MINING FELLOWSHIP · CONCEPT DEMONSTRATOR</div>
<h1>RedMudAI <span style="font-weight:300">Water Recovery Lab</span></h1>
<p>Explore how batch composition, filtration pressure and time affect modeled water recovery — and compare operating tradeoffs.</p></div>''', unsafe_allow_html=True)
st.warning('ILLUSTRATIVE / UNVALIDATED — Simplified simulation, no experimental training data or AI predictions. Values are not industrial performance claims or operating recommendations.')

with st.sidebar:
    st.title('💧 Set up your batch')
    st.caption('All sliders update the simulation immediately.')
    solids = st.slider('Solids concentration (% by mass)', 5, 60, 30)
    quantity = st.number_input('Slurry quantity (kg)', min_value=1.0, max_value=100000.0, value=1000.0, step=100.0)
    pressure = st.slider('Filtration pressure (bar)', 0.5, 10.0, 3.0, 0.5)
    time = st.slider('Filtration time (minutes)', 1, 120, 30)
    goal = st.selectbox('Optimization goal', GOALS, index=2)
    st.caption('Search bounds: 0.5–10 bar in 0.5-bar steps; 5–120 min in 5-min steps. Current simulation also permits 1–4 min.')
    st.divider()
    st.caption('RedMudAI is a project name. This MVP uses equations and a finite grid search; it has no trained AI model.')

current = simulate(solids, quantity, pressure, time)
optimal = optimize(solids, quantity, goal)
st.subheader('Your batch · modeled estimates')
cols = st.columns(4)
for col, label, value in zip(cols, ['Water recovery', 'Recovered water', 'Residual cake moisture', 'Illustrative energy'],
        [f'{current.recovery_pct:.1f}%', f'{current.recovered_water_kg:,.1f} kg', f'{current.moisture_pct:.1f}%', f'{current.energy_kwh:.4f} kWh']):
    col.metric(label, value)
st.caption('Recovery = recovered water ÷ initial water. Cake moisture = retained water ÷ wet cake mass. Energy includes assumed pumping work and auxiliary electricity only.')

tab1, tab2, tab3 = st.tabs(['Explore & compare', 'Mass balance', 'Model & assumptions'])
with tab1:
    st.subheader(f'{goal} · best point in the illustrative search grid')
    a,b,c,d = st.columns(4)
    a.metric('Optimal modeled pressure', f'{optimal.pressure_bar:g} bar')
    b.metric('Optimal modeled time', f'{optimal.time_min:g} min')
    c.metric('Modeled recovery at this point', f'{optimal.recovery_pct:.1f}%', f'{optimal.recovery_pct-current.recovery_pct:+.1f} percentage points')
    d.metric('Illustrative energy at this point', f'{optimal.energy_kwh:.4f} kWh')
    st.info('Max recovery: highest recovered fraction. Min energy: least energy while achieving ≥80% of the grid’s maximum recovery. Balanced: 65% normalized recovery reward minus 35% normalized energy penalty. These are demonstration choices, not validated process targets.')
    left,right = st.columns(2)
    with left:
        fig = go.Figure()
        for p in sorted(set([0.5, pressure, optimal.pressure_bar, 10.0])):
            points = [simulate(solids, quantity, p, t) for t in range(1,121)]
            fig.add_trace(go.Scatter(x=[r.time_min for r in points], y=[r.recovery_pct for r in points], name=f'{p:g} bar'))
        fig.add_trace(go.Scatter(x=[time], y=[current.recovery_pct], mode='markers', name='Current', marker=dict(size=13,color='#c4583f')))
        fig.update_layout(title='Illustrative recovery over time', xaxis_title='Time (min)', yaxis_title='Initial water recovered (%)', yaxis_range=[0,100], legend_title='Pressure')
        st.plotly_chart(fig, use_container_width=True)
    with right:
        frame = pd.DataFrame([to_dict(r) for r in candidates(solids,quantity)])
        fig = px.scatter(frame, x='energy_kwh', y='recovery_pct', color='pressure_bar', hover_data=['time_min'], labels={'energy_kwh':'Illustrative energy (kWh)','recovery_pct':'Water recovery (%)','pressure_bar':'Pressure (bar)','time_min':'Time (min)'}, color_continuous_scale='Teal', title='Illustrative recovery–energy tradeoff')
        fig.add_trace(go.Scatter(x=[optimal.energy_kwh], y=[optimal.recovery_pct], mode='markers', name='Selected goal', marker=dict(symbol='star',size=18,color='#c4583f')))
        st.plotly_chart(fig, use_container_width=True)
    st.dataframe(pd.DataFrame([{'Scenario':'Current',**to_dict(current)},{'Scenario':goal,**to_dict(optimal)}])[['Scenario','pressure_bar','time_min','recovery_pct','recovered_water_kg','moisture_pct','energy_kwh']], hide_index=True, width='stretch')
    st.download_button('Download modeled results (JSON)', json.dumps({'label':'Illustrative / unvalidated; not industrial advice','inputs':{'solids_pct':solids,'quantity_kg':quantity,'goal':goal},'current':to_dict(current),'grid_optimum':to_dict(optimal)}, indent=2), 'redmudai-results.json', 'application/json')
with tab2:
    st.subheader('Every kilogram accounted for')
    fig = go.Figure(go.Sankey(node=dict(label=['Feed slurry','Dry solids in cake','Water in feed','Recovered water','Retained cake water'],color=['#173e4b','#c4583f','#4b9ba6','#66b3a6','#9aacb8']),link=dict(source=[0,0,2,2],target=[1,2,3,4],value=[current.solids_kg,current.initial_water_kg,current.recovered_water_kg,current.cake_water_kg])))
    fig.update_layout(title='Modeled mass flows (kg)', height=380)
    st.plotly_chart(fig, use_container_width=True)
    st.success(f'{quantity:,.2f} kg feed = {current.recovered_water_kg:,.2f} kg recovered water + {current.cake_mass_kg:,.2f} kg wet cake. Dry solids remain {current.solids_kg:,.2f} kg.')
with tab3:
    st.subheader('Transparent equations, explicit limitations')
    st.markdown('''Solids concentration is a **mass percentage**. All solids remain in the cake; no evaporation, dissolution, leakage or solids in the filtrate is modeled. Water density is assumed to be **1,000 kg/m³**.

The chosen retained-water floor is **0.35 kg water per kg dry solids**. It is an arbitrary demonstration parameter, not a measured red-mud property. Filter area is held fixed; batch-size scaling is illustrative.''')
    st.code('dry_solids = batch_kg × solids_pct / 100\ninitial_water = batch_kg − dry_solids\nremovable_water = max(0, initial_water − 0.35 × dry_solids)\ntau_min = 18 × (solids_pct / 30)^1.5 × (batch_kg / 1000)^0.5\nrecovered_water = removable_water × [1 − exp(−time_min × sqrt(pressure_bar) / tau_min)]\ncake_water = initial_water − recovered_water\nrecovery_pct = 100 × recovered_water / initial_water\nmoisture_pct = 100 × cake_water / (dry_solids + cake_water)\nenergy_kWh = pressure_bar × 100000 × (recovered_water / 1000) / (0.60 × 3600000)\n             + 0.25 × time_min / 60', language='text')
    st.markdown('''The exponential surrogate gives diminishing recovery and a water-retention floor. The **18-minute coefficient and concentration/loading exponents are invented**, not fitted to experiments. It is not a Darcy-law or cake-resistance model.

Energy assumes **60% hydraulic efficiency and 0.25 kW auxiliary power**. Both are unvalidated. Pressurization of feed/cake, compressed air, equipment standby, dewatering equipment design and upstream/downstream energy are excluded.

Pressure-dependent cake compression, filter area changes, permeability, particle size, temperature, red-mud chemistry and filtrate quality are excluded. Recovered water is not established as suitable for reuse. No uncertainty intervals are available because the model has no calibration data.

**Next validation step:** collect pressure/time/filtrate-mass/cake-moisture measurements with known filter area, fit parameters, compare held-out batches, and measure actual electricity. This MVP demonstrates the interface and tradeoff workflow only.''')
st.caption('RedMudAI · Presentation MVP · Every result is illustrative and unvalidated')
