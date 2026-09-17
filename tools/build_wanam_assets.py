"""Create portfolio figures from the Wanam project files.

Run with:
    python tools/build_wanam_assets.py "<Wanam project root>" assets

The source files stay outside the website repository. Only the two SVG figures
are written to the requested output directory.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


INK = "#10213d"
SEA = "#0c5e7d"
SOFT = "#52627a"
GRID = "#d7dbe0"
PALETTE = ["#0c5e7d", "#d08729", "#66862a", "#98456d", "#5260a0"]
LINE_STYLES = ["solid", "dashed", "dashdot", "dotted", (0, (6, 2, 1, 2))]


def basin_paths(model_root: Path) -> dict[int, Path]:
    return {
        1: model_root / "SHP Outlet 1" / "Subbasin.shp",
        2: model_root / "Outlet 2" / "SHP DAS Outlet 2" / "Subbasin.shp",
        3: model_root / "Outlet 3" / "SHP DAS Outlet 3" / "Subbasin.shp",
        4: model_root / "Outlet 4" / "SHP DAS Outlet 4" / "Subbasin.shp",
        5: model_root / "Outlet 5" / "SHP DAS Outlet 5" / "Subbasin.shp",
    }


def basin_model_paths(model_root: Path) -> dict[int, Path]:
    return {
        1: model_root / "Outlet 1" / "Outlet_1" / "Basin_1.basin",
        2: model_root / "Outlet 2" / "Model Outlet 2" / "Outlet_2" / "Basin_1.basin",
        3: model_root / "Outlet 3" / "Model Outlet 3" / "Outlet_3" / "Basin_1.basin",
        4: model_root / "Outlet 4" / "Model Outlet 4" / "Outlet_4" / "Basin_1.basin",
        5: model_root / "Outlet 5" / "Model Outlet 5" / "Outlet_5" / "Basin_1.basin",
    }


def sink_xy(model_file: Path) -> tuple[float, float]:
    text = model_file.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"Sink: Sink-1\s*(.*?)\s*End:", text, re.S)
    if match is None:
        raise ValueError(f"Sink-1 tidak ditemukan: {model_file}")
    x = re.search(r"Canvas X:\s*([0-9.]+)", match.group(1))
    y = re.search(r"Canvas Y:\s*([0-9.]+)", match.group(1))
    if x is None or y is None:
        raise ValueError(f"Koordinat Sink-1 tidak lengkap: {model_file}")
    return float(x.group(1)), float(y.group(1))


def draw_map(model_root: Path, output: Path) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})
    fig, ax = plt.subplots(figsize=(12, 8), dpi=160)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f7fafb")

    extents: list[np.ndarray] = []
    for number, shp in basin_paths(model_root).items():
        basin = gpd.read_file(shp)
        if str(basin.crs) != "EPSG:32754":
            raise ValueError(f"CRS tidak sesuai UTM 54S: {shp}: {basin.crs}")
        basin.plot(ax=ax, facecolor=PALETTE[number - 1], edgecolor=INK, alpha=0.22, linewidth=1.5)
        basin.boundary.plot(ax=ax, color=PALETTE[number - 1], linewidth=2.0)
        extents.append(basin.total_bounds)

    for number, basin_file in basin_model_paths(model_root).items():
        x, y = sink_xy(basin_file)
        ax.scatter([x], [y], s=125, facecolor="#ffffff", edgecolor=INK, linewidth=1.7, zorder=7)
        ax.annotate(
            str(number), (x, y), ha="center", va="center", color=INK,
            fontsize=10, fontweight="bold", zorder=8,
        )

    extent = np.array(extents)
    xmin, ymin = extent[:, :2].min(axis=0)
    xmax, ymax = extent[:, 2:].max(axis=0)
    padx = (xmax - xmin) * 0.07
    pady = (ymax - ymin) * 0.07
    ax.set_xlim(xmin - padx, xmax + padx)
    ax.set_ylim(ymin - pady, ymax + pady)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(color=GRID, linewidth=0.6, alpha=0.7)
    ax.tick_params(axis="both", labelsize=9, colors=SOFT)
    ax.ticklabel_format(style="plain", useOffset=False)
    ax.set_xlabel("Easting UTM 54S (m)", fontsize=10, color=SOFT, labelpad=10)
    ax.set_ylabel("Northing UTM 54S (m)", fontsize=10, color=SOFT, labelpad=10)
    ax.set_title("Lima DAS dan outlet model — Wanam, Papua", loc="left", fontsize=18, color=INK, pad=19)
    ax.text(
        0.0, 1.015, "Poligon DAS dari analisis GIS; angka menandai outlet komputasi HEC-HMS",
        transform=ax.transAxes, ha="left", va="bottom", fontsize=10, color=SOFT,
    )
    ax.annotate("N", xy=(0.955, 0.92), xytext=(0.955, 0.82), xycoords="axes fraction",
                ha="center", va="center", arrowprops={"arrowstyle": "-|>", "color": INK, "lw": 1.6},
                fontsize=11, color=INK, fontweight="bold")
    for spine in ax.spines.values():
        spine.set_color(GRID)
    fig.tight_layout(pad=1.6)
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def discharge_path(model_root: Path, number: int) -> Path:
    if number == 1:
        return model_root / "Hasil Outlet 1" / "+ Baseflow rdf" / "Discharge_Outlet 1.csv"
    return (
        model_root / f"Outlet {number}" / f"Hasil Outlet {number}"
        / "+ Baseflow RDF" / f"Discharge_Outlet {number}.csv"
    )


def draw_fdc(model_root: Path, output: Path) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})
    fig, ax = plt.subplots(figsize=(12, 6.6), dpi=160)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    for number in range(1, 6):
        df = pd.read_csv(discharge_path(model_root, number))
        flows = pd.to_numeric(df["Total Inflow (M3/S) + Baseflow"], errors="raise").to_numpy(float)
        if len(flows) != 4017 or not np.isfinite(flows).all() or np.any(flows <= 0):
            raise ValueError(f"Seri Outlet {number} tidak sesuai dengan keluaran 2013–2023")
        ordered = np.sort(flows)[::-1]
        exceedance = np.arange(1, len(ordered) + 1) / (len(ordered) + 1) * 100
        q80 = float(np.quantile(flows, 0.2, method="linear"))
        ax.plot(
            exceedance, ordered, color=PALETTE[number - 1],
            linestyle=LINE_STYLES[number - 1], linewidth=2.2,
            label=f"Outlet {number}  ·  Q80 {q80:.2f} m³/s",
        )
        ax.scatter([80], [q80], s=45, facecolor="#ffffff",
                   edgecolor=PALETTE[number - 1], linewidth=1.8, zorder=6)

    ax.axvline(80, color=SOFT, linewidth=1, linestyle=(0, (3, 4)), alpha=0.8)
    ax.set_yscale("log")
    ax.set_xlim(0, 100)
    ax.set_ylim(0.2, 170)
    ax.set_xticks(np.arange(0, 101, 20))
    ax.set_yticks([0.3, 1, 3, 10, 30, 100], ["0,3", "1", "3", "10", "30", "100"])
    ax.grid(which="major", color=GRID, linewidth=0.8)
    ax.grid(which="minor", visible=False)
    ax.tick_params(axis="both", labelsize=10, colors=SOFT, length=0, pad=7)
    ax.set_xlabel("Peluang terlampaui (%)", fontsize=11, color=INK, labelpad=12)
    ax.set_ylabel("Debit skenario (m³/s) · skala log", fontsize=11, color=INK, labelpad=12)
    ax.set_title("Kurva durasi aliran dan estimasi Q80", loc="left", fontsize=18, color=INK, pad=24)
    ax.text(0, 1.02, "Lima outlet · 4.017 nilai harian per outlet · seri model 2013–2023",
            transform=ax.transAxes, ha="left", va="bottom", fontsize=10, color=SOFT)
    ax.legend(loc="upper right", frameon=True, facecolor="#ffffff", edgecolor=GRID,
              fontsize=9.5, labelspacing=0.8, handlelength=3.4)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    fig.tight_layout(pad=1.6)
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("wanam_root", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    model_root = args.wanam_root / "[2] MODEL" / "Revisi"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    draw_map(model_root, args.output_dir / "wanam-five-outlets-map.svg")
    draw_fdc(model_root, args.output_dir / "wanam-five-outlets-fdc.svg")


if __name__ == "__main__":
    main()
