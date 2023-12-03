import numpy as np
from scipy.optimize import curve_fit


# define the polynomial function to fit
def poly_func(x, a, b, c, d, e, f):
    return a * x ** 5 + b * x ** 4 + c * x ** 3 + d * x ** 2 + e * x + f


# fit data to polynomial curve for one test
def fit_poly(test):
    y = test.P4

    start_time = 0.2
    end_time = 0.2 * len(y)
    num_steps = round((end_time - start_time) / 0.2) + 1

    x = np.linspace(start_time, end_time, num_steps)

    # perform the curve fit
    popt, _ = curve_fit(poly_func, x, y)
    y_fit = poly_func(x, *popt)  # unpacks tuple into the 6 coefficients rather than passing an array

    return x, y, y_fit, popt


# define the linear function to fit
def lin_func(x, a, b):
    return a * x + b


# fit data to linear curve for one test
def fit_lin(test):
    y = test.P4

    start_time = 0.2
    end_time = 0.2 * len(y)
    num_steps = round((end_time - start_time) / 0.2) + 1

    x = np.linspace(start_time, end_time, num_steps)

    # perform the curve fit
    popt, _ = curve_fit(lin_func, x, y)
    y_fit = lin_func(x, *popt)  # unpacks tuple into the 2 coefficients rather than passing an array

    return x, y, y_fit, popt


# compute residuals for one test
def compute_residuals(y, y_fit):
    residuals = y - y_fit

    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)

    return r_squared
