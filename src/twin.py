"""ISS Crew Ultrasound Phantom Verification Twin (SIMULATION ONLY).
All parameter distributions are ESTIMATED/ASSUMED from literature-typical ranges,
not measured. Only the nominal targets (~5 kPa, ~27 kPa) are inspired by
M. Lozada-Longog's Hele Imua phantom work."""
import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, pathlib
rng=np.random.default_rng(2027); N=20000; RHO=1040.0
ROOT=pathlib.Path(__file__).resolve().parents[1]; FIG=ROOT/"figures"; FIG.mkdir(exist_ok=True)
TARGETS={"soft_5kPa":5.0,"firm_27kPa":27.0}
TOL=0.10   # REQ: measured E within ±10% of certified value
# ASSUMED sensitivities (labelled estimates)
dE_dT_cool=-0.015   # frac/°C deviation of cool-down temperature from 4 °C setpoint
dE_dT_cabin=-0.020  # frac/°C cabin temp away from 22 °C at measurement (gel softening)
k_preload=4.0       # apparent stiffening per unit compressive strain (nonlinear gel)
c_bias_speed=0.0025 # frac speed-of-sound error per °C -> elastography scaling error x2
def sample(n):
    return pd.DataFrame({
      "cool_dev_C": rng.normal(0,2.0,n),            # cool-down setpoint error
      "uniformity_cv": np.abs(rng.normal(0,0.04,n)), # gel uniformity proxy (CV), vibration-worsened
      "vib_grms": rng.uniform(0.5,6.0,n),             # shipping vibration proxy (launch-ish ~6 gRMS)
      "cabin_C": rng.uniform(18.5,26.7,n),           # ISS USOS nominal band
      "probe_strain": np.abs(rng.normal(0.03,0.025,n)), # operator preload (crew, minimal training)
    })
def measure(E0,d):
    nonunif=d.uniformity_cv*(1+0.08*d.vib_grms)       # vibration amplifies inhomogeneity (assumed)
    E_true=E0*(1+dE_dT_cool*d.cool_dev_C)*(1+dE_dT_cabin*(d.cabin_C-22))
    E_app=E_true*(1+k_preload*d.probe_strain)*(1+rng.normal(0,1,len(d))*nonunif)
    E_app*=(1+2*c_bias_speed*(d.cabin_C-22)*rng.choice([0,1],len(d),p=[.5,.5]))  # uncorrected-scanner half
    return E_app
rows=[];res={}
for name,E0 in TARGETS.items():
    d=sample(N); Em=measure(E0,d); err=Em/E0-1; d["err"]=err
    X=(d.drop(columns="err")-d.drop(columns="err").mean())/d.drop(columns="err").std()
    beta=np.linalg.lstsq(np.c_[np.ones(N),X],(err-err.mean())/err.std(),rcond=None)[0][1:]
    src=dict(zip(X.columns,beta**2/np.sum(beta**2)))
    # mitigated scenario: preload controlled by standoff gauge, cabin-temp correction
    d2=d.copy(); d2.probe_strain=np.abs(rng.normal(0.01,0.005,N)); d2.cabin_C=22+(d.cabin_C-22)*0.2
    err2=measure(E0,d2)/E0-1
    cs=np.sqrt(Em*1e3/(3*RHO))
    res[name]=dict(E0=E0,pass_base=np.mean(np.abs(err)<=TOL),pass_mit=np.mean(np.abs(err2)<=TOL),
        bias_pct=100*np.median(err),p95_abs_pct=100*np.quantile(np.abs(err),.95),
        shear_speed_mps=np.median(cs),src=src,err=err,err2=err2)
summary=pd.DataFrame([{ "phantom":k,"E_target_kPa":v["E0"],"median_bias_%":round(v["bias_pct"],1),
  "p95_|err|_%":round(v["p95_abs_pct"],1),"pass_rate_baseline":round(v["pass_base"],3),
  "pass_rate_mitigated":round(v["pass_mit"],3),"median_shear_speed_m/s":round(v["shear_speed_mps"],2),
  **{f"var_share_{a}":round(b,3) for a,b in v["src"].items()}} for k,v in res.items()])
summary.to_csv(ROOT/"docs/results_summary.csv",index=False); print(summary.T.to_string())
fig,ax=plt.subplots(1,2,figsize=(11,4.2),dpi=200)
for a,(k,v) in zip(ax,res.items()):
    a.hist(100*v["err"],bins=120,alpha=.6,label=f"baseline (pass {v['pass_base']:.0%})",density=True)
    a.hist(100*v["err2"],bins=120,alpha=.6,label=f"mitigated (pass {v['pass_mit']:.0%})",density=True)
    a.axvspan(-10,10,color="g",alpha=.08); a.set_xlim(-40,60)
    a.set_title(f"{k}: E target {v['E0']} kPa (simulated)"); a.set_xlabel("Apparent stiffness error (%)"); a.legend(fontsize=8)
fig.suptitle("Monte Carlo (N=20,000/phantom): calibration error vs ±10% verification band"); fig.tight_layout()
fig.savefig(FIG/"fig1_calibration_error_mc.png")
fig,ax=plt.subplots(figsize=(7,4),dpi=200); labs=list(res["soft_5kPa"]["src"]); x=np.arange(len(labs))
for i,(k,v) in enumerate(res.items()): ax.bar(x+i*.4-.2,[v["src"][l] for l in labs],.4,label=k)
ax.set_xticks(x,["cool-down\ntemp","gel uniformity\nproxy","vibration\n(gRMS)","cabin\ntemp","probe\npreload"])
ax.set_ylabel("Share of explained variance (SRC²)"); ax.set_title("Sensitivity: which process variables drive calibration error"); ax.legend()
fig.tight_layout(); fig.savefig(FIG/"fig2_sensitivity_tornado.png")
