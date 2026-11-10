# ══════════════════════════════════════════════════════════════
# fig1_dag_v2.py — Figure 1 (DAG), revision of the 2_analysis.ipynb
# Cell 1b version. Changes relative to v1 (content identical):
#   * filled solid arrowheads drawn as a separate SOLID segment, so
#     dashed shafts no longer produce broken/faint heads
#   * each arrow lands on its own anchor point on the target box —
#     no more overlapping head clusters at PSY / MSD
#   * long diagonals re-anchored/curved so no line crosses box text
# Output: ../output/fig_dag_v2.pdf / .png  (copy → Figure_1_DAG.pdf)
# ══════════════════════════════════════════════════════════════
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'output')
os.makedirs(OUT, exist_ok=True)

PAL = {
    'exposure':   {'fill': '#D6E0EA', 'edge': '#1F4E79', 'text': '#1F4E79'},
    'outcome':    {'fill': '#EFD9D6', 'edge': '#8B2E2E', 'text': '#8B2E2E'},
    'mediator':   {'fill': '#D9E4D9', 'edge': '#4A6B53', 'text': '#3F5A47'},
    'confounder': {'fill': '#E8E8E8', 'edge': '#6E6E6E', 'text': '#3D3D3D'},
    'key_conf':   {'fill': '#F0E2C2', 'edge': '#8E6815', 'text': '#7A5912'},
    'time':       {'fill': '#DDD8E8', 'edge': '#5F5278', 'text': '#4A3F61'},
}

fig, ax = plt.subplots(figsize=(11, 6.3))
ax.set_xlim(-0.3, 10.3)
ax.set_ylim(3.38, 8.72)
ax.set_aspect('equal')
ax.axis('off')

nodes = {
    'PSY':  (1.5, 6.0, 'Psychosocial\nExposures\n(JDC-S)', 'exposure'),
    'MSD':  (8.5, 6.0, 'Musculoskeletal\nDisorders\n(MSD)', 'outcome'),
    'SES':  (3.0, 8.0, 'Education',        'confounder'),
    'AGE':  (5.0, 8.0, 'Age, Sex',         'confounder'),
    'EMP':  (7.0, 8.0, 'Employment\ntype', 'confounder'),
    'IND':  (5.0, 4.0, 'Industry',         'key_conf'),
    'ERG':  (5.0, 5.35, 'Ergonomic\nExposures', 'mediator'),
    'WAVE': (1.5, 4.0, 'Wave\n(Time)',     'time'),
    'HRS':  (8.5, 4.0, 'Long\nwork hours', 'confounder'),
}

def calc_box_size(label):
    lines = label.split('\n')
    width = max(0.95, max(len(l) for l in lines) * 0.13 + 0.55)
    height = max(0.60, len(lines) * 0.40 + 0.20)
    return width, height

PAD = 0.04  # FancyBboxPatch round pad
box_geo = {}
for key, (x, y, label, role) in nodes.items():
    pal = PAL[role]
    w, h = calc_box_size(label)
    ax.add_patch(FancyBboxPatch((x - w/2, y - h/2), w, h,
                                boxstyle='round,pad=0.04',
                                facecolor=pal['fill'], edgecolor=pal['edge'],
                                linewidth=1.6, zorder=3))
    ax.text(x, y, label, ha='center', va='center', fontsize=9.5,
            fontweight='bold', color=pal['text'], zorder=4)
    box_geo[key] = (x, y, w/2 + PAD, h/2 + PAD)  # centre + half extents incl pad

def edge_point(key, side, frac):
    """Point on the box border. frac: 0→left/bottom end, 1→right/top end."""
    x, y, hw, hh = box_geo[key]
    if side == 'top':
        return np.array([x - hw + 2*hw*frac, y + hh])
    if side == 'bottom':
        return np.array([x - hw + 2*hw*frac, y - hh])
    if side == 'left':
        return np.array([x - hw, y - hh + 2*hh*frac])
    if side == 'right':
        return np.array([x + hw, y - hh + 2*hh*frac])

EDGE_STYLE = {
    'main':     {'color': '#1F2937', 'lw': 2.5, 'ls': '-'},
    'conf':     {'color': '#6E6E6E', 'lw': 1.1, 'ls': (0, (5, 3))},
    'key':      {'color': '#8E6815', 'lw': 1.6, 'ls': '-'},
    'mediator': {'color': '#4A6B53', 'lw': 1.4, 'ls': '-'},
    'time':     {'color': '#5F5278', 'lw': 1.1, 'ls': (0, (5, 3))},
}

