"""Interactive illustration of geometric probability invariance.

The program samples points uniformly from a square region and lets you translate
and reshape an event region (matching areas) with widgets. Because geometric
probability under a uniform distribution depends only on region measure, the
estimated hit rate stays constant as you move the region or switch between
shapes of equal area.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, RadioButtons, Slider


BOUND = 2.0  # Points are sampled from the square [-BOUND, BOUND]^2.
BASE_RADIUS = 0.6
EVENT_AREA = math.pi * BASE_RADIUS**2
SAMPLE_SIZE = 20_000
WIDE_RECT_RATIO = 2.0  # width / height
TALL_RECT_RATIO = 0.5


@dataclass
class TargetRegion:
    """Event region that can take multiple shapes but keeps area fixed."""

    center: tuple[float, float]
    area: float
    shape: str = "circle"

    @property
    def radius(self) -> float:
        return math.sqrt(self.area / math.pi)

    @property
    def half_side(self) -> float:
        return 0.5 * math.sqrt(self.area)

    @property
    def diamond_extent(self) -> float:
        return math.sqrt(self.area / 2.0)

    def _rect_half_dims(self, aspect_ratio: float) -> tuple[float, float]:
        half_width = 0.5 * math.sqrt(self.area * aspect_ratio)
        half_height = 0.5 * math.sqrt(self.area / aspect_ratio)
        return half_width, half_height

    @property
    def extent_x(self) -> float:
        if self.shape == "circle":
            return self.radius
        if self.shape == "square":
            return self.half_side
        if self.shape == "diamond":
            return self.diamond_extent
        if self.shape == "wide-rect":
            half_width, _ = self._rect_half_dims(WIDE_RECT_RATIO)
            return half_width
        if self.shape == "tall-rect":
            half_width, _ = self._rect_half_dims(TALL_RECT_RATIO)
            return half_width
        raise ValueError(f"Unknown shape: {self.shape}")

    @property
    def extent_y(self) -> float:
        if self.shape == "circle":
            return self.radius
        if self.shape == "square":
            return self.half_side
        if self.shape == "diamond":
            return self.diamond_extent
        if self.shape == "wide-rect":
            _, half_height = self._rect_half_dims(WIDE_RECT_RATIO)
            return half_height
        if self.shape == "tall-rect":
            _, half_height = self._rect_half_dims(TALL_RECT_RATIO)
            return half_height
        raise ValueError(f"Unknown shape: {self.shape}")

    def contains(self, points: np.ndarray) -> np.ndarray:
        """Return a boolean mask for points that fall inside the region."""

        shifted = points - np.array(self.center)
        if self.shape == "circle":
            return np.sum(shifted * shifted, axis=1) <= self.radius**2

        if self.shape == "square":
            return (
                np.abs(shifted[:, 0]) <= self.half_side
            ) & (
                np.abs(shifted[:, 1]) <= self.half_side
            )

        if self.shape == "diamond":
            return (np.abs(shifted[:, 0]) + np.abs(shifted[:, 1])) <= self.diamond_extent

        if self.shape == "wide-rect":
            half_width, half_height = self._rect_half_dims(WIDE_RECT_RATIO)
            return (
                np.abs(shifted[:, 0]) <= half_width
            ) & (
                np.abs(shifted[:, 1]) <= half_height
            )

        if self.shape == "tall-rect":
            half_width, half_height = self._rect_half_dims(TALL_RECT_RATIO)
            return (
                np.abs(shifted[:, 0]) <= half_width
            ) & (
                np.abs(shifted[:, 1]) <= half_height
            )

        raise ValueError(f"Unknown shape: {self.shape}")


def sample_points(sample_size: int, bound: float) -> np.ndarray:
    """Draw points uniformly from the square [-bound, bound]^2."""

    return np.random.uniform(-bound, bound, size=(sample_size, 2))


def estimate_probability(target: TargetRegion, points: np.ndarray) -> float:
    """Estimate probability that the random point hits ``target``."""

    hits = target.contains(points)
    return hits.mean()


def theoretical_probability(area: float, bound: float) -> float:
    """Exact area ratio for a region fully contained in the sampling square."""

    square_area = (2 * bound) ** 2
    return area / square_area


def main() -> None:
    np.random.seed(7)  # Stable results between runs for reproducibility.

    points = sample_points(SAMPLE_SIZE, BOUND)
    target = TargetRegion(center=(0.0, 0.0), area=EVENT_AREA)
    exact = theoretical_probability(target.area, BOUND)

    print("Interactive geometric probability demo")
    print("---")
    print(
        "Use the sliders to move the region and the buttons to change shape.\n"
        "The Monte Carlo estimate stays close to the analytic area ratio no"
        " matter where the region sits or which equal-area shape you pick."
    )

    fig, ax = plt.subplots(figsize=(6, 6))
    plt.subplots_adjust(bottom=0.38, right=0.82)

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-BOUND, BOUND)
    ax.set_ylim(-BOUND, BOUND)
    ax.set_title("Geometric probability ignores translations and shape swaps")

    all_scatter = ax.scatter(points[:, 0], points[:, 1], s=5, alpha=0.12, label="tossed points")

    square_patch = plt.Rectangle((-BOUND, -BOUND), 2 * BOUND, 2 * BOUND, fill=False, linewidth=2)
    ax.add_patch(square_patch)

    hits_mask = target.contains(points)
    hits_scatter = ax.scatter(
        points[hits_mask, 0],
        points[hits_mask, 1],
        s=10,
        color="tab:orange",
        alpha=0.6,
        label="hits",
    )

    shape_patch = None

    def create_shape_patch() -> plt.Artist:
        if target.shape == "circle":
            return plt.Circle(target.center, target.radius, fill=False, color="tab:red", linewidth=2)

        if target.shape == "square":
            half_side = target.half_side
            return plt.Rectangle(
                (target.center[0] - half_side, target.center[1] - half_side),
                2 * half_side,
                2 * half_side,
                fill=False,
                color="tab:blue",
                linewidth=2,
            )

        if target.shape == "diamond":
            extent = target.diamond_extent
            return plt.Polygon(
                [
                    (target.center[0], target.center[1] + extent),
                    (target.center[0] + extent, target.center[1]),
                    (target.center[0], target.center[1] - extent),
                    (target.center[0] - extent, target.center[1]),
                ],
                closed=True,
                fill=False,
                color="tab:green",
                linewidth=2,
            )

        if target.shape == "wide-rect":
            half_width, half_height = target._rect_half_dims(WIDE_RECT_RATIO)
            return plt.Rectangle(
                (target.center[0] - half_width, target.center[1] - half_height),
                2 * half_width,
                2 * half_height,
                fill=False,
                color="tab:purple",
                linewidth=2,
            )

        if target.shape == "tall-rect":
            half_width, half_height = target._rect_half_dims(TALL_RECT_RATIO)
            return plt.Rectangle(
                (target.center[0] - half_width, target.center[1] - half_height),
                2 * half_width,
                2 * half_height,
                fill=False,
                color="tab:brown",
                linewidth=2,
            )

        raise ValueError(f"Unknown shape: {target.shape}")

    def update_shape_patch() -> None:
        nonlocal shape_patch
        if shape_patch is not None:
            shape_patch.remove()
        shape_patch = create_shape_patch()
        ax.add_patch(shape_patch)

    info_text = ax.text(
        0.02,
        1.02,
        "",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
    )

    def compute_bounds() -> tuple[float, float, float, float]:
        extent_x = target.extent_x
        extent_y = target.extent_y
        x_min = -BOUND + extent_x
        x_max = BOUND - extent_x
        y_min = -BOUND + extent_y
        y_max = BOUND - extent_y
        return x_min, x_max, y_min, y_max

    def adjust_position_controls() -> None:
        x_min, x_max, y_min, y_max = compute_bounds()
        clamped_x = float(np.clip(target.center[0], x_min, x_max))
        clamped_y = float(np.clip(target.center[1], y_min, y_max))
        target.center = (clamped_x, clamped_y)

        slider_x.eventson = False
        slider_y.eventson = False

        slider_x.valmin = x_min
        slider_x.valmax = x_max
        slider_x.ax.set_xlim(x_min, x_max)
        slider_y.valmin = y_min
        slider_y.valmax = y_max
        slider_y.ax.set_xlim(y_min, y_max)

        slider_x.set_val(clamped_x)
        slider_y.set_val(clamped_y)

        slider_x.eventson = True
        slider_y.eventson = True

    def refresh_display() -> None:
        hits_mask = target.contains(points)
        hits_scatter.set_offsets(points[hits_mask])
        estimate = hits_mask.mean()
        info_text.set_text(
            "Shape: "
            f"{target.shape}\nMonte Carlo hit rate: {estimate:.4f}\nAnalytic area ratio: {exact:.4f}"
        )
        update_shape_patch()
        fig.canvas.draw_idle()

    bounds = compute_bounds()

    slider_ax_width = 0.6
    slider_ax_left = 0.16
    slider_x_ax = plt.axes([slider_ax_left, 0.23, slider_ax_width, 0.03])
    slider_y_ax = plt.axes([slider_ax_left, 0.15, slider_ax_width, 0.03])

    slider_x = Slider(
        slider_x_ax,
        "center x",
        bounds[0],
        bounds[1],
        valinit=target.center[0],
    )
    slider_y = Slider(
        slider_y_ax,
        "center y",
        bounds[2],
        bounds[3],
        valinit=target.center[1],
    )

    def on_slider_change(_val: float) -> None:
        target.center = (slider_x.val, slider_y.val)
        refresh_display()

    slider_x.on_changed(on_slider_change)
    slider_y.on_changed(on_slider_change)

    radio_ax = plt.axes([0.84, 0.45, 0.14, 0.35])
    radio = RadioButtons(radio_ax, ("circle", "square", "diamond", "wide-rect", "tall-rect"), active=0)

    def on_shape_change(label: str) -> None:
        target.shape = label
        adjust_position_controls()
        refresh_display()

    radio.on_clicked(on_shape_change)

    button_ax = plt.axes([0.16, 0.06, 0.2, 0.06])
    throw_button = Button(button_ax, "Throw points", hovercolor="0.8")

    def on_throw(_event: object) -> None:
        nonlocal points
        points = sample_points(SAMPLE_SIZE, BOUND)
        all_scatter.set_offsets(points)
        refresh_display()

    throw_button.on_clicked(on_throw)

    ax.legend(loc="upper right")
    adjust_position_controls()
    refresh_display()
    plt.show()


if __name__ == "__main__":
    main()

