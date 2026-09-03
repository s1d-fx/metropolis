"""Matplotlib user interface for viewing a 2D bin-packing result."""

from __future__ import annotations

from random import Random
from time import perf_counter

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle as RectanglePatch
from matplotlib.widgets import Button, RadioButtons, Slider

from bin_packing.algorithms.base import PackingAlgorithm
from bin_packing.generation import generate_rectangles
from bin_packing.models import Bin, PackingResult, Rectangle


class PackingVisualiser:
    """Render packing algorithms and expose controls for their input values.

    The visualiser owns widget callbacks and drawing only.  It calls the
    supplied algorithm through its small shared interface and draws its result.
    """

    def __init__(
        self,
        algorithms: dict[str, PackingAlgorithm],
        bin: Bin,
        rectangles: list[Rectangle],
    ) -> None:
        if not algorithms:
            raise ValueError("At least one packing algorithm is required.")

        self.algorithms = algorithms
        self.algorithm_name = next(iter(algorithms))
        self.bin = bin
        self.rectangles = rectangles
        self._random = Random()
        self._synchronising_dimension_sliders = False

        self.figure, (self.bin_axes, self.unpacked_axes) = plt.subplots(
            1, 2, figsize=(13, 9), gridspec_kw={"width_ratios": [3, 1]}
        )
        self.figure.subplots_adjust(bottom=0.46, wspace=0.35)
        self.figure.suptitle("2D Rectangular Bin Packing", fontsize=16)

        self.stats_text = self.figure.text(
            0.08, 0.43, "", family="monospace", va="top"
        )
        self._build_controls()
        self.redraw()

    @property
    def algorithm(self) -> PackingAlgorithm:
        """The currently selected algorithm instance."""
        return self.algorithms[self.algorithm_name]

    def _build_controls(self) -> None:
        """Create sliders once; callbacks redraw instead of rebuilding widgets."""
        slider_left, slider_width = 0.16, 0.56
        slider_positions = [0.35, 0.31, 0.27, 0.23, 0.19, 0.15, 0.11]
        slider_axes = [
            self.figure.add_axes((slider_left, y, slider_width, 0.025))
            for y in slider_positions
        ]

        self.width_slider = Slider(
            slider_axes[0], "Bin width", valmin=1, valmax=100,
            valinit=self.bin.width, valstep=1,
        )
        self.height_slider = Slider(
            slider_axes[1], "Bin height", valmin=1, valmax=100,
            valinit=self.bin.height, valstep=1,
        )
        self.count_slider = Slider(slider_axes[2], "Rectangle count", 1, 50, 20, valstep=1)
        self.min_width_slider = Slider(slider_axes[3], "Minimum width", 1, 50, 4, valstep=1)
        self.max_width_slider = Slider(slider_axes[4], "Maximum width", 1, 50, 18, valstep=1)
        self.min_height_slider = Slider(slider_axes[5], "Minimum height", 1, 50, 4, valstep=1)
        self.max_height_slider = Slider(slider_axes[6], "Maximum height", 1, 50, 18, valstep=1)

        self.width_slider.on_changed(self._on_bin_size_changed)
        self.height_slider.on_changed(self._on_bin_size_changed)
        for slider in (
            self.count_slider,
            self.min_width_slider,
            self.max_width_slider,
            self.min_height_slider,
            self.max_height_slider,
        ):
            slider.on_changed(self._on_rectangle_parameters_changed)

        button_axes = self.figure.add_axes((0.16, 0.035, 0.20, 0.045))
        self.regenerate_button = Button(button_axes, "Regenerate rectangles")
        self.regenerate_button.on_clicked(self._on_regenerate_clicked)

        algorithm_axes = self.figure.add_axes((0.52, 0.025, 0.25, 0.07))
        self.algorithm_selector = RadioButtons(
            algorithm_axes, list(self.algorithms), active=0, activecolor="tab:blue"
        )
        self.algorithm_selector.on_clicked(self._on_algorithm_changed)

    def _on_bin_size_changed(self, _: float) -> None:
        """Slider callbacks receive a value, but both controls define the bin."""
        self.bin = Bin(self.width_slider.val, self.height_slider.val)
        self.redraw()

    def _on_rectangle_parameters_changed(self, _: float) -> None:
        """Keep each dimension range valid, then make a fresh input set."""
        if self._synchronising_dimension_sliders:
            return

        self._synchronising_dimension_sliders = True
        if self.min_width_slider.val > self.max_width_slider.val:
            self.max_width_slider.set_val(self.min_width_slider.val)
        if self.min_height_slider.val > self.max_height_slider.val:
            self.max_height_slider.set_val(self.min_height_slider.val)
        self._synchronising_dimension_sliders = False
        self._regenerate_rectangles()

    def _on_regenerate_clicked(self, _: object) -> None:
        self._regenerate_rectangles()

    def _on_algorithm_changed(self, algorithm_name: str) -> None:
        self.algorithm_name = algorithm_name
        self.redraw()

    def _regenerate_rectangles(self) -> None:
        self.rectangles = generate_rectangles(
            count=int(self.count_slider.val),
            min_width=int(self.min_width_slider.val),
            max_width=int(self.max_width_slider.val),
            min_height=int(self.min_height_slider.val),
            max_height=int(self.max_height_slider.val),
            random_source=self._random,
        )
        self.redraw()

    def _run_algorithm(self) -> PackingResult:
        """Time an algorithm without making timing a responsibility of algorithms."""
        start = perf_counter()
        result = self.algorithm.pack(self.bin, self.rectangles)
        result.runtime_ms = (perf_counter() - start) * 1_000
        return result

    def redraw(self) -> None:
        """Obtain a fresh result and redraw every dynamic part of the window."""
        result = self._run_algorithm()
        self._draw_bin(result)
        self._draw_unpacked(result)
        self._draw_statistics(result)
        self.figure.canvas.draw_idle()

    def _draw_bin(self, result: PackingResult) -> None:
        axes = self.bin_axes
        axes.clear()
        axes.add_patch(
            RectanglePatch(
                (0, 0), self.bin.width, self.bin.height,
                fill=False, edgecolor="black", linewidth=2,
            )
        )

        for placement in result.placements:
            rectangle = placement.rectangle
            axes.add_patch(
                RectanglePatch(
                    (placement.x, placement.y), rectangle.width, rectangle.height,
                    facecolor="tab:blue", edgecolor="white", alpha=0.8,
                )
            )
            axes.text(
                placement.x + rectangle.width / 2,
                placement.y + rectangle.height / 2,
                str(rectangle.identifier),
                ha="center", va="center", color="white", fontsize=8,
            )

        padding = max(self.bin.width, self.bin.height) * 0.06
        axes.set_xlim(-padding, self.bin.width + padding)
        axes.set_ylim(-padding, self.bin.height + padding)
        axes.set_aspect("equal", adjustable="box")
        axes.set_title(f"Bin ({self.bin.width:g} × {self.bin.height:g})")
        axes.set_xlabel("width")
        axes.set_ylabel("height")
        axes.grid(True, alpha=0.2)

    def _draw_unpacked(self, result: PackingResult) -> None:
        axes = self.unpacked_axes
        axes.clear()
        axes.axis("off")
        axes.set_title(f"Unpacked ({len(result.unpacked)})")

        if result.unpacked:
            lines = [
                f"#{rectangle.identifier}: {rectangle.width:g} × {rectangle.height:g}"
                for rectangle in result.unpacked[:16]
            ]
            if len(result.unpacked) > 16:
                lines.append(f"… and {len(result.unpacked) - 16} more")
            axes.text(0, 1, "\n".join(lines), va="top", family="monospace")
        else:
            axes.text(0, 1, "All rectangles packed.", va="top")

    def _draw_statistics(self, result: PackingResult) -> None:
        input_area = sum(rectangle.area for rectangle in self.rectangles)
        self.stats_text.set_text(
            f"Algorithm: {self.algorithm.name}    "
            f"Rectangles: {len(self.rectangles)}    "
            f"Input area: {input_area:g}    "
            f"Packed: {len(result.placements)}    "
            f"Unpacked: {len(result.unpacked)}    "
            f"Utilisation: {result.utilisation(self.bin):.1%}    "
            f"Runtime: {result.runtime_ms:.3f} ms"
        )

    def show(self) -> None:
        """Hand control over to Matplotlib's GUI event loop."""
        plt.show()
