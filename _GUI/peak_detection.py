import numpy as np
from scipy.signal import find_peaks


# function to find small peaks for one LONG test
def small_peaks(test):
    # checking for valleys
    peaks, _ = find_peaks(-1 * np.array(test.P4), width=10)

    # checking for peaks
    if len(peaks) == 0:
        peaks, _ = find_peaks(np.array(test.P4), width=10)

        # checking number of peaks
    if len(peaks) >= 10:  # ref bubble
        # print("len(peaks) = ", str(len(peaks)))
        return 3
    elif 5 < len(peaks) < 10:  # ref bubble OR ref failure
        # print("len(peaks) = ", str(len(peaks)))
        return 2
    elif 0 < len(peaks) <= 5:  # normal test OR ref failure
        # print("len(peaks) = ", str(len(peaks)))
        return 1
    else:
        # print("len(peaks) = ", str(len(peaks)))
        return 0  # no peaks --> undetermined


# function to find wide peaks for one LONG test
def wide_peaks(test):
    # checking for valleys
    peaks, _ = find_peaks(-1 * np.array(test.P4), width=250)

    # checking for peaks
    if len(peaks) == 0:
        peaks, _ = find_peaks(np.array(test.P4), width=250)

    return peaks


# function to find (short) peaks for one SHORT TEST. size = width of peaks
def short_peaks(test, size):
    if size == 0:
        # checking for valleys
        peaks_1, _ = find_peaks(-1 * np.array(test.P4))

        # checking for peaks
        peaks_2, _ = find_peaks(np.array(test.P4))

        # merging valleys and peaks
        peaks = np.concatenate((peaks_1, peaks_2))

        if len(peaks) >= 80:  # normal
            return 1
        else:  # undetermined
            return 0

    elif size == 10:
        # checking for valleys
        peaks_1, _ = find_peaks(-1 * np.array(test.P4), width=size)

        # checking for peaks
        peaks_2, _ = find_peaks(np.array(test.P4), width=size)

        # merging valleys and peaks
        peaks = np.concatenate((peaks_1, peaks_2))

        if len(peaks) >= 3:  # ref bubble
            return 1
        else:  # undetermined
            return 0
