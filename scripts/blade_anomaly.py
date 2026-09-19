import numpy as np

def calculate_mad_anomaly(data_points, threshold=3.0):
    data = np.array(data_points)
    median = np.median(data)
    mad = np.median(np.abs(data - median))
    if mad == 0:
        return np.zeros(len(data), dtype=bool)
    modified_z_scores = 0.6745 * (data - median) / mad
    return np.abs(modified_z_scores) > threshold

if __name__ == '__main__':
    test_ticks = [100.1, 100.2, 100.15, 100.3, 100.2, 125.4, 100.1]
    anomalies = calculate_mad_anomaly(test_ticks)
    print(f'[BLADE ENGINE] Input: {test_ticks}')
    print(f'[BLADE ENGINE] Anomalies Flagged: {[test_ticks[i] for i, is_anomaly in enumerate(anomalies) if is_anomaly]}')
