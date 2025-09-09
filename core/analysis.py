import numpy as np
import csv


def load_weather_data(file_path):
    try:
        data = np.loadtxt(file_path, delimiter=",", skiprows=1, dtype=float)
        return data
    except Exception as e:
        raise ValueError(f"Error loading data: {e}")


def calculate_monthly_averages(data):
    months = data[:, 0].astype(int)
    temps = data[:, 1]
    rains = data[:, 2]
    humids = data[:, 3] if data.shape[1] > 3 else None

    avg_temps, avg_rains, avg_humids = [], [], []
    unique_months = np.unique(months)

    for m in unique_months:
        month_data = data[months == m]
        avg_temps.append(np.mean(month_data[:, 1]))
        avg_rains.append(np.mean(month_data[:, 2]))
        if humids is not None:
            avg_humids.append(np.mean(month_data[:, 3]))

    return unique_months, avg_temps, avg_rains, avg_humids if humids is not None else None


def get_hottest_month(data):
    idx = np.argmax(data[:, 1])
    return int(data[idx, 0]), data[idx, 1]


def get_rainiest_month(data):
    idx = np.argmax(data[:, 2])
    return int(data[idx, 0]), data[idx, 2]


def get_monthly_trends(data):
    months = data[:, 0].astype(int)
    temps = data[:, 1]
    rainfall = data[:, 2]
    return months, temps, rainfall


def calculate_monthly_rainfall(data):
    return get_monthly_trends(data)[1]


def export_to_csv(data, filepath):
    try:
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Month", "Temperature", "Rainfall", "Humidity"])
            for row in data:
                writer.writerow(row)
    except Exception as e:
        raise IOError(f"Could not write to file: {e}")


def filter_by_month(data, month):
    return data[data[:, 0] == month]


def filter_by_day(data, month, day_col_idx=4):
    filtered_month = filter_by_month(data, month)
    if filtered_month.shape[1] > day_col_idx:
        return filtered_month[np.argsort(filtered_month[:, day_col_idx])]
    else:
        raise IndexError("Day column index out of bounds.")
