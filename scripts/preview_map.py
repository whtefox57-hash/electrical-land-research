"""
Static PNG overview so there is something to look at without opening QGIS.
Not a substitute for outputs/screen.qgz — no basemap, no interactivity.
"""
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

GPKG = "outputs/tx_candidates.gpkg"

counties = gpd.read_file(GPKG, layer="counties")
lines = gpd.read_file(GPKG, layer="transmission_lines")
cand = gpd.read_file(GPKG, layer="candidates")

fig, ax = plt.subplots(figsize=(13, 13))
counties.boundary.plot(ax=ax, color="#bbbbbb", linewidth=0.4, zorder=1)

for lo, hi, color, lw, lbl in [
    (0, 138, "#d9d9d9", 0.3, "<138 kV"),
    (138, 230, "#f2b134", 0.5, "138-229 kV"),
    (230, 345, "#e8701a", 0.7, "230-344 kV"),
    (345, 1e6, "#c1121f", 1.0, "345 kV+"),
]:
    sel = lines[(lines["voltage_kv"] >= lo) & (lines["voltage_kv"] < hi)]
    if len(sel):
        sel.plot(ax=ax, color=color, linewidth=lw, zorder=2)

pop2 = cand[cand["population"] == 2]
pop2.plot(ax=ax, color="#5b8db8", markersize=1.5, alpha=0.35, zorder=3)

pop1 = cand[cand["population"] == 1].sort_values("score")
pop1.plot(ax=ax, column="score", cmap="YlOrRd", markersize=pop1["score"] * 1.5,
          edgecolor="black", linewidth=0.4, zorder=4, legend=True,
          legend_kwds={"label": "candidate score (0-100)", "shrink": 0.45})

top = cand.head(25)
for r in top.itertuples():
    ax.annotate(f"{r.rank}. {r.site_name}",
                (r.geometry.x, r.geometry.y),
                xytext=(5, 4), textcoords="offset points",
                fontsize=6.5, color="#111111", zorder=6)

handles = [
    Line2D([], [], color="#c1121f", lw=1.4, label="transmission 345 kV+"),
    Line2D([], [], color="#e8701a", lw=1.0, label="transmission 230-344 kV"),
    Line2D([], [], color="#f2b134", lw=0.8, label="transmission 138-229 kV"),
    Line2D([], [], marker="o", color="none", markerfacecolor="#5b8db8",
           markersize=4, label="Population 2 (proxy substation node)"),
    Line2D([], [], marker="o", color="none", markerfacecolor="#c1121f",
           markeredgecolor="black", markersize=8,
           label="Population 1 (retired/retiring plant)"),
]
ax.legend(handles=handles, loc="lower left", fontsize=8, framealpha=0.92)
ax.set_title("Texas powered-land screen — top 25 labelled\n"
             "Population 1 = EIA-860/860M retired or announced-retirement "
             "plants >= 50 MW; substations are a DERIVED proxy", fontsize=11)
ax.set_axis_off()
plt.tight_layout()
plt.savefig("outputs/preview_map.png", dpi=170, bbox_inches="tight")
print("wrote outputs/preview_map.png")
