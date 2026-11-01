import run from '@/data/research-oct13/run.json';
import {Research50Run} from './oct19-research';

const price=(v:number|null)=>v==null?'Price unpublished':new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(v);
export function CurrentLead({record,candidate}:{record?:any;candidate?:any}){
 const c=candidate||record?.researchOct13;
 if(!c)return null;
 return <section className="oct-lead panel stack">
  <div className="oct-eyebrow">OCTOBER 13 REVIEW · {c.priority}</div>
  <div className="oct-title"><div><h2>{c.name}</h2><p>{c.county}, {c.state} · {c.acres} advertised acres</p></div><strong>{price(c.price)}</strong></div>
  <p className="oct-muted">{c.novelty}. {c.priceNote}</p>
  <p>{c.why}</p><div className="oct-hold">{c.capitalDecision} · Research order does not establish available MW, a funded buyer or assignment value.</div>
  <dl className="oct-facts"><div><dt>Offered land</dt><dd>{c.apns.join(' · ')||'APN unresolved'}. {c.apnStatus}</dd></div><div><dt>Power</dt><dd>{c.power}</dd></div><div><dt>Fiber</dt><dd>{c.fiber}</dd></div><div><dt>What could stop it</dt><dd>{c.risk}</dd></div></dl>
  <div className="oct-next"><h3>Next evidence to obtain</h3><p>{c.nextTest}</p><p className="oct-muted">{c.contact} · {c.channel}</p></div>
  <div className="oct-links"><a href={c.listingUrl} target="_blank" rel="noreferrer">Observed source ↗</a><a href="/research-oct13">Full run and prior-week review →</a></div>
  <details><summary>Sources and proof limits</summary>{c.sourceIds.map((id:string)=>{const s=run.sources.find(x=>x.id===id);return s?<p key={id}><a href={s.url} target="_blank" rel="noreferrer">{s.title}</a> · {s.kind} · {s.date}. {s.limitation}</p>:null;})}</details>
  {c.id===run.focusId&&<details><summary>Hinds: all 16 control gates remain open</summary><div className="oct-table"><table><thead><tr><th>Gate</th><th>Status</th><th>Missing evidence</th></tr></thead><tbody>{run.hindsGates.map(g=><tr key={g.id}><td>{g.id} · {g.name}</td><td>{g.status}</td><td>{g.reason}</td></tr>)}</tbody></table></div></details>}
 </section>;
}
export function LatestResearch({full=false,records=[]}:{full?:boolean;records?:any[]}){
 const current=run.candidates.map(c=>({c,r:records.find(r=>r.id===c.id)}));
 return <>{!full&&<Research50Run/>}<section className="oct-research" aria-label="October 13 research run">
  <header className="oct-header"><div><div className="oct-eyebrow">HISTORICAL RUN · 13 OCTOBER 2026</div><h1>{full?'Hinds first. Evidence next.':'Hinds 110 is your active focus'}</h1><p>{run.conclusion}</p></div><a className="oct-button" href={full?'/?view=active':'/research-oct13'}>{full?'Open Hinds dossier':'Read full research run'} →</a></header>
  <div className="oct-metrics"><div><strong>Hinds 110</strong><span>Founder’s first priority</span></div><div><strong>Dillon 53 / 48</strong><span>Best backup research</span></div><div><strong>0</strong><span>New leads cleared for paid control</span></div><div><strong>$0</strong><span>New spending recommended</span></div></div>
  <p className="oct-muted">Prior week reviewed: October 6–12. Fourteen offering records reviewed or recovered; these are not fourteen new discoveries. Research priority is separate from paid-control eligibility.</p>
  <div className="oct-table"><table><thead><tr><th>Attention order</th><th>Offering / advertised ask</th><th>Current judgment</th><th>Next proof</th></tr></thead><tbody>{current.slice(0,full?current.length:4).map(({c,r})=><tr key={c.id}><td>#{c.rank}<br/><span className="oct-muted">{c.novelty}</span></td><td><a href={full?'#'+c.id:'/?view=parcels&record='+c.id}>{c.name}</a><br/>{price(c.price)} · {c.acres} acres</td><td><b>{c.priority}</b><p>{c.risk}</p>{r?.priority_tier==='REJECTED'&&<strong>Founder rejection preserved in dossier.</strong>}</td><td>{c.nextTest}</td></tr>)}</tbody></table></div>
  <div className="oct-next"><h2>Hinds: the immediate request</h2><p>Get the exact 110-acre offered survey and the issuer documents behind your reported power and fiber deliverability. Then resolve the actual 25 MW / 50 MW service path and design-specific Texas permitting requirements. Your earlier confirmation is preserved; this review has not independently documented its scope or transferability.</p></div>
  {!full&&<div className="oct-links"><a href="/?view=active">Open Hinds and prepared actions →</a><a href="/research-oct13#week">See what emerged over the past week →</a></div>}
  {full&&<>
   <section id="week" className="panel stack"><h2>What emerged over the past week?</h2><p><strong>Dillon 53 was the strongest backup research lead; Dillon 48 is the layout challenger.</strong> Great Falls, Abilene and Duck Hill did not clear the priority screen. No recovered watch report supplied a new parcel-specific Hinds power/fiber commitment.</p>{run.weekly.map(w=><details key={w.date}><summary>{w.date} · {w.leadImpact}</summary><p>{w.finding}</p></details>)}<p className="oct-muted">All seven Power/Siting originals were recovered. Fresh Land entries came from accessible prior conversation summaries and current listing checks. Full Fresh Land exports and Federal AI outputs were unavailable; cross-chat coverage is incomplete.</p></section>
   <section className="oct-section"><h2>Reviewed offerings</h2>{run.candidates.map(c=><details className="oct-candidate" id={c.id} key={c.id} open={c.id===run.focusId}><summary>{c.name} · {c.priority}</summary><CurrentLead candidate={c}/><a className="oct-record-link" href={'/?view=parcels&record='+c.id}>Open saved record, map and notes →</a></details>)}</section>
   <section className="panel stack"><h2>Prepared requests · no outreach sent</h2>{run.actions.map(a=><details key={a.id}><summary>{a.title}</summary><p><b>{a.contact}</b> · {a.channel}</p><p>{a.question}</p><p><b>Decision:</b> {a.decision}</p><p className="oct-muted">{a.costEstimate}</p></details>)}</section>
   <section className="panel stack"><h2>Other leads screened out or held</h2><p>Ten search/listing observations. These received triage, not full parcel clearance.</p>{run.excluded.map(x=><details key={x.name}><summary>{x.name} · {x.offer}</summary><p>{x.reason}</p><a href={x.url} target="_blank" rel="noreferrer">Observed listing / search source ↗</a><p className="oct-muted">{x.evidence}</p></details>)}</section>
   <section className="panel stack"><h2>Full work and evidence trail</h2><div className="oct-links"><a href="/research/2026-10-13/report.md" download>Complete research memo</a><a href="/research/2026-10-13/run.json" download>Structured current run</a><a href="/research/2026-10-13/recovered-week.json" download>Seven original watch reports</a><a href="/research/2026-10-13/dillon-adairsville-oct08.json" download>October 8 GIS and gate audit</a><a href="/research/2026-10-13/hinds-oct03-addendum.md" download>Hinds regulatory addendum</a></div><h3>Coverage</h3>{run.coverage.map(x=><p key={x}>{x}</p>)}<details><summary>Twenty source entries and limitations</summary>{run.sources.map(s=><p key={s.id}><a href={s.url} target="_blank" rel="noreferrer">{s.title}</a> · {s.publisher} · {s.date} · {s.kind}. {s.limitation}</p>)}</details><p className="oct-hold">Capital limits remain $5,000 learning / $10,000 all-in soft control. Prior exposure and remaining cash are unresolved. No money, messages or applications were sent.</p></section>
  </>}
 </section></>;
}
