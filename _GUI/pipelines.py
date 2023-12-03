from peak_detection import small_peaks, wide_peaks, short_peaks
from curve_fitting import fit_poly, fit_lin, compute_residuals


# SHORT PIPELINE
def run_short(idx, test, test_df):
    # checking for peaks of width=0
    sh_flag = short_peaks(test, 0)

    # if at least 80 peaks
    if sh_flag == 1:
        test_df.loc[idx, 'Predicted'] = 'Normal'  # short normal
        # print("short normal; >= 80 peaks")
    else:
        # checking for peaks of width=10
        sh_flag = short_peaks(test, 10)

        # if at least 3 peaks
        if sh_flag == 1:
            test_df.loc[idx, 'Predicted'] = 'Ref bubble'  # short ref bubble
            # print("short ref bubble; >= 3 peaks")

        # less than 3 peaks
        else:
            # fit to LINEAR function
            x, y, y_fit, popt = fit_lin(test)

            # compute R-squared value
            r_squared = compute_residuals(y, y_fit)

            # check with soft threshold
            if r_squared > 0.989249:
                test_df.loc[idx, 'Predicted'] = 'Normal'  # short normal
                # print("short normal; <3 peaks, strong linear fit")
            elif r_squared < 0.979945:
                test_df.loc[idx, 'Predicted'] = 'Ref bubble'  # short ref bubble
                # print("short ref bubble; <3 peaks, weaker linear fit")
            else: # in ambiguous region
                test_df.loc[idx, 'Predicted'] = 'Ambiguous'  # ambiguous
                # check with hard threshold
                if r_squared >= 0.9850:
                    test_df.loc[idx, 'Comments'] = "Suspected normal test (short)"
                else:
                    test_df.loc[idx, 'Comments'] = "Suspected ref bubble (short)"


# LONG PIPELINE
def run_long(idx, test, test_df):
    sm_flag = small_peaks(test)

    # if at least 10 peaks
    if sm_flag == 3:
        test_df.loc[idx, 'Predicted'] = 'Ref bubble'  # ref bubble
        # print("ref bubble; >=10 small peaks")

    # if between 5 and 10 peaks
    elif sm_flag == 2:
        wd_flag = len(wide_peaks(test))
        if wd_flag > 0:
            test_df.loc[idx, 'Predicted'] = 'Ref failure'  # ref failure
            # print("ref failure; between 5 and 10 small peaks, some wide peaks")
        else:
            test_df.loc[idx, 'Predicted'] = 'Ref bubble'  # ref bubble
            # print("ref bubble; between 5 and 10 small peaks, no wide peaks")

    # if no peak detected
    elif sm_flag == 0:
        # fit to LINEAR function
        x, y, y_fit, popt = fit_lin(test)

        # check if slope is positive
        if popt[0] > 0:
            test_df.loc[idx, 'Predicted'] = 'Ref bubble'  # ref bubble
            # print("ref bubble; no peaks, slope is positive")
        else:
            test_df.loc[idx, 'Predicted'] = 'Normal'  # normal
            # print("normal; no peaks, slope is negative")

    # somewhere between 0 and 5 peaks --> this filtering should be very similar to prior
    else:
        # fit to LINEAR function
        x, y, y_fit, popt = fit_lin(test)

        # compute R-squared value
        r_squared = compute_residuals(y, y_fit)

        # check if slope is positive & fit is strong
        if (popt[0] > 0) & (r_squared > 0.9500):
            test_df.loc[idx, 'Predicted'] = 'Ref bubble'  # ref bubble
            # print("ref bubble; few peaks, positive slope and strong linear fit")
        else:
            # fit to POLYNOMIAL curve
            x, y, y_fit, popt = fit_poly(test)

            # compute R-squared value
            r_squared = compute_residuals(y, y_fit)

            # check with soft threshold
            if r_squared > 0.999286:
                test_df.loc[idx, 'Predicted'] = 'Normal'  # normal
                # print("normal; few peaks, strong polynomial fit")
            elif r_squared < 0.994845:
                test_df.loc[idx, 'Predicted'] = 'Ref failure'  # ref failure
                # print("ref failure; few peaks, weaker polynomial fit")
            else:  # in ambiguous region
                test_df.loc[idx, 'Predicted'] = 'Ambiguous'  # ambiguous
                # check with hard threshold
                if r_squared > 0.9970:
                    test_df.loc[idx, 'Comments'] = "Suspected normal test (long)"
                else:
                    test_df.loc[idx, 'Comments'] = "Suspected ref failure (long)"
