"""Export the actual benchmark dataflow as SVG and PNG."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch

root=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','svg.hashsalt':'dbs-corrected-v1'})
fig,ax=plt.subplots(figsize=(12,5.2));ax.set(xlim=(0,12),ylim=(0,5.2));ax.axis('off')
ax.text(.2,4.85,'A benchmark with an evaluator-side ground truth',fontsize=19,weight='bold',color='#202c40')
ax.text(.2,4.4,'OFFLINE SETUP  /  measured separately from the search budget',fontsize=10,color='#406681')
def box(x,y,title,body):
 ax.add_patch(FancyBboxPatch((x,y),2.55,1.05,boxstyle='round,pad=0.06',fc='#f2f5f7',ec='#bac7cf',lw=1))
 ax.text(x+.12,y+.75,title,fontsize=11,weight='bold',color='#202c40')
 ax.text(x+.12,y+.43,body,fontsize=9,va='top',color='#333333')
def arrow(x,y,u,v,dashed=False):
 ax.add_patch(FancyArrowPatch((x,y),(u,v),arrowstyle='-|>',mutation_scale=12,color='#406681',lw=1.2,linestyle='--' if dashed else '-'))
xs=[.25,3.25,6.25,9.25]
for x,t,b in zip(xs,['Define the feasible set','STN–GPe simulator','Build the objective','Enumerate the oracle'],
 ['Stage 1 / 2 grid; Stage 3 bits\nStage 2 feasibility before simulation',
  'Fixed model, no patient data\nBeta power normalized to baseline',
  'Stages 1 / 2: beta + energy\nStage 3: 41-point quadratic fit',
  'Full finite feasible domain\nOptimum held by the evaluator']):box(x,3.1,t,b)
for x in xs[:-1]:arrow(x+2.62,3.63,x+2.92,3.63)
ax.text(.2,2.7,'BUDGETED SEARCH  /  repeated with paired seeds 0–9',fontsize=10,color='#406681')
for x,t,b in zip(xs,['Shared initialization','Six optimization methods','Scalar oracle access','Regret and seed variation'],
 ['5 charged observations\nNo-stimulation control when allowed',
  'Random, GA, BO, CMA-ES\nExhaustive surrogate, QAOA p=1',
  'Stop at 40 unique setting queries\nCache repeated queries; keep a trace',
  'Best cost − finite-domain minimum\nRead prefixes at 10, 20, 30, 40']):box(x,1.3,t,b)
for x in xs[:-1]:arrow(x+2.62,1.83,x+2.92,1.83)
arrow(10.55,3.02,10.55,2.43,True)
arrow(7.52,1.22,4.55,1.22,True)
ax.text(.25,.58,'Resource ledger: simulator setup calls • objective queries • surrogate predictions • circuit executions • simulated shots • wall time',fontsize=10)
ax.text(.25,.23,'QAOA runs on a classical statevector simulator. Stage 3 queries evaluate a fitted QUBO. This is not a clinical treatment system.',fontsize=9)
fig.tight_layout(pad=.6)
fig.savefig(root/'assets/architecture.svg');fig.savefig(root/'assets/architecture.png',dpi=180)