HEAD_LEN = 0.20  # data units, length of the solid terminal segment

def draw_edge(frm, f_side, f_frac, to, t_side, t_frac, style_key, rad=0.0):
    """Shaft (dashed or solid) + always-solid filled head, landing exactly
    on its own anchor. Straight edges only (rad bends via quad Bezier)."""
    st = EDGE_STYLE[style_key]
    p0 = edge_point(frm, f_side, f_frac)
    p1 = edge_point(to, t_side, t_frac)
    v = p1 - p0
    L = np.linalg.norm(v)
    u = v / L
    if rad == 0.0:
        head_base = p1 - u * HEAD_LEN
        # shaft stops slightly inside the head so no gap, no overshoot
        ax.add_patch(FancyArrowPatch(
            posA=tuple(p0), posB=tuple(head_base + u * 0.02),
            arrowstyle='-', shrinkA=0, shrinkB=0,
            color=st['color'], linewidth=st['lw'], linestyle=st['ls'],
            capstyle='round', zorder=2))
        ax.add_patch(FancyArrowPatch(
            posA=tuple(head_base), posB=tuple(p1),
            arrowstyle='-|>', mutation_scale=15, shrinkA=0, shrinkB=0,
            color=st['color'], linewidth=st['lw'], linestyle='-',
            capstyle='round', joinstyle='round', zorder=2.5))
    else:
        # quadratic Bezier via control point offset perpendicular to chord
        n = np.array([-u[1], u[0]])
        c = (p0 + p1) / 2 + n * rad * L
        ts = np.linspace(0, 1, 60)
        pts = ((1-ts)**2)[:, None]*p0 + (2*ts*(1-ts))[:, None]*c + (ts**2)[:, None]*p1
        # trim the last HEAD_LEN of arc for the head
        d = np.cumsum(np.r_[0, np.linalg.norm(np.diff(pts, axis=0), axis=1)])
        cut = np.searchsorted(d, d[-1] - HEAD_LEN)
        ax.plot(pts[:cut+1, 0], pts[:cut+1, 1], color=st['color'],
                lw=st['lw'], ls=st['ls'], solid_capstyle='round', zorder=2)
        tang = pts[-1] - pts[cut]
        tang = tang / np.linalg.norm(tang)
        ax.add_patch(FancyArrowPatch(
            posA=tuple(pts[-1] - tang * HEAD_LEN), posB=tuple(pts[-1]),
            arrowstyle='-|>', mutation_scale=15, shrinkA=0, shrinkB=0,
            color=st['color'], linewidth=st['lw'], linestyle='-',
            capstyle='round', joinstyle='round', zorder=2.5))

