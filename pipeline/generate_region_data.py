import argparse
import json
import numpy as np
import pyvista as pv
from pathlib import Path


BEFORE_VTP = "raw/1_before.vtp"
AFTER_VTP = "raw/1_after.vtp"

OUT_DATA_DIR = Path("data")
OUT_RAW_DIR = Path("raw")

PRESSURE_FIELD = "pressure"
DISPLACEMENT_FIELD = "shape_displacement"


def get_region_masks(points):
    """
    Split the vehicle into four fixed 3D regions:
    front, roof, side, rear.

    Assumption:
    x-axis = vehicle length
    z-axis = vehicle height
    """
    x = points[:, 0]
    z = points[:, 2]

    x_min, x_max = x.min(), x.max()
    z_min, z_max = z.min(), z.max()

    x_range = x_max - x_min
    z_range = z_max - z_min



    front = x <= x_min + 0.25 * x_range
    rear = x >= x_max - 0.25 * x_range
    roof = z >= z_min + 0.70 * z_range

    side = ~(front | rear | roof)

    return {
        "front": front,
        "roof": roof,
        "side": side,
        "rear": rear
    }


def get_shape_level(value, all_values):
    """
    Rank-based level for shape displacement.
    Largest displacement = high
    Smallest displacement = low
    Others = medium
    """
    abs_values = sorted([abs(v) for v in all_values], reverse=True)
    value = abs(value)

    if len(abs_values) == 1:
        return "high"

    if value == abs_values[0]:
        return "high"
    elif value == abs_values[-1]:
        return "low"
    else:
        return "medium"


def get_pressure_level(value, all_values):
    """
    Rank-based level for pressure change.
    Use absolute pressure change because both positive and negative changes matter.
    Largest absolute change = high
    Smallest absolute change = low
    Others = medium
    """
    abs_values = sorted([abs(v) for v in all_values], reverse=True)
    value = abs(value)

    if len(abs_values) == 1:
        return "high"

    if value == abs_values[0]:
        return "high"
    elif value == abs_values[-1]:
        return "low"
    else:
        return "medium"

REGION_TEXT = {
    "front": {
        "shape_effect": "A local geometry adjustment in the front region may affect the incoming airflow and change the pressure distribution near the vehicle nose.",
        "pressure_effect": "Pressure change in the front region may influence the pressure drag generated at the vehicle nose."
    },
    "roof": {
        "shape_effect": "A roofline geometry change may affect the airflow passing over the upper body of the vehicle.",
        "pressure_effect": "Pressure change over the roof may indicate a change in upper-body airflow smoothness."
    },
    "side": {
        "shape_effect": "A side-body geometry change may influence the airflow along the vehicle side surface.",
        "pressure_effect": "Pressure change on the side region may reflect redistribution of airflow along the vehicle body."
    },
    "rear": {
        "shape_effect": "A rear geometry adjustment may affect wake formation and flow separation behind the vehicle.",
        "pressure_effect": "Pressure change in the rear region may influence wake behavior and rear pressure drag."
    }
}

def main():
    OUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_RAW_DIR.mkdir(parents=True, exist_ok=True)

    before = pv.read(BEFORE_VTP)
    after = pv.read(AFTER_VTP)

    before_points = np.asarray(before.points)
    after_points = np.asarray(after.points)

    if before_points.shape != after_points.shape:
        raise ValueError("Before and after VTP point numbers are different.")

    if not np.isfinite(before_points).all() or not np.isfinite(after_points).all():
        raise ValueError("Mesh coordinates must be finite.")
    masks = get_region_masks(before_points)
    if any(not mask.any() for mask in masks.values()):
        raise ValueError("Every region must contain points; verify mesh orientation.")

    # ---------- shape displacement ----------
    if DISPLACEMENT_FIELD in after.point_data:
        displacement = np.asarray(after.point_data[DISPLACEMENT_FIELD])
    else:
        displacement = np.linalg.norm(after_points - before_points, axis=1)

    if displacement.shape != (len(before_points),) or not np.isfinite(displacement).all() or (displacement < 0).any():
        raise ValueError("Displacement must contain finite nonnegative scalar magnitudes.")
    np.save(OUT_RAW_DIR / "vertex_displacement.npy", displacement)

    shape_temp = []
    max_displacements = []

    for region_id, mask in masks.items():
        values = displacement[mask]
        avg_disp = float(np.mean(values))
        max_disp = float(np.max(values))

        shape_temp.append({
            "region_id": region_id,
            "average_displacement": avg_disp,
            "max_displacement": max_disp
        })
        max_displacements.append(max_disp)

    shape_regions = []
    for item in shape_temp:
        level = get_shape_level(item["max_displacement"], max_displacements)
        shape_regions.append({
            "region_id": item["region_id"],
            "average_displacement": round(item["average_displacement"], 6),
            "max_displacement": round(item["max_displacement"], 6),
            "change_level": level,
            "description": f"The {item['region_id']} region shows {level} geometry displacement after optimization.",
            "possible_effect": REGION_TEXT[item["region_id"]]["shape_effect"]
        })

    with open(OUT_DATA_DIR / "shape_regions.json", "w", encoding="utf-8") as f:
        json.dump(shape_regions, f, indent=2)

    # ---------- pressure ----------
    if PRESSURE_FIELD not in before.point_data or PRESSURE_FIELD not in after.point_data:
        raise ValueError(f"Pressure field '{PRESSURE_FIELD}' not found in VTP point data.")

    before_pressure = np.asarray(before.point_data[PRESSURE_FIELD])
    after_pressure = np.asarray(after.point_data[PRESSURE_FIELD])

    if any(values.shape != (len(before_points),) or not np.isfinite(values).all() for values in (before_pressure, after_pressure)):
        raise ValueError("Pressure must contain one finite scalar per point.")
    pressure_temp = []
    pressure_changes = []

    for region_id, mask in masks.items():
        p_before = before_pressure[mask]
        p_after = after_pressure[mask]

        before_mean = float(np.mean(p_before))
        after_mean = float(np.mean(p_after))
        change = after_mean - before_mean

        pressure_temp.append({
            "region_id": region_id,
            "pressure_before_mean": before_mean,
            "pressure_after_mean": after_mean,
            "pressure_change": change
        })
        pressure_changes.append(change)

    pressure_regions = []
    for item in pressure_temp:
        level = get_pressure_level(item["pressure_change"], pressure_changes)
        pressure_regions.append({
            "region_id": item["region_id"],
            "pressure_before_mean": round(item["pressure_before_mean"], 6),
            "pressure_after_mean": round(item["pressure_after_mean"], 6),
            "pressure_change": round(item["pressure_change"], 6),
            "change_level": level,
            "description": f"The {item['region_id']} region shows {level} pressure change after optimization.",
            "possible_effect": REGION_TEXT[item["region_id"]]["pressure_effect"]
        })

    with open(OUT_DATA_DIR / "pressure_regions.json", "w", encoding="utf-8") as f:
        json.dump(pressure_regions, f, indent=2)

    print("Generated:")
    print("data/shape_regions.json")
    print("data/pressure_regions.json")
    print("raw/vertex_displacement.npy")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export regional summaries from corresponding VTP meshes.")
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    BEFORE_VTP, AFTER_VTP = args.before, args.after
    OUT_DATA_DIR, OUT_RAW_DIR = args.output / "data", args.output / "raw"
    main()
