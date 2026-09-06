"""Interactive runtime and utilisation experiments for discrete packing algorithms."""

from __future__ import annotations

import argparse
from random import Random
from pathlib import Path
from statistics import fmean, stdev
from time import perf_counter

import matplotlib.pyplot as plt
from matplotlib.table import Table
from matplotlib.ticker import FuncFormatter
from matplotlib.widgets import Button, RadioButtons, Slider

from disc_bin_packing.algorithms import (
    FirstFeasibleAlgorithm,
    MaxRectsAlgorithm,
    NFDHAlgorithm,
)
from disc_bin_packing.algorithms.base import GridPackingAlgorithm
from disc_bin_packing.generation import generate_modules
from disc_bin_packing.models import MODULE_SIZES, GridBin


DEFAULT_WIDTH = 10
DEFAULT_HEIGHT = 8
DEFAULT_MODULE_COUNT = 40
DEFAULT_TRIALS = 10
DEFAULT_SEED = 2026
COMPARISON_FIGURE = (
    Path(__file__).resolve().parent
    / "disc_bin_packing"
    / "scaling_experiments"
    / "Algorithm Comparison.png"
)


class RuntimeExperiment:
    """Run and display repeated packing measurements on demand."""

    def __init__(self, *, seed: int = DEFAULT_SEED) -> None:
        self.base_seed = seed
        self.run_number = 0
        self.current_seed = seed
        self.algorithms: dict[str, GridPackingAlgorithm] = {
            "First Feasible": FirstFeasibleAlgorithm(),
            "NFDH": NFDHAlgorithm(),
            "MaxRects (BSSF)": MaxRectsAlgorithm(),
        }
        self.algorithm = self.algorithms["First Feasible"]
        self.scaling_figures: list[object] = []
        self.figure, self.results_axes = plt.subplots(figsize=(10, 7))
        self.figure.subplots_adjust(bottom=0.28, top=0.88)
        self.figure.suptitle("Algorithmic Experimentation & Comparison", fontsize=16)

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

        util_axes = self.figure.add_axes((0.02, 0.045, 0.17, 0.055))
        self.util_scaling_button = Button(util_axes, "Generate util scaling")
        self.util_scaling_button.on_clicked(self._on_util_scaling_clicked)

        run_axes = self.figure.add_axes((0.22, 0.045, 0.17, 0.055))
        self.run_button = Button(run_axes, "Run experiment")
        self.run_button.on_clicked(self._on_run_clicked)

        runtime_axes = self.figure.add_axes((0.42, 0.045, 0.17, 0.055))
        self.runtime_scaling_button = Button(
            runtime_axes, "Generate runtime scaling"
        )
        self.runtime_scaling_button.on_clicked(self._on_runtime_scaling_clicked)

        packed_axes = self.figure.add_axes((0.62, 0.045, 0.17, 0.055))
        self.packed_scaling_button = Button(
            packed_axes, "Generate packed scaling"
        )
        self.packed_scaling_button.on_clicked(self._on_packed_scaling_clicked)

        comparison_axes = self.figure.add_axes((0.82, 0.045, 0.16, 0.055))
        self.comparison_button = Button(comparison_axes, "Compare algorithms")
        self.comparison_button.on_clicked(self._on_comparison_clicked)

        algorithm_axes = self.figure.add_axes((0.82, 0.42, 0.16, 0.22))
        algorithm_axes.set_title("Algorithm", fontsize=10, pad=8)
        self.algorithm_radio = RadioButtons(
            algorithm_axes, list(self.algorithms), active=0
        )
        self.algorithm_radio.on_clicked(self._on_algorithm_selected)

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

    def _on_comparison_clicked(self, _: object) -> None:
        self._show_algorithm_comparison()

    def _on_algorithm_selected(self, label: str) -> None:
        self.algorithm = self.algorithms[label]
        self.run_experiment()

    def _begin_run(self) -> int:
        """Advance to a reproducible but distinct seed for the next action."""
        self.current_seed = self.base_seed + self.run_number
        self.run_number += 1
        return self.current_seed

    def _module_counts_for_scaling(self) -> list[int]:
        maximum = int(self.module_slider.valmax)
        counts = list(range(1, maximum + 1, 5))
        if counts[-1] != maximum:
            counts.append(maximum)
        return counts

    def _run_measurements(
        self, module_count: int, trial_count: int, random_source: Random
    ) -> tuple[float, float, float, float]:
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
            fmean(runtimes),
            fmean(utilisations),
            fmean(packed_percentages),
            stdev(runtimes) if trial_count > 1 else 0.0,
        )

    def _show_scaling_plot(
        self, y_label: str, title: str, metric: str
    ) -> None:
        trial_count = int(self.trial_slider.val)
        module_counts = self._module_counts_for_scaling()
        run_seed = self._begin_run()
        random_source = Random(run_seed)
        values: list[float] = []
        runtime_standard_deviations: list[float] = []
        for module_count in module_counts:
            runtime, utilisation, packed, runtime_standard_deviation = self._run_measurements(
                module_count, trial_count, random_source
            )
            values.append(
                {"runtime": runtime, "utilisation": utilisation, "packed": packed}[metric]
            )
            runtime_standard_deviations.append(runtime_standard_deviation)

        figure, axes = plt.subplots(figsize=(8, 5))
        if metric == "runtime":
            axes.errorbar(
                module_counts,
                values,
                yerr=runtime_standard_deviations,
                fmt="-o",
                capsize=3,
                label="Mean runtime ± 1 standard deviation",
            )
            axes.legend()
        else:
            axes.plot(module_counts, values, marker="o")
        selected_title = f"{self.algorithm.name}: {title}"
        axes.set_title(
            f"{selected_title} (±1 standard deviation)"
            if metric == "runtime"
            else selected_title
        )
        figure.suptitle(f"Seed {run_seed} | Run {self.run_number}")
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

    def _show_algorithm_comparison(self) -> None:
        """Compare all algorithms on identical random module sequences."""
        trial_count = int(self.trial_slider.val)
        module_counts = self._module_counts_for_scaling()
        values = {
            name: {"runtime": [], "utilisation": [], "packed": []}
            for name in self.algorithms
        }
        run_seed = self._begin_run()
        random_source = Random(run_seed)

        for module_count in module_counts:
            measurements = {
                name: {"runtime": [], "utilisation": [], "packed": []}
                for name in self.algorithms
            }
            for _ in range(trial_count):
                modules = generate_modules(
                    module_count,
                    {size: 1 for size in MODULE_SIZES},
                    random_source=random_source,
                )
                bin = GridBin(int(self.width_slider.val), int(self.height_slider.val))
                for name, algorithm in self.algorithms.items():
                    start = perf_counter()
                    result = algorithm.pack(bin, modules)
                    measurements[name]["runtime"].append(
                        (perf_counter() - start) * 1_000
                    )
                    measurements[name]["utilisation"].append(result.utilisation(bin))
                    measurements[name]["packed"].append(
                        (len(modules) - len(result.unpacked)) / module_count
                    )

            for name in self.algorithms:
                for metric in values[name]:
                    values[name][metric].append(fmean(measurements[name][metric]))

        figure, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharex=True)
        plots = (
            ("utilisation", "Useful utilisation", True),
            ("packed", "Requested modules packed", True),
            ("runtime", "Average runtime (ms)", False),
        )
        for axes_item, (metric, label, as_percentage) in zip(axes, plots):
            for name in self.algorithms:
                axes_item.plot(module_counts, values[name][metric], marker="o", label=name)
            axes_item.set_title(label)
            axes_item.set_xlabel("Module count")
            axes_item.grid(True, alpha=0.3)
            if as_percentage:
                axes_item.set_ylim(0, 1)
                axes_item.yaxis.set_major_formatter(
                    FuncFormatter(lambda value, _: f"{value:.0%}")
                )
            else:
                axes_item.set_ylabel(label)

        axes[0].set_ylabel("Average proportion")
        axes[2].legend()
        figure.suptitle(
            f"Algorithm comparison: identical input sequences | "
            f"Seed {run_seed} | Run {self.run_number}"
        )
        figure.tight_layout()
        figure.savefig(COMPARISON_FIGURE, dpi=180, bbox_inches="tight")
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
        run_seed = self._begin_run()
        random_source = Random(run_seed)

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
            f"{self.algorithm.name} | {width} × {height} grid | {module_count} modules | "
            f"{len(measurements)} trials | Seed {self.current_seed} | "
            f"Run {self.run_number}",
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
            bbox=(0.02, 0.02, 0.74, 0.98),
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
    parser = argparse.ArgumentParser(
        description="Run interactive, reproducible discrete packing experiments."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Seed for generated module sequences (default: {DEFAULT_SEED}).",
    )
    args = parser.parse_args()
    RuntimeExperiment(seed=args.seed).show()


if __name__ == "__main__":
    main()
