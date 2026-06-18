#!/usr/bin/env python3
"""Vẽ bốn phép so sánh STP từ response-times.csv."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Một số terminal Windows dùng cp1252 và không in được tiếng Việt. Giữ script
# chạy được bằng cách thay ký tự không hỗ trợ thay vì phát sinh UnicodeError.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

try:
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
except ImportError as error:
    missing = getattr(error, "name", "pandas/matplotlib/numpy")
    print(
        f"error: thiếu package {missing!r}. "
        "Cài bằng: py -m pip install pandas matplotlib",
        file=sys.stderr,
    )
    raise SystemExit(2)


FAILURE_TIME = 100.0
RECOVERY_TIME = 160.0

COMPARISONS = [
    {
        "slug": "01_dutcap_lambda",
        "title": "So sánh 1 — Đứt cáp: ảnh hưởng của λ",
        "recovery_time": RECOVERY_TIME,
        "configs": {
            "SoSanh1_DutCap_Lambda1": "λ1",
            "SoSanh1_DutCap_Lambda2": "λ2",
        },
    },
    {
        "slug": "02_saproot_lambda",
        "title": "So sánh 2 — Sập Root Bridge: ảnh hưởng của λ",
        "recovery_time": None,
        "configs": {
            "SoSanh2_SapRoot_Lambda1": "λ1",
            "SoSanh2_SapRoot_Lambda2": "λ2",
        },
    },
    {
        "slug": "03_dutcap_topology",
        "title": "So sánh 3 — Đứt cáp: ảnh hưởng của độ phức tạp topology",
        "recovery_time": RECOVERY_TIME,
        "configs": {
            "SoSanh3_DutCap_TopoHienTai": "Hiện tại: 4 switch / 4 link",
            "SoSanh3_DutCap_TopoPhucTap": "Phức tạp: 8 switch / 9 link",
        },
    },
    {
        "slug": "04_saproot_topology",
        "title": "So sánh 4 — Sập Root Bridge: ảnh hưởng của độ phức tạp topology",
        "recovery_time": None,
        "configs": {
            "SoSanh4_SapRoot_TopoHienTai": "Hiện tại: 4 switch / 4 link",
            "SoSanh4_SapRoot_TopoPhucTap": "Phức tạp: 8 switch / 9 link",
        },
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Tạo bốn biểu đồ so sánh RTT và tỷ lệ mất gói từ CSV do "
            "export_response_times.py sinh ra."
        )
    )
    parser.add_argument(
        "--csv",
        default="simulations/results/response-times.csv",
        help="File CSV đầu vào",
    )
    parser.add_argument(
        "--output-dir",
        default="simulations/results/plots",
        help="Thư mục chứa biểu đồ và bảng tổng hợp",
    )
    parser.add_argument(
        "--bin-width",
        type=float,
        default=2.0,
        help="Độ rộng cửa sổ gom nhóm theo thời gian, đơn vị giây (mặc định: 2)",
    )
    parser.add_argument(
        "--start-time",
        type=float,
        default=FAILURE_TIME,
        help=(
            "Thời điểm bắt đầu hiển thị trên biểu đồ, đơn vị giây "
            f"(mặc định: {FAILURE_TIME:g}, đúng lúc xảy ra sự cố)"
        ),
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Hiển thị cửa sổ biểu đồ ngoài việc lưu PNG",
    )
    return parser.parse_args()


def validate_data(data: "pd.DataFrame") -> "pd.DataFrame":
    required_columns = {
        "run",
        "config",
        "send_time_s",
        "response_time_ms",
        "status",
    }
    missing = sorted(required_columns - set(data.columns))
    if missing:
        raise ValueError(f"CSV thiếu các cột bắt buộc: {', '.join(missing)}")

    data = data.copy()
    data["send_time_s"] = pd.to_numeric(data["send_time_s"], errors="coerce")
    data["response_time_ms"] = pd.to_numeric(
        data["response_time_ms"], errors="coerce"
    )
    data = data.dropna(subset=["send_time_s", "config"])
    if data.empty:
        raise ValueError("CSV không có dòng dữ liệu hợp lệ")
    return data


def add_time_bins(data: "pd.DataFrame", bin_width: float) -> "pd.DataFrame":
    data = data.copy()
    data["time_bin_s"] = (
        np.floor(data["send_time_s"] / bin_width) * bin_width + bin_width / 2
    )
    data["is_lost"] = data["status"].eq("LOST")
    return data


def aggregate_variant(
    data: "pd.DataFrame", config: str, label: str
) -> "pd.DataFrame":
    selected = data[data["config"] == config].copy()
    if selected.empty:
        return pd.DataFrame()

    packet_stats = (
        selected.groupby("time_bin_s", as_index=False)
        .agg(packet_count=("status", "size"), lost_count=("is_lost", "sum"))
        .sort_values("time_bin_s")
    )
    packet_stats["loss_rate_pct"] = (
        100.0 * packet_stats["lost_count"] / packet_stats["packet_count"]
    )

    received = selected[
        selected["status"].eq("RECEIVED") & selected["response_time_ms"].notna()
    ]
    if received.empty:
        rtt_stats = pd.DataFrame(
            columns=["time_bin_s", "rtt_median_ms", "rtt_q25_ms", "rtt_q75_ms"]
        )
    else:
        rtt_stats = (
            received.groupby("time_bin_s")["response_time_ms"]
            .agg(
                rtt_median_ms="median",
                rtt_q25_ms=lambda values: values.quantile(0.25),
                rtt_q75_ms=lambda values: values.quantile(0.75),
            )
            .reset_index()
        )

    result = packet_stats.merge(rtt_stats, on="time_bin_s", how="left")
    result["config"] = config
    result["variant"] = label
    return result


def resolve_variant_label(
    data: "pd.DataFrame", config: str, fallback: str
) -> str:
    if "lambda_pps" not in data.columns or "Lambda" not in config:
        return fallback
    values = (
        data.loc[data["config"].eq(config), "lambda_pps"]
        .dropna()
        .astype(str)
        .replace("", np.nan)
        .dropna()
        .unique()
    )
    if len(values) == 1:
        return f"λ = {values[0]} packet/s"
    return fallback


def mark_failure_window(axis: "plt.Axes", recovery_time: float | None) -> None:
    right_edge = recovery_time if recovery_time is not None else axis.get_xlim()[1]
    axis.axvspan(
        FAILURE_TIME,
        right_edge,
        color="tab:red",
        alpha=0.08,
        label=(
            "Khoảng cáp bị đứt"
            if recovery_time is not None
            else "Giai đoạn sau khi root sập"
        ),
    )
    axis.axvline(FAILURE_TIME, color="tab:red", linestyle="--", linewidth=1)
    if recovery_time is not None:
        axis.axvline(
            recovery_time, color="tab:green", linestyle="--", linewidth=1
        )


def plot_comparison(
    data: "pd.DataFrame",
    comparison: dict,
    output_dir: Path,
    start_time: float,
    show: bool,
) -> bool:
    available = set(data["config"].unique())
    missing = [
        config for config in comparison["configs"] if config not in available
    ]
    if missing:
        print(
            f"warning: {comparison['slug']} thiếu config: {', '.join(missing)}",
            file=sys.stderr,
        )

    aggregates = []
    for config, fallback_label in comparison["configs"].items():
        label = resolve_variant_label(data, config, fallback_label)
        aggregate = aggregate_variant(data, config, label)
        if not aggregate.empty:
            aggregates.append(aggregate)

    if not aggregates:
        print(
            f"warning: bỏ qua {comparison['slug']} vì chưa có dữ liệu",
            file=sys.stderr,
        )
        return False

    figure, (rtt_axis, loss_axis) = plt.subplots(
        2,
        1,
        figsize=(12, 8),
        sharex=True,
        gridspec_kw={"height_ratios": [2, 1]},
    )

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for index, aggregate in enumerate(aggregates):
        color = colors[index % len(colors)]
        label = aggregate["variant"].iloc[0]
        rtt_axis.plot(
            aggregate["time_bin_s"],
            aggregate["rtt_median_ms"],
            color=color,
            linewidth=1.7,
            label=label,
        )
        rtt_axis.fill_between(
            aggregate["time_bin_s"],
            aggregate["rtt_q25_ms"],
            aggregate["rtt_q75_ms"],
            color=color,
            alpha=0.18,
        )
        loss_axis.plot(
            aggregate["time_bin_s"],
            aggregate["loss_rate_pct"],
            color=color,
            linewidth=1.5,
            label=label,
        )

    maximum_time = max(
        float(aggregate["time_bin_s"].max()) for aggregate in aggregates
    )
    if start_time >= maximum_time:
        print(
            f"warning: bỏ qua {comparison['slug']} vì --start-time "
            "nằm sau toàn bộ dữ liệu",
            file=sys.stderr,
        )
        plt.close(figure)
        return False

    rtt_axis.set_xlim(start_time, maximum_time)
    mark_failure_window(rtt_axis, comparison["recovery_time"])
    mark_failure_window(loss_axis, comparison["recovery_time"])

    rtt_axis.set_title(comparison["title"])
    rtt_axis.set_ylabel("RTT trung vị (ms)")
    rtt_axis.grid(True, linestyle=":", alpha=0.55)
    rtt_axis.legend(loc="best")

    loss_axis.set_xlabel("Thời gian mô phỏng (s)")
    loss_axis.set_ylabel("Mất gói (%)")
    loss_axis.set_ylim(-2, 102)
    loss_axis.grid(True, linestyle=":", alpha=0.55)

    subtitle = (
        "Đứt cáp tại 100s, khôi phục tại 160s"
        if comparison["recovery_time"] is not None
        else "Root Bridge sập tại 100s và không được khởi động lại"
    )
    figure.suptitle(subtitle, fontsize=9, y=0.995)
    figure.tight_layout()

    output_path = output_dir / f"{comparison['slug']}.png"
    figure.savefig(output_path, dpi=200, bbox_inches="tight")
    print(f"Đã lưu: {output_path}")
    if show:
        plt.show()
    plt.close(figure)
    return True


def classify_period(config: str, send_time: float) -> str:
    if send_time < FAILURE_TIME:
        return "before_failure"
    if "SapRoot" in config:
        return "after_root_failure"
    if send_time < RECOVERY_TIME:
        return "during_failure"
    return "after_recovery"


def write_summary(data: "pd.DataFrame", output_dir: Path) -> Path:
    selected_configs = {
        config
        for comparison in COMPARISONS
        for config in comparison["configs"]
    }
    selected = data[data["config"].isin(selected_configs)].copy()
    selected["period"] = selected.apply(
        lambda row: classify_period(row["config"], row["send_time_s"]), axis=1
    )

    rows = []
    for (config, period), group in selected.groupby(
        ["config", "period"], sort=False
    ):
        received = group[
            group["status"].eq("RECEIVED")
            & group["response_time_ms"].notna()
        ]
        lost_count = int(group["status"].eq("LOST").sum())
        rows.append(
            {
                "config": config,
                "period": period,
                "packet_count": len(group),
                "received_count": len(received),
                "lost_count": lost_count,
                "loss_rate_pct": 100.0 * lost_count / len(group),
                "mean_rtt_ms": received["response_time_ms"].mean(),
                "median_rtt_ms": received["response_time_ms"].median(),
                "p95_rtt_ms": received["response_time_ms"].quantile(0.95),
            }
        )

    summary_path = output_dir / "experiment-summary.csv"
    pd.DataFrame(rows).to_csv(summary_path, index=False)
    print(f"Đã lưu: {summary_path}")
    return summary_path


def main() -> int:
    args = parse_args()
    if args.bin_width <= 0:
        print("error: --bin-width phải lớn hơn 0", file=sys.stderr)
        return 2

    csv_path = Path(args.csv)
    if not csv_path.is_file():
        print(f"error: không tìm thấy CSV: {csv_path}", file=sys.stderr)
        return 2

    try:
        data = validate_data(pd.read_csv(csv_path))
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    data = add_time_bins(data, args.bin_width)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    generated = 0
    for comparison in COMPARISONS:
        generated += plot_comparison(
            data, comparison, output_dir, args.start_time, args.show
        )

    write_summary(data, output_dir)
    if generated == 0:
        print(
            "error: CSV chưa chứa config nào trong ma trận thí nghiệm",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
