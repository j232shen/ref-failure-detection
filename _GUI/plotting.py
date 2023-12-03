import numpy as np
import matplotlib.pyplot as plt


# plot waveforms with peaks for list of tests
def plot_waveforms(target_indices, tests, test_peaks):
    n_plots = len(target_indices)

    # calculate grid dimensions
    n_cols = 4
    n_rows = int(np.ceil(n_plots / n_cols))

    # create the figure and subplots
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(10, 2.25 * n_rows))

    # flatten the subplots array to make it easier to index
    axs = axs.ravel()

    # loop over the plots and generate them
    for axs_num, idx in enumerate(target_indices):
        P4_array = np.array(tests[idx].P4)
        peaks = test_peaks[idx]

        # plotting waveforms with peaks
        axs[axs_num].plot(P4_array)
        axs[axs_num].plot(peaks, P4_array[peaks], "x")
        axs[axs_num].tick_params(axis='both', which='major', labelsize=8)

    # hide any unused subplots
    for i in range(n_plots, n_rows * n_cols):
        axs[i].axis('off')

    # show the plots
    plt.tight_layout()
    plt.show()


# plot data and fit function for one test
def plot_fit(x, y, y_fit):
    # create plot
    plt.scatter(x, y, marker='o', s=0.05, label='Data')
    plt.plot(x, y_fit, color='red', label='Fit')
    plt.show()
