"""Render a discrete module-packing run as a 120-frame MP4 animation."""

from __future__ import annotations

import argparse
from shutil import which
from pathlib import Path
from random import Random

import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle as RectanglePatch

from disc_bin_packing.algorithms import FirstFeasibleAlgorithm
from disc_bin_packing.generation import generate_modules
from disc_bin_packing.models import MODULE_SIZES, GridBin, GridPackingResult

FRAME_COUNT = 120
FPS = 30
FILLER_COLOUR = "#f2c14e"
DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent
    / "disc_bin_packing"
    / "algorithms"
    / "grid_packing.mp4"
)


def _draw_frame(
    axes: plt.Axes,
    result: GridPackingResult,
    bin: GridBin,
    visible_placements: int,
) -> None:
    axes.clear()
    axes.add_patch(
        RectanglePatch(
            (0, 0), bin.width, bin.height,
            facecolor="0.88", edgecolor="none", zorder=0,
        )
    )

    colours = plt.get_cmap("tab10")
    patches: list[RectanglePatch] = []
    for placement in result.placements[:visible_placements]:
        module = placement.module
        colour = FILLER_COLOUR if module.is_filler else colours(module.identifier % 10)
        patches.append(
            RectanglePatch(
                (placement.x, placement.y), module.width, module.height,
                facecolor=colour, edgecolor="white", linewidth=1.2, zorder=1,
            )
        )
        if not module.is_filler:
            axes.text(
                placement.x + module.width / 2,
                placement.y + module.height / 2,
                str(module.identifier),
                ha="center", va="center", fontsize=8, zorder=2,
            )

    if patches:
        axes.add_collection(PatchCollection(patches, match_original=True))

    axes.set_xlim(0, bin.width)
    axes.set_ylim(0, bin.height)
    axes.set_aspect("equal", adjustable="box")
    axes.set_xticks(range(bin.width + 1))
    axes.set_yticks(range(bin.height + 1))
    axes.grid(color="0.65", linewidth=0.7)
    axes.set_xlabel("x cell")
    axes.set_ylabel("y cell")
    axes.set_title(
        f"Discrete module packing: {visible_placements}/"
        f"{len(result.placements)} placements"
    )


def create_animation(
    output_path: Path,
    *,
    width: int = 10, ####################### GRID WIDTH
    height: int = 8, ####################### GRID HEIGHT
    module_count: int = 40, ############### NUMBER OF MODULES
    seed: int | None = None,
) -> None:
    """Pack modules and write exactly 120 frames to ``output_path``."""
    if which("ffmpeg") is None:
        raise RuntimeError(
            "MP4 output requires FFmpeg. Install it with "
            "`brew install ffmpeg` and run this script again."
        )

    modules = generate_modules(
        count=module_count,
        weights={size: 1 for size in MODULE_SIZES},
        random_source=Random(seed),
    )
    result = FirstFeasibleAlgorithm().pack(GridBin(width, height), modules)
    bin = GridBin(width, height)

    figure, axes = plt.subplots(figsize=(8, 7))
    figure.tight_layout()

    def update(frame: int) -> None:
        if not result.placements:
            visible = 0
        else:
            visible = min(
                len(result.placements),
                max(1, (frame + 1) * len(result.placements) // FRAME_COUNT),
            )
        _draw_frame(axes, result, bin, visible)

    animation = FuncAnimation(
        figure,
        update,
        frames=FRAME_COUNT,
        interval=1_000 / FPS,
        repeat=False,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    animation.save(output_path, writer=FFMpegWriter(fps=FPS), dpi=120)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o", "--output", type=Path, default=DEFAULT_OUTPUT,
        help=f"Output MP4 path (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument("--width", type=int, default=10, help="Grid width (default: 10).")
    parser.add_argument("--height", type=int, default=8, help="Grid height (default: 8).")
    parser.add_argument("--modules", type=int, default=40, dest="module_count", help="Number of modules (default: 40).")
    parser.add_argument("--seed", type=int, default=None, help="Random seed (default: None).")
    args = parser.parse_args()
    create_animation(
        args.output,
        width=args.width,
        height=args.height,
        module_count=args.module_count,
        seed=args.seed,
    )
    print(f"Wrote {FRAME_COUNT} frames at {FPS} fps to {args.output}")


if __name__ == "__main__":
    main()
