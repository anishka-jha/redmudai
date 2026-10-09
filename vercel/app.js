const $=id=>document.getElementById(id);
const fmt=(n,d=1)=>n.toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
let latest;
let saved=[];
function cards(items){return items.map(([label,value])=>`<div class="metric"><span>${label}</span><strong>${value}</strong></div>`).join('');}
function svgPlot(points,{xmax,ymax=100,xlabel,ylabel,line=false,selected}){
  const w=450,h=280,l=48,r=18,top=20,bottom=43;
  const x=v=>l+v/xmax*(w-l-r),y=v=>h-bottom-v/ymax*(h-top-bottom);
  let content='';
  for(let v=0;v<=100;v+=25) content+=`<line x1="${l}" x2="${w-r}" y1="${y(v)}" y2="${y(v)}" stroke="#e5edf1"/><text x="${l-9}" y="${y(v)+4}" text-anchor="end">${v}</text>`;
  for(let i=0;i<=4;i++)content+=`<text x="${x(xmax*i/4)}" y="${h-bottom+19}" text-anchor="middle">${fmt(xmax*i/4,line?0:2)}</text>`;
  if(line) content+=`<polyline points="${points.map(p=>`${x(p.x)},${y(p.y)}`).join(' ')}" fill="none" stroke="#2e9298" stroke-width="3"/>`;
  content+=points.map(p=>`<circle tabindex="0" cx="${x(p.x)}" cy="${y(p.y)}" r="${line?3:3.4}" fill="${line?'#2e9298':`hsl(${180+p.pressure*2},40%,${65-p.pressure*2}%)`}" opacity=".8"><title>${p.tip}</title></circle>`).join('');
  content+=`<text x="${w/2}" y="${h-3}" text-anchor="middle">${xlabel}</text><text transform="translate(12 ${h/2}) rotate(-90)" text-anchor="middle">${ylabel}</text>`;
  if(selected)content+=`<text x="${x(selected.x)}" y="${y(selected.y)+6}" text-anchor="middle" style="fill:#c45b43;font-size:23px">★<title>${selected.tip}</title></text>`;
  return `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${ylabel} versus ${xlabel}">${content}</svg><p class="chart-readout" aria-live="polite">Hover or focus a point to inspect its modeled values.</p>`;
}
function update(){
  const s=+$('solids').value,q=+$('quantity').value,p=+$('pressure').value,t=+$('time').value,goal=$('goal').value;
  $('solids-value').textContent=`${s}% by mass`;$('pressure-value').textContent=`${p} bar`;$('time-value').textContent=`${t} min`;
  let c,o;
  try{c=simulate(s,q,p,t);o=optimize(s,q,goal);$('error').textContent='';$('download').disabled=false;}catch(e){$('error').textContent='Enter a slurry quantity from 1 to 100,000 kg. Displayed results remain from the last valid batch.';$('download').disabled=true;return;}
  latest={label:'Illustrative / unvalidated; no trained AI; not industrial advice',inputs:{solids_pct:s,quantity_kg:q,goal},current:c,grid_optimum:o};
  $('metrics').innerHTML=cards([['Water recovery',fmt(c.recovery_pct)+'%'],['Recovered water',fmt(c.recovered_water_kg)+' kg'],['Residual cake moisture',fmt(c.moisture_pct)+'%'],['Illustrative energy',fmt(c.energy_kwh,4)+' kWh']]);
  $('opt-title').textContent=goal+' · best point in the search grid';
  $('optimum').innerHTML=cards([['Optimal modeled pressure',fmt(o.pressure_bar,1)+' bar'],['Optimal modeled time',fmt(o.time_min,0)+' min'],['Modeled recovery',fmt(o.recovery_pct)+'%'],['Illustrative energy',fmt(o.energy_kwh,4)+' kWh']]);
  const floor=.35*c.solids_kg, ceiling=100*Math.max(0,c.initial_water_kg-floor)/c.initial_water_kg;
  $('insight').textContent=`Of ${fmt(c.initial_water_kg)} kg initial water, this scenario recovers ${fmt(c.recovered_water_kg)} kg and retains ${fmt(c.cake_water_kg)} kg in the cake. ${fmt(c.recovery_pct/ceiling*100)}% of the model’s removable water is recovered.`;
  $('model-limit').textContent=`The assumed retention floor limits recovery to ${fmt(ceiling)}% for this composition, even with longer filtration. This ceiling comes from the invented 0.35 kg water/kg dry-solids parameter.`;
  $('comparison').innerHTML=[['Current',c],['Selected goal',o]].map(([label,r])=>`<tr><td>${label}</td><td>${fmt(r.pressure_bar)} bar / ${r.time_min} min</td><td>${fmt(r.recovery_pct)}%</td><td>${fmt(r.moisture_pct)}%</td><td>${fmt(r.energy_kwh,4)} kWh</td></tr>`).join('');
  const deltaWater=o.recovered_water_kg-c.recovered_water_kg, deltaEnergy=o.energy_kwh-c.energy_kwh;
  $('decision-summary').textContent=`The selected point models ${fmt(Math.abs(deltaWater))} kg ${deltaWater>=0?'more':'less'} recovered water and ${fmt(Math.abs(deltaEnergy),4)} kWh ${deltaEnergy>=0?'more':'less'} energy than your current settings. The selected goal can trade recovery for energy; it is not automatically better on every measure.`;
  $('goal-description').textContent={Balanced:'65% normalized recovery reward minus 35% normalized energy penalty. Invented weights for demonstration.', 'Max recovery':'Highest recovery in the finite grid. A boundary optimum is expected under this monotone model.', 'Min energy':'Lowest energy while achieving at least 80% of the grid’s maximum modeled recovery. This avoids the trivial no-filtration solution.'}[goal];
  const curve=Array.from({length:120},(_,i)=>{const r=simulate(s,q,p,i+1);return{x:i+1,y:r.recovery_pct,tip:`${i+1} min · ${fmt(r.recovery_pct)}% recovery`};});
  $('curve').innerHTML=svgPlot(curve,{xmax:120,xlabel:'Filtration time (min)',ylabel:'Water recovery (%)',line:true,selected:{x:t,y:c.recovery_pct,tip:'Current settings'}});
  const rows=candidates(s,q);
  $('tradeoff').innerHTML=svgPlot(rows.map(r=>({x:r.energy_kwh,y:r.recovery_pct,pressure:r.pressure_bar,tip:`${r.pressure_bar} bar · ${r.time_min} min · ${fmt(r.recovery_pct)}% · ${fmt(r.energy_kwh,4)} kWh`})),{xmax:Math.max(...rows.map(r=>r.energy_kwh))*1.05,xlabel:'Illustrative energy (kWh)',ylabel:'Water recovery (%)',selected:{x:o.energy_kwh,y:o.recovery_pct,tip:'Selected goal'}});
  const parts=[['Recovered water',c.recovered_water_kg,'#4eaaa0'],['Dry solids in cake',c.solids_kg,'#c45b43'],['Retained cake water',c.cake_water_kg,'#9cafba']];
  $('balance').innerHTML=`<div class="bar" role="img" aria-label="Mass balance">${parts.map(([name,value,color])=>`<div style="width:${100*value/q}%;background:${color}" title="${name}: ${fmt(value)} kg"></div>`).join('')}</div><div class="legend">${parts.map(([name,value,color])=>`<span><i class="dot" style="background:${color}"></i>${name}: ${fmt(value)} kg</span>`).join('')}</div>`;
  $('balance-text').textContent=`${fmt(q,2)} kg feed = ${fmt(c.recovered_water_kg,2)} kg recovered water + ${fmt(c.cake_mass_kg,2)} kg wet cake.`;
  for(const plotId of ['curve','tradeoff']){
    const plot=$(plotId), readout=plot.querySelector('.chart-readout');
    for(const point of plot.querySelectorAll('circle')){
      const show=()=>{readout.textContent=point.querySelector('title').textContent;};
      point.addEventListener('pointerenter',show);point.addEventListener('focus',show);point.addEventListener('click',show);
    }
  }
}
for(const id of ['solids','quantity','pressure','time','goal'])$(id).addEventListener('input',update);
$('reset').addEventListener('click',()=>{for(const[id,value]of Object.entries({solids:30,quantity:1000,pressure:3,time:30,goal:'Balanced'}))$(id).value=value;update();});
$('download').addEventListener('click',()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(latest,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='redmudai-results.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
update();
for(const button of document.querySelectorAll('[data-preset]'))button.addEventListener('click',()=>{
  const presets={gentle:{solids:30,quantity:1000,pressure:1,time:30,goal:'Min energy'},long:{solids:30,quantity:1000,pressure:3,time:60,goal:'Balanced'},dense:{solids:50,quantity:1000,pressure:3,time:30,goal:'Balanced'}};
  for(const[id,value]of Object.entries(presets[button.dataset.preset]))$(id).value=value;update();
});
function renderSaved(){
  if(!saved.length){$('saved-scenarios').innerHTML='<p class="empty-state">Your first comparison starts with a question.<br><span>Try 30 minutes vs. 60 minutes, then compare recovery and energy.</span></p>';return;}
  $('saved-scenarios').innerHTML='<table><thead><tr><th>Scenario</th><th>Batch</th><th>Pressure / time</th><th>Recovery</th><th>Recovered water</th><th>Energy</th></tr></thead><tbody>'+saved.map((r,i)=>`<tr><td>${i+1}</td><td>${fmt(r.solids_kg/(r.solids_kg+r.initial_water_kg)*100,0)}% / ${fmt(r.solids_kg+r.initial_water_kg,0)} kg</td><td>${r.pressure_bar} bar / ${r.time_min} min</td><td>${fmt(r.recovery_pct)}%</td><td>${fmt(r.recovered_water_kg)} kg</td><td>${fmt(r.energy_kwh,4)} kWh</td></tr>`).join('')+'</tbody></table>';
}
$('save-scenario').addEventListener('click',()=>{if($('download').disabled)return;if(saved.length===4)saved.shift();saved.push({...latest.current});renderSaved();});
$('clear-scenarios').addEventListener('click',()=>{saved=[];renderSaved();});
