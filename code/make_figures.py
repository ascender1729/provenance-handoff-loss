"""Build the three paper figures (p1_arch, p2_perhop, p3_armdepth) from results.json.

Usage (from the repository root):
    python code/make_figures.py      # writes figures/p1_arch.{pdf,png} etc.
"""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

plt.rcParams.update({
    "font.family": "serif", "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8.5,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "figure.dpi": 220, "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.8,
})
BLUE, ORANGE, GREEN, PINK, RED, GREY, DARK = \
    "#0072B2", "#E69F00", "#009E73", "#CC79A7", "#D55E00", "#8C8C8C", "#222222"

LBL = {"anthropic_haiku45": "Claude Haiku 4.5", "meta_llama33_70b": "Llama 3.3 70B",
       "amazon_nova_pro": "Nova Pro", "mistral_pixtral_lg": "Pixtral Large"}
COL = {"anthropic_haiku45": BLUE, "meta_llama33_70b": ORANGE,
       "amazon_nova_pro": GREEN, "mistral_pixtral_lg": PINK}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figures")
os.makedirs(FIG, exist_ok=True)
r = json.load(open(os.path.join(ROOT, "results.json"), encoding="utf-8"))


def save(fig, stem):
    fig.savefig(os.path.join(FIG, stem + ".pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(FIG, stem + ".png"), bbox_inches="tight")

# ============ FIGURE 1: two-layer architecture ============
fig, ax = plt.subplots(figsize=(6.6, 2.45))
ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(-6, 56)

xs = [9, 35, 61, 87]
names = ["principal\nP", "agent 1", "agent 2", "agent 3"]

# --- token layer band: nodes 38, arrow labels 44, title above at 51 ---
ax.add_patch(Rectangle((2, 31), 96, 17, fc="#EAF3FA", ec="none", zorder=0))
ax.text(2, 50.5, "token layer: signed delegation chain (UCAN, ZCAP-LD, RFC 8693)",
        fontsize=6.9, color=BLUE, va="bottom", ha="left")

# --- model layer band: nodes 12, arrow labels 18, title above at 25 ---
ax.add_patch(Rectangle((2, 5), 96, 17, fc="#FDF1E6", ec="none", zorder=0))
ax.text(2, 24.5, "model layer: the handoff message the model composes",
        fontsize=6.9, color=RED, va="bottom", ha="left")

for x, nm in zip(xs, names):
    for y, col in ((38.0, BLUE), (12.0, RED)):
        ax.text(x, y, nm, ha="center", va="center", fontsize=6.8, color=col, zorder=3,
                bbox=dict(boxstyle="round,pad=0.26", fc="white", ec=col, lw=0.8))

for i in range(3):
    xa, xb = xs[i] + 7.5, xs[i + 1] - 7.5
    mid = (xs[i] + xs[i + 1]) / 2
    ax.add_patch(FancyArrowPatch((xa, 38.0), (xb, 38.0), arrowstyle="-|>",
                                 mutation_scale=7, lw=0.9, color=BLUE, zorder=2))
    ax.text(mid, 43.4, "signed act chain", ha="center", fontsize=5.9, color=BLUE)
    ax.add_patch(FancyArrowPatch((xa, 12.0), (xb, 12.0), arrowstyle="-|>",
                                 mutation_scale=7, lw=0.9, color=RED, zorder=2))
    ax.text(mid, 17.4, "prose handoff", ha="center", fontsize=5.9, color=RED)

ax.text(50, -4.0, "identity is verifiable by construction on the top row, and is whatever the "
                  "model chose to write on the bottom row",
        fontsize=6.4, color=GREY, ha="center", style="italic")
save(fig, "p1_arch")
plt.close(fig); print("wrote p1_arch")

# ============ FIGURE 2: per-hop survival, control ============
fig, ax = plt.subplots(figsize=(3.6, 2.9))
for k, v in r["per_hop_survival_depth5"].items():
    if v["arm"] != "control" or v["family"] not in COL:
        continue
    hops = [h["hop"] for h in v["hops"]]
    rates = [100 * h["full_rate"] for h in v["hops"]]
    ax.plot(hops, rates, marker="o", ms=3.2, lw=1.3, color=COL[v["family"]],
            label=LBL[v["family"]], zorder=3)
# pooled line, visually distinct
tot = {}
for v in r["per_hop_survival_depth5"].values():
    if v["arm"] != "control" or v["family"] not in COL:
        continue
    for h in v["hops"]:
        a, b = tot.get(h["hop"], (0, 0))
        tot[h["hop"]] = (a + h["full"], b + v["n"])
hops = sorted(tot)
ax.plot(hops, [100 * tot[h][0] / tot[h][1] for h in hops], color=DARK, lw=1.6,
        ls=(0, (4, 2)), marker="s", ms=3.4, label="all families", zorder=4)
ax.set_xlabel("delegation hop")
ax.set_ylabel("full provenance retained (percent)")
ax.set_xticks([1, 2, 3, 4, 5]); ax.set_ylim(0, 105)
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=2,
          handlelength=1.6, columnspacing=1.3, borderpad=0.0)
save(fig, "p2_perhop")
plt.close(fig); print("wrote p2_perhop")

# ============ FIGURE 3: arm by depth ============
fig, ax = plt.subplots(figsize=(3.3, 2.9))
for arm, col, mk in (("control", RED, "o"), ("clause", BLUE, "s")):
    ds = [1, 3, 5]
    ys = [100 * r["pooled_arm_by_depth"]["%s|d%d" % (arm, d)]["prog_full_rate"] for d in ds]
    lo = [100 * r["pooled_arm_by_depth"]["%s|d%d" % (arm, d)]["prog_full_ci95"][0] for d in ds]
    hi = [100 * r["pooled_arm_by_depth"]["%s|d%d" % (arm, d)]["prog_full_ci95"][1] for d in ds]
    ax.plot(ds, ys, marker=mk, ms=4, lw=1.5, color=col, label=arm, zorder=3)
    ax.fill_between(ds, lo, hi, color=col, alpha=0.16, lw=0, zorder=1)
ax.set_xlabel("delegation depth")
ax.set_ylabel("full provenance (percent)")
ax.set_xticks([1, 3, 5]); ax.set_ylim(0, 105)
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=2,
          handlelength=1.6, columnspacing=1.6, borderpad=0.0)
save(fig, "p3_armdepth")
plt.close(fig); print("wrote p3_armdepth")
