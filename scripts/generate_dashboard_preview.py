import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import pandas as pd
import numpy as np
from pathlib import Path

df = pd.read_parquet('data/processed/sample_features.parquet')
out_dir = Path('reports/figures')

plt.style.use('dark_background')
fig = plt.figure(figsize=(15, 9), facecolor='#0b0f19')
gs = gridspec.GridSpec(2, 2, height_ratios=[0.24, 0.76], hspace=0.35, wspace=0.25)

# --- Top: KPI Cards ---
ax_kpi = fig.add_subplot(gs[0, :])
ax_kpi.set_facecolor('#0b0f19')
ax_kpi.axis('off')

flagged_sum = int(df['is_flagged'].sum())
flagged_pct = (df['is_flagged'].mean() * 100)
mean_hype = df['hype_score'].mean()

kpis = [
    ('Total Media Items', f'{len(df)}', '#38bdf8', '10 Feeds + Audio STT'),
    ('High-Hype Flagged', f'{flagged_sum} ({flagged_pct:.1f}%)', '#f43f5e', 'Threshold >= 0.50'),
    ('Mean Hype Score', f'{mean_hype:.3f}', '#a855f7', 'Moderate Industry Baseline'),
    ('Echo Nodes & Edges', '11 Nodes / 14 Edges', '#34d399', 'PageRank Epicenter: CNBC')
]

for idx, (title, val, color, sub) in enumerate(kpis):
    x = 0.02 + idx * 0.25
    rect = FancyBboxPatch((x, 0.08), 0.22, 0.82, transform=ax_kpi.transAxes,
                          boxstyle='round,pad=0.03,rounding_size=0.05',
                          facecolor='#1e293b', edgecolor='#334155', linewidth=1.5)
    ax_kpi.add_patch(rect)
    ax_kpi.text(x + 0.11, 0.68, title, transform=ax_kpi.transAxes,
                ha='center', va='center', color='#94a3b8', fontsize=11, fontweight='bold')
    ax_kpi.text(x + 0.11, 0.38, val, transform=ax_kpi.transAxes,
                ha='center', va='center', color=color, fontsize=16, fontweight='heavy')
    ax_kpi.text(x + 0.11, 0.17, sub, transform=ax_kpi.transAxes,
                ha='center', va='center', color='#64748b', fontsize=9)

# --- Bottom Left: Radar Chart ---
categories = ['Superlative\nDensity', 'Sentiment\nSubjectivity', 'Clickbait\nSyntax', 'Vague\nAuthority', 'Ungrounded\nClaims']
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

ax_radar = fig.add_subplot(gs[1, 0], polar=True)
ax_radar.set_facecolor('#1e293b')

cnbc = [0.85, 0.55, 0.40, 0.35, 0.70]
cnbc += cnbc[:1]
reuters = [0.00, 0.35, 0.05, 0.00, 0.00]
reuters += reuters[:1]

ax_radar.plot(angles, cnbc, linewidth=2.5, linestyle='solid', color='#f43f5e', label='CNBC Markets (Score: 0.70)')
ax_radar.fill(angles, cnbc, color='#f43f5e', alpha=0.25)

ax_radar.plot(angles, reuters, linewidth=2.5, linestyle='solid', color='#34d399', label='Reuters Wire (Score: 0.08)')
ax_radar.fill(angles, reuters, color='#34d399', alpha=0.20)

ax_radar.set_xticks(angles[:-1])
ax_radar.set_xticklabels(categories, color='#cbd5e1', size=10, fontweight='bold')
ax_radar.tick_params(colors='#64748b')
ax_radar.grid(color='#334155', linestyle=':')
ax_radar.spines['polar'].set_color('#475569')
ax_radar.set_title('5-Factor Linguistic Fingerprint\n(High Hype vs. Wire Baseline)', color='#ffffff', size=13, fontweight='bold', pad=25)
ax_radar.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15), facecolor='#1e293b', edgecolor='#475569', fontsize=9)

# --- Bottom Right: Hype Score Distribution ---
ax_hist = fig.add_subplot(gs[1, 1])
ax_hist.set_facecolor('#1e293b')

counts, bins, patches = ax_hist.hist(df['hype_score'], bins=15, edgecolor='#334155', linewidth=1.2)
for bin_left, patch in zip(bins[:-1], patches):
    if bin_left < 0.25:
        patch.set_facecolor('#34d399')
    elif bin_left < 0.50:
        patch.set_facecolor('#fb923c')
    elif bin_left < 0.75:
        patch.set_facecolor('#f43f5e')
    else:
        patch.set_facecolor('#e11d48')

ax_hist.axvline(x=0.50, color='#f43f5e', linestyle='--', linewidth=2, label='Alert Line (>=0.50)')
ax_hist.set_title('Hype Score Distribution Across 151 Items', color='#ffffff', size=13, fontweight='bold', pad=15)
ax_hist.set_xlabel('Hype Score (0.00 = Wire, 1.00 = Peak Hype)', color='#94a3b8', size=10)
ax_hist.set_ylabel('Number of Media Items', color='#94a3b8', size=10)
ax_hist.grid(color='#334155', linestyle=':', alpha=0.6)
ax_hist.tick_params(colors='#cbd5e1')
for spine in ax_hist.spines.values():
    spine.set_color('#475569')
ax_hist.legend(facecolor='#1e293b', edgecolor='#475569', fontsize=9)

plt.suptitle('BS & Hype Analyzer — Executive Decision Dashboard', fontsize=18, fontweight='heavy', color='#ffffff', y=0.98)
plt.savefig(out_dir / 'dashboard_preview.png', dpi=200, bbox_inches='tight')
plt.close()
print('dashboard_preview.png successfully generated!')
