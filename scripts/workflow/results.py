from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from scipy.io import loadmat


def default_csv_output_path(mat_path: Path) -> Path:
    return mat_path.with_suffix(".csv")


def decode_char_matrix(value: np.ndarray) -> list[str]:
    if value.ndim != 2:
        raise ValueError(f"Expected a 2D character matrix, got shape {value.shape}")
    return ["".join(value[:, i]).rstrip(" \x00") for i in range(value.shape[1])]


def load_trajectory_layout(
    mat_path: Path,
) -> tuple[list[str], list[str], np.ndarray, np.ndarray, np.ndarray]:
    data = loadmat(mat_path, chars_as_strings=False)
    required_keys = {"Aclass", "name", "description", "dataInfo", "data_1", "data_2"}
    missing = required_keys.difference(data)
    if missing:
        raise KeyError(f"Missing expected MAT keys: {', '.join(sorted(missing))}")

    names = decode_char_matrix(data["name"])
    descriptions = decode_char_matrix(data["description"])
    data_info = np.asarray(data["dataInfo"], dtype=np.int64)
    data_1 = np.asarray(data["data_1"], dtype=np.float64)
    data_2 = np.asarray(data["data_2"], dtype=np.float64)
    return names, descriptions, data_info, data_1, data_2


def extract_series(
    names: list[str],
    descriptions: list[str],
    data_info: np.ndarray,
    data_1: np.ndarray,
    data_2: np.ndarray,
) -> tuple[list[str], list[str], list[np.ndarray]]:
    if data_2.shape[0] < 1:
        raise ValueError("data_2 does not contain a time row")

    time = np.asarray(data_2[0, :], dtype=np.float64)
    headers = ["time"]
    header_descriptions = ["Independent time axis"]
    columns = [time]

    for idx, name in enumerate(names):
        if name == "time":
            continue

        source_matrix = int(data_info[0, idx])
        source_row = int(data_info[1, idx])
        sign = -1.0 if int(data_info[3, idx]) < 0 else 1.0

        if source_matrix == 1:
            if source_row < 1 or source_row > data_1.shape[0]:
                raise IndexError(f"Invalid data_1 row {source_row} for variable {name}")
            value = sign * float(data_1[source_row - 1, 0])
            series = np.full(time.shape, value, dtype=np.float64)
        elif source_matrix == 2:
            if source_row < 1 or source_row > data_2.shape[0]:
                raise IndexError(f"Invalid data_2 row {source_row} for variable {name}")
            series = sign * np.asarray(data_2[source_row - 1, :], dtype=np.float64)
        else:
            continue

        headers.append(name)
        header_descriptions.append(descriptions[idx])
        columns.append(series)

    return headers, header_descriptions, columns


def write_csv(
    output_path: Path,
    headers: list[str],
    descriptions: list[str],
    columns: list[np.ndarray],
    include_description_row: bool = False,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = zip(*columns)
    with output_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        if include_description_row:
            writer.writerow(descriptions)
        writer.writerows(rows)


def unpack_mat_to_csv(
    mat_path: Path,
    output_path: Path | None = None,
    include_description_row: bool = False,
) -> Path:
    resolved_mat_path = mat_path.resolve()
    if not resolved_mat_path.is_file():
        raise FileNotFoundError(f"MAT file not found: {resolved_mat_path}")

    resolved_output_path = (
        output_path.resolve() if output_path else default_csv_output_path(resolved_mat_path)
    )
    names, descriptions, data_info, data_1, data_2 = load_trajectory_layout(resolved_mat_path)
    headers, header_descriptions, columns = extract_series(
        names=names,
        descriptions=descriptions,
        data_info=data_info,
        data_1=data_1,
        data_2=data_2,
    )
    write_csv(
        output_path=resolved_output_path,
        headers=headers,
        descriptions=header_descriptions,
        columns=columns,
        include_description_row=include_description_row,
    )
    return resolved_output_path


def unpack_mat_results_in_directory(
    directory: Path,
    include_description_row: bool = False,
) -> list[Path]:
    output_paths: list[Path] = []
    for mat_path in sorted(directory.glob("*.mat")):
        output_paths.append(
            unpack_mat_to_csv(
                mat_path,
                include_description_row=include_description_row,
            )
        )
    return output_paths
