# -*- coding: utf-8 -*-
"""Fig. 1: same saved audited means/SE/95% CIs; no raw-data recomputation or source writes."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from figure_layout import FIGSIZE, MAIN_RECT, CONTRAST_RECTS
from plot_config import MAIN_DATA
from plot_output import save_figure
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9.5,'axes.labelsize':9.5,
 'axes.titlesize':9.5,'legend.fontsize':8,'xtick.labelsize':8.5,'ytick.labelsize':8.5,
 'axes.linewidth':.8,'svg.fonttype':'none','pdf.fonttype':42})
C={'L':'#2466A8','U':'#D18326','D':'#B42C48','heat':'#885AA8',
   'velocity':'#2466A8','lifetime':'#309479','net':'#303A44'}
def clean(ax):
    ax.tick_params(direction='in',top=True,right=True,length=3,width=.7)
    ax.grid(axis='y',color='#E6E8EB',lw=.5,zorder=0)
def save(fig, name, fixed_canvas=False):
    return save_figure(fig, "Fig1", dpi=450)
means = pd.read_csv(MAIN_DATA / "hnemd_summary.csv")
md = pd.read_csv(MAIN_DATA / "hnemd_differences.csv")
assert len(means) == 9 and len(md) == 9
fig=plt.figure(figsize=FIGSIZE)
axk=fig.add_axes(MAIN_RECT)
for state,marker in [('L','o'),('U','s'),('D','^')]:
    z=means[means.state==state].sort_values('T_K')
    axk.errorbar(z.T_K,z['mean'],yerr=z.se,fmt=marker+'-',ms=4,mfc='white',
                 color=C[state],capsize=2,lw=1.2,label='$'+state+'$')
axk.set_xlim(130,320);axk.set_xticks([150,200,300]);axk.set_ylim(25,98)
axk.set_xlabel('Temperature (K)');axk.set_ylabel(r'$\kappa$ (W m$^{-1}$ K$^{-1}$)')
axk.set_title('(a)',loc='left',pad=8)
axk.legend(frameon=False,ncol=3,loc='upper center',bbox_to_anchor=(.5,1.02),
           handlelength=1.0,columnspacing=.8)
# Panels b to d show one temperature each with a row for each contrast.
contrast_styles=[('L-U','Mean mass',C['L'],'o'),('U-D','Disorder',C['D'],'s'),
      ('L-D','Total',C['net'],'D')]
temps=[150.,200.,300.]
for j,Tk in enumerate(temps):
    ax=fig.add_axes(CONTRAST_RECTS[j])
    for i,(pair,label,color,marker) in enumerate(contrast_styles):
        r=md[(md.contrast==pair)&(md['T']==Tk)].iloc[0]
        sig=r.low>0 or r.high<0
        ax.errorbar(r.difference,2-i,
                    xerr=[[r.difference-r.low],[r.high-r.difference]],
                    fmt=marker,color=color,mfc=color if sig else 'white',
                    mew=1.0,ms=4.2,capsize=2.4,lw=1.1,
                    label=label if j==0 else None)
    ax.axvline(0,color='black',lw=.9)
    ax.set_yticks([0,1,2],['Total','Disorder','Mean mass'])
    ax.set_ylim(-.6,2.6);ax.set_xlim(-30,36);ax.set_xticks([-20,0,20])
    if j==2: ax.set_xlabel(r'$\Delta\kappa$ (W m$^{-1}$ K$^{-1}$)')
    else: ax.set_xticklabels([])
    ax.set_title(f'({chr(98+j)}) {int(Tk)} K',loc='left',pad=8 if j==0 else 4)
    ax.tick_params(direction='in',top=True,right=True,length=3,width=.7)
    ax.grid(False)
axk.tick_params(direction='in',top=True,right=True,length=3,width=.7)
axk.grid(False)
save(fig,'fig1',fixed_canvas=True)