# ── Edge table: (frm, side, frac, to, side, frac, style, rad) ──
# Anchors are spread so that every head has its own landing point and
# no path crosses a box.
E = [
    # main causal path (upper channel, clear of the ERG box)
    ('PSY', 'right', 0.72, 'MSD', 'left', 0.72, 'main', 0.0),
    # demographics -> PSY (distinct anchors on PSY top edge)
    ('SES', 'bottom', 0.35, 'PSY', 'top', 0.30, 'conf', 0.0),
    ('AGE', 'bottom', 0.25, 'PSY', 'top', 0.58, 'conf', 0.0),
    ('EMP', 'bottom', 0.15, 'PSY', 'top', 0.86, 'conf', 0.04),
    # demographics -> MSD (distinct anchors on MSD top edge)
    ('AGE', 'bottom', 0.75, 'MSD', 'top', 0.30, 'conf', 0.0),
    ('EMP', 'bottom', 0.65, 'MSD', 'top', 0.62, 'conf', 0.0),
    # long hours (bow below the ERG box)
    ('HRS', 'left',   0.70, 'PSY', 'bottom', 0.85, 'conf', 0.055),
    ('HRS', 'top',    0.50, 'MSD', 'bottom', 0.78, 'conf', 0.0),
    # industry (key confounder)
    ('IND', 'left',   0.60, 'PSY', 'bottom', 0.55, 'key', 0.0),
    ('IND', 'right',  0.60, 'MSD', 'bottom', 0.35, 'key', 0.0),
    ('IND', 'right',  0.85, 'EMP', 'bottom', 0.30, 'key', -0.05),
    ('IND', 'top',    0.50, 'ERG', 'bottom', 0.50, 'key', 0.0),
    # ergonomic mediator (directions as in the analysis notebook)
    ('ERG', 'left',   0.55, 'PSY', 'right', 0.18, 'mediator', 0.10),
    ('ERG', 'right',  0.55, 'MSD', 'left', 0.18, 'mediator', -0.10),
    # wave (secular time; bow below the ERG box)
    ('WAVE', 'top',   0.50, 'PSY', 'bottom', 0.25, 'time', 0.0),
    ('WAVE', 'right', 0.60, 'MSD', 'bottom', 0.10, 'time', -0.055),
]
def edge_path(frm, f_side, f_frac, to, t_side, t_frac, style_key, rad=0.0):
    p0 = edge_point(frm, f_side, f_frac)
    p1 = edge_point(to, t_side, t_frac)
    u = (p1 - p0) / np.linalg.norm(p1 - p0)
    n = np.array([-u[1], u[0]])
    c = (p0 + p1) / 2 + n * rad * np.linalg.norm(p1 - p0)
    ts = np.linspace(0, 1, 300)
    return ((1-ts)**2)[:, None]*p0 + (2*ts*(1-ts))[:, None]*c + (ts**2)[:, None]*p1

collisions = []
for e in E:
    pts = edge_path(*e)
    for key, (x, y, hw, hh) in box_geo.items():
        if key in (e[0], e[3]):
            continue
        inside = (np.abs(pts[:, 0] - x) < hw) & (np.abs(pts[:, 1] - y) < hh)
        if inside.any():
            collisions.append(f'{e[0]}->{e[3]} crosses {key}')
if collisions:
    print('!! BOX COLLISIONS:', collisions)
else:
    print('collision check: clean — no edge crosses any box')

for e in E:
    draw_edge(*e)

# ── Legend & caption (unchanged from v1) ──
legend_items = [
    mpatches.Patch(facecolor=PAL['exposure']['fill'], edgecolor=PAL['exposure']['edge'], linewidth=1.2, label='Exposure (JDC-S)'),
    mpatches.Patch(facecolor=PAL['outcome']['fill'], edgecolor=PAL['outcome']['edge'], linewidth=1.2, label='Outcome (MSD)'),
    mpatches.Patch(facecolor=PAL['mediator']['fill'], edgecolor=PAL['mediator']['edge'], linewidth=1.2, label='Ergonomic mediator'),
    mpatches.Patch(facecolor=PAL['key_conf']['fill'], edgecolor=PAL['key_conf']['edge'], linewidth=1.2, label='Industry (key confounder)'),
    mpatches.Patch(facecolor=PAL['confounder']['fill'], edgecolor=PAL['confounder']['edge'], linewidth=1.2, label='Demographic / time-varying covariate'),
    mpatches.Patch(facecolor=PAL['time']['fill'], edgecolor=PAL['time']['edge'], linewidth=1.2, label='Wave (secular time trend)'),
]
leg = fig.legend(handles=legend_items, loc='lower center',
                 bbox_to_anchor=(0.5, 0.045), ncol=3, fontsize=8.5,
                 framealpha=0.95, title='Minimal sufficient adjustment set',
                 title_fontsize=9, edgecolor='#888', borderpad=0.6,
                 columnspacing=1.4, handletextpad=0.6)
leg.get_frame().set_linewidth(0.7)

fig.text(0.5, 0.005,
         'Adjustment set: age, sex, education, employment type, industry, ergonomic '
         'exposures (4 items), long working hours, wave (time trend).  '
         'Industry is the principal confounder underlying the apparent autonomy paradox.',
         ha='center', va='bottom', fontsize=8, style='italic', color='#444', wrap=True)

fig.subplots_adjust(left=0.03, right=0.97, top=0.98, bottom=0.205)
fig.savefig(os.path.join(OUT, 'fig_dag_v2.png'), dpi=300, bbox_inches='tight')
fig.savefig(os.path.join(OUT, 'fig_dag_v2.pdf'), bbox_inches='tight')
print('saved fig_dag_v2.png / .pdf')
