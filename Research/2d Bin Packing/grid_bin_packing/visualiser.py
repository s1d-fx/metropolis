"""Matplotlib controls and rendering for discrete-grid packing experiments."""

from __future__ import annotations

from math import ceil
from random import Random
from time import perf_counter

import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle as RectanglePatch
from matplotlib.widgets import Button, RadioButtons, Slider, TextBox

from grid_bin_packing.algorithms.base import GridPackingAlgorithm
from grid_bin_packing.generation import generate_modules
from grid_bin_packing.models import (
    MODULE_SIZES,
    GridBin,
    GridPackingResult,
    Module,
    ModuleSize,
)


class GridPackingVisualiser:
    """Render a discrete packing result without embedding algorithm logic.

    The algorithm is run once per input change.  Step controls then reveal its
    placements incrementally from that fixed result, which makes the process
    inspectable without mutating or rerunning the packing algorithm.
    """

    def __init__(
        self,
        algorithms: dict[str, GridPackingAlgorithm],
        bin: GridBin,
        modules: list[Module],
    ) -> None:
        if not algorithms:
            raise ValueError("At least one grid packing algorithm is required.")

        self.algorithms = algorithms
        self.algorithm_name = next(iter(algorithms))
        self.bin = bin
        self.modules = modules
        self.result = GridPackingResult()
        self.visible_placements = 0
        self._random = Random()
        self._updating_weights = False
        colours = plt.get_cmap("tab10")
        self.module_colours = {
            size: colours(index / max(1, len(MODULE_SIZES) - 1))
            for index, size in enumerate(MODULE_SIZES)
        }

        self.figure, (self.bin_axes, self.unpacked_axes) = plt.subplots(
            1, 2, figsize=(16, 8), gridspec_kw={"width_ratios": [3.5, 1]}
        )
        self.figure.subplots_adjust(bottom=0.50, wspace=0.30)
        self.figure.suptitle("Discrete Grid Module Packing", fontsize=16)
        self.figure.legend(
            handles=[
                Patch(facecolor=self.module_colours[size], label=f"{size[0]}×{size[1]}")
                for size in MODULE_SIZES
            ],
            title="Module size",
            loc="upper left",
            bbox_to_anchor=(0.68, 0.75),
            fontsize=8,
            title_fontsize=9,
            frameon=True,
            borderpad=0.6,
        )
        self.stats_text = self.figure.text(
            0.68,
            0.52,
            "",
            family="monospace",
            fontsize=9,
            va="top",
            linespacing=1.35,
            bbox={
                "boxstyle": "round,pad=0.6",
                "facecolor": "white",
                "edgecolor": "0.75",
                "alpha": 0.95,
            },
        )
        self.step_text = self.figure.text(
            0.88,
            0.33,
            "",
            fontsize=9,
            va="top",
            bbox={
                "boxstyle": "round,pad=0.5",
                "facecolor": "white",
                "edgecolor": "0.75",
                "alpha": 0.95,
            },
        )

        self._build_controls()
        self.redraw(reset_step=True)

    @property
    def algorithm(self) -> GridPackingAlgorithm:
        return self.algorithms[self.algorithm_name]

    def _build_controls(self) -> None:
        slider_left, slider_width = 0.16, 0.40
        slider_positions = [0.405, 0.365, 0.325]
        self._numeric_inputs: list[tuple[Slider, TextBox]] = []
        self.width_slider = Slider(
            self.figure.add_axes((slider_left, 0.405, slider_width, 0.025)),
            "Grid width", 1, 40, self.bin.width, valstep=1,
        )
        self.height_slider = Slider(
            self.figure.add_axes((slider_left, 0.365, slider_width, 0.025)),
            "Grid height", 1, 40, self.bin.height, valstep=1,
        )
        self.count_slider = Slider(
            self.figure.add_axes((slider_left, 0.325, slider_width, 0.025)),
            "Module count", 1, 120, len(self.modules), valstep=1,
        )
        self.width_slider.on_changed(self._on_bin_size_changed)
        self.height_slider.on_changed(self._on_bin_size_changed)
        self.count_slider.on_changed(self._on_generation_changed)
        for slider, y in (
            (self.width_slider, 0.405),
            (self.height_slider, 0.365),
            (self.count_slider, 0.325),
        ):
            self._add_numeric_input(slider, slider_left + slider_width + 0.01, y, 0.055)

        self.weight_sliders: dict[ModuleSize, Slider] = {}
        for index, size in enumerate(MODULE_SIZES):
            column = index // 4
            row = index % 4
            left = 0.16 if column == 0 else 0.58
            axes = self.figure.add_axes((left, 0.275 - row * 0.045, 0.16, 0.022))
            width, height = size
            slider = Slider(axes, f"{width}×{height} weight", 0, 10, 1, valstep=1)
            slider.on_changed(self._on_generation_changed)
            self.weight_sliders[size] = slider
            self._add_numeric_input(slider, left + 0.17, 0.275 - row * 0.045, 0.055)

        regenerate_axes = self.figure.add_axes((0.16, 0.035, 0.20, 0.045))
        self.regenerate_button = Button(regenerate_axes, "Regenerate modules")
        self.regenerate_button.on_clicked(self._on_regenerate_clicked)

        previous_axes = self.figure.add_axes((0.40, 0.035, 0.13, 0.045))
        next_axes = self.figure.add_axes((0.55, 0.035, 0.13, 0.045))
        all_axes = self.figure.add_axes((0.70, 0.035, 0.13, 0.045))
        self.previous_button = Button(previous_axes, "Previous")
        self.next_button = Button(next_axes, "Next")
        self.show_all_button = Button(all_axes, "Show all")
        self.previous_button.on_clicked(self._on_previous_clicked)
        self.next_button.on_clicked(self._on_next_clicked)
        self.show_all_button.on_clicked(self._on_show_all_clicked)

        algorithm_axes = self.figure.add_axes((0.85, 0.14, 0.13, 0.08))
        self.algorithm_selector = RadioButtons(
            algorithm_axes, list(self.algorithms), active=0, activecolor="tab:blue"
        )
        self.algorithm_selector.on_clicked(self._on_algorithm_changed)

    def _add_numeric_input(
        self, slider: Slider, left: float, bottom: float, width: float
    ) -> None:
        slider.valtext.set_visible(False)
        text_box = TextBox(
            self.figure.add_axes((left, bottom, width, 0.025)),
            "",
            initial=str(int(slider.val)),
            textalignment="center",
        )
        text_box.on_submit(
            lambda text, target=slider, field=text_box:
            self._on_numeric_input_submitted(target, field, text)
        )
        slider.on_changed(
            lambda value, field=text_box: field.set_val(str(int(value)))
        )
        self._numeric_inputs.append((slider, text_box))

    def _on_numeric_input_submitted(
        self, slider: Slider, text_box: TextBox, text: str
    ) -> None:
        try:
            value = int(text.strip())
        except ValueError:
            text_box.set_val(str(int(slider.val)))
            return

        value = max(int(slider.valmin), min(int(slider.valmax), value))
        slider.set_val(value)

    def _on_bin_size_changed(self, _: float) -> None:
        self.bin = GridBin(int(self.width_slider.val), int(self.height_slider.val))
        self.redraw(reset_step=True)

    def _on_generation_changed(self, _: float) -> None:
        if self._updating_weights:
            return
        self._updating_weights = True
        if not any(slider.val for slider in self.weight_sliders.values()):
            self.weight_sliders[MODULE_SIZES[0]].set_val(1)
        self._updating_weights = False
        self._regenerate_modules()

    def _on_regenerate_clicked(self, _: object) -> None:
        self._regenerate_modules()

    def _on_algorithm_changed(self, algorithm_name: str) -> None:
        self.algorithm_name = algorithm_name
        self.redraw(reset_step=True)

    def _on_previous_clicked(self, _: object) -> None:
        self.visible_placements = max(0, self.visible_placements - 1)
        self._draw_current_result()

    def _on_next_clicked(self, _: object) -> None:
        self.visible_placements = min(len(self.result.placements), self.visible_placements + 1)
        self._draw_current_result()

    def _on_show_all_clicked(self, _: object) -> None:
        self.visible_placements = len(self.result.placements)
        self._draw_current_result()

    def _regenerate_modules(self) -> None:
        weights = {size: int(slider.val) for size, slider in self.weight_sliders.items()}
        self.modules = generate_modules(
            count=int(self.count_slider.val), weights=weights, random_source=self._random
        )
        self.redraw(reset_step=True)

    def _run_algorithm(self) -> GridPackingResult:
        start = perf_counter()
        result = self.algorithm.pack(self.bin, self.modules)
        result.runtime_ms = (perf_counter() - start) * 1_000
        return result

    def redraw(self, *, reset_step: bool) -> None:
        self.result = self._run_algorithm()
        if reset_step:
            self.visible_placements = len(self.result.placements)
        self._draw_current_result()

    def _draw_current_result(self) -> None:
        self._draw_bin()
        self._draw_unpacked()
        self._draw_statistics()
        self.figure.canvas.draw_idle()

    def _draw_bin(self) -> None:
        axes = self.bin_axes
        axes.clear()

        for placement in self.result.placements[: self.visible_placements]:
            module = placement.module
            colour = "0.85" if module.is_filler else self.module_colours[module.size]
            axes.add_patch(
                RectanglePatch(
                    (placement.x, placement.y), module.width, module.height,
                    facecolor=colour, edgecolor="white", linewidth=1.2,
                )
            )
            if not module.is_filler:
                axes.text(
                    placement.x + module.width / 2,
                    placement.y + module.height / 2,
                    str(module.identifier), ha="center", va="center", fontsize=8,
                )

        tick_step = max(1, ceil(max(self.bin.width, self.bin.height) / 20))
        x_cells = list(range(self.bin.width + 1))
        y_cells = list(range(self.bin.height + 1))
        axes.set_xticks(x_cells)
        axes.set_yticks(y_cells)
        axes.set_xticklabels([str(cell) if cell % tick_step == 0 else "" for cell in x_cells])
        axes.set_yticklabels([str(cell) if cell % tick_step == 0 else "" for cell in y_cells])
        # Major ticks deliberately occur at every boundary: the grid is one cell wide.
        axes.grid(which="major", color="0.65", linewidth=0.7)
        axes.set_xlim(0, self.bin.width)
        axes.set_ylim(0, self.bin.height)
        axes.set_aspect("equal", adjustable="box")
        axes.set_title(f"Grid bin ({self.bin.width} × {self.bin.height} cells)")
        axes.set_xlabel("x cell")
        axes.set_ylabel("y cell")

    def _draw_unpacked(self) -> None:
        axes = self.unpacked_axes
        axes.clear()
        axes.axis("off")
        axes.set_title(f"Unpacked ({len(self.result.unpacked)})")
        if not self.result.unpacked:
            axes.text(0, 1, "All modules packed.", va="top")
            return

        lines = [
            f"#{module.identifier}: {module.width}×{module.height}"
            for module in self.result.unpacked[:8]
        ]
        if len(self.result.unpacked) > 8:
            lines.append(f"… and {len(self.result.unpacked) - 8} more")
        axes.text(0, 1, "\n".join(lines), va="top", family="monospace")

    def _draw_statistics(self) -> None:
        requested_cells = sum(module.cell_count for module in self.modules)
        utilisation = self.result.utilisation(self.bin)

        self.stats_text.set_text(
            "\n".join(
                (
                    f"Algorithm:       {self.algorithm.name}",
                    f"Modules:         {len(self.modules)}",
                    f"Requested cells: {requested_cells}",
                    f"Module cells:    {self.result.requested_module_cells}",
                    f"1×1 fillers:     {self.result.filler_cells}",
                    f"Occupied cells:  {self.result.occupied_cells}/{self.bin.cell_count}",
                    f"Utilisation:     {utilisation:.1%}",
                    f"Runtime:          {self.result.runtime_ms:.3f} ms",
                )
            )
        )
        self.step_text.set_text(
            f"Showing placements:\n"
            f"{self.visible_placements}/{len(self.result.placements)}"
        )

    def show(self) -> None:
        """Hand control over to Matplotlib's GUI event loop."""
        plt.show()
