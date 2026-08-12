from __future__ import annotations
import argparse,json,shutil,tempfile,zipfile,sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import v2_pipeline as v
MODELS=list(v.MAIN_MODEL_FAMILIES)
def locate(root:Path,suffix:str)->Path:
 hits=list(root.rglob(suffix))
 if not hits: raise FileNotFoundError(f"Could not locate {suffix} under {root}")
 return sorted(hits)[-1]
def stage_new_release(repo_path:Path,burden_csv:Path,work:Path):
 repo_root=repo_path
 if repo_path.suffix.lower()==".zip":
  repo_root=work/"repo";repo_root.mkdir(parents=True,exist_ok=True)
  with zipfile.ZipFile(repo_path) as z:z.extractall(repo_root)
 data=work/"data";snap=data/"gtb_snapshot_2025-07-30";snap.mkdir(parents=True,exist_ok=True)
 shutil.copy2(burden_csv,data/"TB_burden_countries_2026-07-18.csv")
 shutil.copy2(ROOT/"data"/"TB_data_dictionary_2026-07-18.csv",data/"TB_data_dictionary_2026-07-18.csv")
 shutil.copy2(locate(repo_root,"db_dr_country.rda"),data/"db_dr_country.rda")
 for f in ("drroutine.rda","tb.rda","tx.rda"):shutil.copy2(locate(repo_root,f),snap/f)
 return work
def metrics(actual,prediction):
 a=np.asarray(actual,float);p=np.asarray(prediction,float)
 return {"n":int(len(a)),"log_MAE":float(np.mean(np.abs(np.log1p(a)-np.log1p(p)))),"rate_MAE":float(np.mean(np.abs(a-p)))}
def evaluate_ensemble(panel,outcome,task,pred_path):
 rate_col="reported_rr_rate" if outcome=="reported" else "modeled_rr_rate"
 obs=panel[panel.year==2025][["iso3","country",rate_col]].rename(columns={rate_col:"actual_rate"})
 p=pd.read_csv(pred_path).merge(obs,on=["iso3","country"],how="inner");p=p[p.actual_rate.notna()].copy();p["actual_log"]=np.log1p(p.actual_rate)
 q={"outcome":outcome,"task":task,**metrics(p.actual_rate,p.prediction_rate),"coverage_0p05":float(((p.actual_log>=p.lower_log_0p05)&(p.actual_log<=p.upper_log_0p05)).mean()),"upper_alert_rate_0p05":float((p.actual_log>p.upper_log_0p05).mean())}
 return q,p
def family_consensus(panel,outcome,task,individual_path,seed_path):
 rate_col="reported_rr_rate" if outcome=="reported" else "modeled_rr_rate"
 obs=panel[panel.year==2025][["iso3","country",rate_col]].rename(columns={rate_col:"actual_rate"})
 ind=pd.read_csv(individual_path).merge(obs,on=["iso3","country"],how="inner");ind=ind[ind.actual_rate.notna()].copy();ind["actual_log"]=np.log1p(ind.actual_rate);ind["alert05"]=ind.actual_log>ind.upper_log_0p05;ind["alert025"]=ind.actual_log>ind.upper_log_0p025
 seeds=pd.read_csv(seed_path).merge(obs,on=["iso3","country"],how="inner");seeds=seeds[seeds.actual_rate.notna()].copy();seeds["actual_log"]=np.log1p(seeds.actual_rate);seeds["a05"]=seeds.actual_log>seeds.upper_log_0p05;seeds["a025"]=seeds.actual_log>seeds.upper_log_0p025
 sg=seeds.groupby(["iso3","model"]).agg(a05=("a05","mean"),a025=("a025","mean")).reset_index();sg["alert05"]=sg.a05>=.8;sg["alert025"]=sg.a025>=.8
 for m in ("gbm_trajectory","gbm_drivers"):ind=ind[ind.model!=m]
 gbm=sg[["iso3","model","alert05","alert025"]].merge(obs[["iso3","country"]],on="iso3",how="left")
 fam=pd.concat([ind[["iso3","country","model","alert05","alert025"]],gbm],ignore_index=True)
 c=fam.groupby(["iso3","country"]).agg(models=("model","nunique"),models_alert05=("alert05","sum"),models_alert025=("alert025","sum")).reset_index();c["stable_2025"]=(c.models_alert05>=4)&(c.models_alert025>=3)
 prior_file=ROOT/"outputs"/"tables"/f'{outcome}_{"stable_alerts" if task=="rolling" else "fixed_origin_stable_alerts"}.csv'
 prior=pd.read_csv(prior_file);prior=prior[prior.year==2024][["iso3","stable_year_alert"]].rename(columns={"stable_year_alert":"stable_2024"})
 c=c.merge(prior,on="iso3",how="left");c["stable_2024"]=c.stable_2024.fillna(False);c["strict_consecutive_2025"]=c.stable_2025&c.stable_2024;c["outcome"]=outcome;c["task"]=task
 return c
def main():
 ap=argparse.ArgumentParser(description="Evaluate the frozen V2 predictions on the next WHO release without retuning.");ap.add_argument("--who-repo",required=True,type=Path);ap.add_argument("--burden-csv",required=True,type=Path);ap.add_argument("--output-dir",required=True,type=Path);args=ap.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
 lock=json.loads((ROOT/"PROSPECTIVE_LOCK.json").read_text())
 with tempfile.TemporaryDirectory(prefix="mdr_v2_next_") as td:
  staged=stage_new_release(args.who_repo,args.burden_csv,Path(td)/"project");paths=v.build_paths(staged);panel,_=v.load_build_panel(paths)
  if int(panel.year.max())<2025:raise ValueError("New release does not contain 2025 outcome data.")
  summary=[];consensuses=[]
  for outcome in ("reported","modeled"):
   for task,stem in [("rolling","rolling"),("fixed_origin","fixed_origin")]:
    q,_=evaluate_ensemble(panel,outcome,task,ROOT/"outputs"/"tables"/f"prospective_2025_{outcome}_{stem}_ensemble.csv");summary.append(q);consensuses.append(family_consensus(panel,outcome,task,ROOT/"outputs"/"tables"/f"prospective_2025_{outcome}_{stem}_individual_models.csv",ROOT/"outputs"/"tables"/f"prospective_2025_{outcome}_{stem}_gbm_seed_predictions.csv"))
  summary=pd.DataFrame(summary);consensus=pd.concat(consensuses,ignore_index=True);summary.to_csv(args.output_dir/"PROSPECTIVE_2025_PERFORMANCE.csv",index=False);consensus.to_csv(args.output_dir/"PROSPECTIVE_2025_FAMILY_CONSENSUS.csv",index=False)
  result={"lock_prediction_sha256":lock["prediction_sha256"],"retuning_performed":False,"performance":summary.to_dict("records")};(args.output_dir/"PROSPECTIVE_2025_EVALUATION_MANIFEST.json").write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=="__main__":main()
