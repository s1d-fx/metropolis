"""Interactive runtime and utilisation experiments for First Feasible packing."""

from __future__ import annotations

from random import Random
from time import perf_counter

import matplotlib.pyplot as plt
from matplotlib.table import Table
from matplotlib.ticker import FuncFormatter
from matplotlib.widgets import Button, Slider

from disc_bin_packing.algorithms import FirstFeasibleAlgorithm
from disc_bin_packing.generation import generate_modules
from disc_bin_packing.models import MODULE_SIZES, GridBin


DEFAULT_WIDTH = 10
DEFAULT_HEIGHT = 8
DEFAULT_MODULE_COUNT = 40
DEFAULT_TRIALS = 10


class RuntimeExperiment:
    """Run and display repeated packing measurements on demand."""

    def __init__(self) -> None:
        self.algorithm = FirstFeasibleAlgorithm()
        self.scaling_figures: list[object] = []
        self.figure, self.results_axes = plt.subplots(figsize=(10, 7))
        self.figure.subplots_adjust(bottom=0.28, top=0.88)
        self.figure.suptitle("First Feasible Runtime Experiment", fontsize=16)

        self.width_slider = self._add_slider(
            (0.12, 0.20, 0.24, 0.03), "Grid width", 1, 40, DEFAULT_WIDTH
        )
        self.height_slider = self._add_slider(
            (0.12, 0.14, 0.24, 0.03), "Grid height", 1, 40, DEFAULT_HEIGHT
        )
        self.module_slider = self._add_slider(
            (0.56, 0.20, 0.24, 0.03),
            "Module count",
            1,
            120,
            DEFAULT_MODULE_COUNT,
        )
        self.trial_slider = self._add_slider(
            (0.56, 0.14, 0.24, 0.03),
            "Number of trials",
            1,
            30,
            DEFAULT_TRIALS,
        )

        util_axes = self.figure.add_axes((0.04, 0.045, 0.20, 0.055))
        self.util_scaling_button = Button(util_axes, "Generate util scaling")
        self.util_scaling_button.on_clicked(self._on_util_scaling_clicked)

        run_axes = self.figure.add_axes((0.28, 0.045, 0.20, 0.055))
        self.run_button = Button(run_axes, "Run experiment")
        self.run_button.on_clicked(self._on_run_clicked)

        runtime_axes = self.figure.add_axes((0.52, 0.045, 0.20, 0.055))
        self.runtime_scaling_button = Button(
            runtime_axes, "Generate runtime scaling"
        )
        self.runtime_scaling_button.on_clicked(self._on_runtime_scaling_clicked)

        packed_axes = self.figure.add_axes((0.76, 0.045, 0.20, 0.055))
        self.packed_scaling_button = Button(
            packed_axes, "Generate packed scaling"
        )
        self.packed_scaling_button.on_clicked(self._on_packed_scaling_clicked)

        self.table: Table | None = None
        self._show_empty_results()
        self.run_experiment()

    def _add_slider(
        self,
        position: tuple[float, float, float, float],
        label: str,
        minimum: int,
        maximum: int,
        initial: int,
    ) -> Slider:
        slider = Slider(
            self.figure.add_axes(position),
            label,
            minimum,
            maximum,
            valinit=initial,
            valstep=1,
        )
        return slider

    def _show_empty_results(self) -> None:
        self.results_axes.axis("off")
        self.results_axes.text(
            0.5,
            0.5,
            "Set experiment parameters, then click Run experiment.",
            ha="center",
            va="center",
        )

    def _on_run_clicked(self, _: object) -> None:
        self.run_experiment()

    def _on_runtime_scaling_clicked(self, _: object) -> None:
        self._show_scaling_plot("Average runtime (ms)", "Runtime scaling", "runtime")

    def _on_util_scaling_clicked(self, _: object) -> None:
        self._show_scaling_plot("Average utilisation", "Utilisation scaling", "utilisation")

    def _on_packed_scaling_clicked(self, _: object) -> None:
        self._show_scaling_plot(
            "Average modules packed (%)", "Modules packed scaling", "packed"
        )

    def _module_counts_for_scaling(self) -> list[int]:
        maximum = int(self.module_slider.valmax)
        counts = list(range(1, maximum + 1, 5))
        if counts[-1] != maximum:
            counts.append(maximum)
        return counts

    def _run_measurements(
        self, module_count: int, trial_count: int, random_source: Random
    ) -> tuple[float, float, float]:
        bin = GridBin(int(self.width_slider.val), int(self.height_slider.val))
        weights = {size: 1 for size in MODULE_SIZES}
        runtimes: list[float] = []
        utilisations: list[float] = []
        packed_percentages: list[float] = []

        for _ in range(trial_count):
            modules = generate_modules(
                module_count, weights, random_source=random_source
            )
            start = perf_counter()
            result = self.algorithm.pack(bin, modules)
            runtimes.append((perf_counter() - start) * 1_000)
            utilisations.append(result.utilisation(bin))
            packed_percentages.append(
                (len(modules) - len(result.unpacked)) / module_count
            )

        return (
            sum(runtimes) / trial_count,
            sum(utilisations) / trial_count,
            sum(packed_percentages) / trial_count,
        )

    def _show_scaling_plot(
        self, y_label: str, title: str, metric: str
    ) -> None:
        trial_count = int(self.trial_slider.val)
        module_counts = self._module_counts_for_scaling()
        random_source = Random()
        values: list[float] = []
        for module_count in module_counts:
            runtime, utilisation, packed = self._run_measurements(
                module_count, trial_count, random_source
            )
            values.append(
                {"runtime": runtime, "utilisation": utilisation, "packed": packed}[metric]
            )

        figure, axes = plt.subplots(figsize=(8, 5))
        axes.plot(module_counts, values, marker="o")
        axes.set_title(title)
        axes.set_xlabel("Module count")
        axes.set_ylabel(y_label)
        if metric in {"utilisation", "packed"}:
            axes.set_ylim(0, 1)
            axes.yaxis.set_major_formatter(
                FuncFormatter(lambda value, _: f"{value:.0%}")
            )
        axes.grid(True, alpha=0.3)
        figure.tight_layout()
        self.scaling_figures.append(figure)
        figure.canvas.mpl_connect(
            "close_event",
            lambda _: self.scaling_figures.remove(figure)
            if figure in self.scaling_figures
            else None,
        )
        figure.canvas.draw_idle()
        plt.show(block=False)

    def run_experiment(self) -> None:
        """Run all trials using the current slider values and refresh the table."""
        width = int(self.width_slider.val)
        height = int(self.height_slider.val)
        module_count = int(self.module_slider.val)
        trial_count = int(self.trial_slider.val)
        bin = GridBin(width, height)
        weights = {size: 1 for size in MODULE_SIZES}
        measurements: list[tuple[int, float, float, int]] = []
        random_source = Random()

        for trial in range(1, trial_count + 1):
            modules = generate_modules(
                module_count, weights, random_source=random_source
            )
            start = perf_counter()
            result = self.algorithm.pack(bin, modules)
            runtime_ms = (perf_counter() - start) * 1_000
            modules_packed = len(modules) - len(result.unpacked)
            measurements.append(
                (trial, runtime_ms, result.utilisation(bin), modules_packed)
            )

        average_runtime = sum(runtime for _, runtime, _, _ in measurements) / trial_count
        average_utilisation = (
            sum(utilisation for _, _, utilisation, _ in measurements) / trial_count
        )
        average_modules_packed = (
            sum(packed for _, _, _, packed in measurements) / trial_count
        )
        self._draw_results(
            measurements,
            average_runtime,
            average_utilisation,
            average_modules_packed,
            width,
            height,
            module_count,
        )

    def _draw_results(
        self,
        measurements: list[tuple[int, float, float, int]],
        average_runtime: float,
        average_utilisation: float,
        average_modules_packed: float,
        width: int,
        height: int,
        module_count: int,
    ) -> None:
        self.results_axes.clear()
        self.results_axes.axis("off")
        self.results_axes.set_title(
            f"{width} × {height} grid | {module_count} modules | "
            f"{len(measurements)} trials",
            pad=12,
        )
        table_data = [["Trial", "Runtime (ms)", "Utilisation", "Modules packed"]]
        table_data.extend(
            [
                str(trial),
                f"{runtime_ms:.4f}",
                f"{utilisation:.2%}",
                f"{modules_packed} / {module_count} ({modules_packed / module_count:.1%})",
            ]
            for trial, runtime_ms, utilisation, modules_packed in measurements
        )
        table_data.extend(
            [
                [
                    "Average",
                    f"{average_runtime:.4f}",
                    f"{average_utilisation:.2%}",
                    f"{average_modules_packed:.1f} / {module_count} "
                    f"({average_modules_packed / module_count:.1%})",
                ],
            ]
        )
        self.table = self.results_axes.table(
            cellText=table_data,
            loc="center",
            cellLoc="center",
            colWidths=[0.14, 0.27, 0.27, 0.32],
            bbox=(0.08, 0.02, 0.84, 0.98),
        )
        self.table.auto_set_font_size(False)
        row_count = len(table_data)
        self.table.set_fontsize(max(6, min(9, 235 / row_count)))
        for column in range(4):
            self.table[(0, column)].set_facecolor("#d9eaf7")
            self.table[(len(table_data) - 1, column)].set_facecolor("#e8f3e8")
        self.figure.canvas.draw_idle()

    def show(self) -> None:
        """Display the experiment controls and latest results."""
        plt.show()


def main() -> None:
    RuntimeExperiment().show()


if __name__ == "__main__":
    main()
