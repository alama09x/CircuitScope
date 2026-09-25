from scipy.optimize import curve_fit
import numpy as np
from numpy import ndarray

MICRO = 10**-6

class Model:
    def __init__(self, components: str, filter: str, fn: function):
        self.components = components
        self.filter = filter
        self.name = f"{components} {filter}"
        self.fn = fn

# t in seconds
def rc_high_pass(t, V_i, V_f, tau):
    return (V_f - V_i) * np.exp(-t / tau)

def rc_low_pass(t, V_i, V_f, tau):
    return V_f - rc_high_pass(t, V_i, V_f, tau)

def rlc_high_pass(t, V_i, V_f, alpha, omega0):
    if alpha > omega0:
        beta = np.sqrt(alpha**2 - omega0**2)
        if np.any(beta * t > 50):
            damping = 0
        else:
            damping = np.cosh(beta * t) + (alpha / beta) * np.sinh(beta * t)
        # damping = (1 / (2 * beta)) * ((beta - alpha) * np.exp(-beta * t) + (alpha + beta) * np.exp(beta * t))
    elif alpha < omega0:
        omega_d = np.sqrt(omega0**2 - alpha**2)
        damping = np.cos(omega_d * t) + (alpha / omega_d) * np.sin(omega_d * t)
    elif alpha == omega0:
        # Basically imposible
         damping = 1 + alpha * t
    return (V_f - V_i) * damping * np.exp(-alpha * t)

def rlc_low_pass(t, V_i, V_f, alpha, omega0):
    return V_f - rlc_high_pass(t, V_i, V_f, alpha, omega0)

RC_LOW_PASS = Model("RC", "Low Pass", rc_low_pass)
RC_HIGH_PASS = Model("RC", "High Pass", rc_high_pass)
RLC_LOW_PASS = Model("RLC", "Low Pass", rlc_low_pass)
RLC_HIGH_PASS = Model("RLC", "High Pass", rlc_high_pass)

def fit_to_model(v_data: ndarray, t_data: ndarray) -> dict | None:
    
    # popt, pcov = curve_fit(rlc_low_pass, t_data, v_data, [-10, 10, 60000, 100000], bounds=([-20, 0, 0, 0], [0, 20, 10**9, 10**9]))
    # return RLC_LOW_PASS, popt, pcov

    rc_models = [RC_LOW_PASS, RC_HIGH_PASS]
    rlc_models = [RLC_LOW_PASS, RLC_HIGH_PASS]

    all_models = [rlc_models, rc_models]
    solutions = []

    for i, models in enumerate(all_models):
        for model in models:
            if i == 0:
                # RLC
                p0 = [-10, 10, 1e5, 1e5]
                bounds = ([-20, 0, 0, 0], [0, 20, 1e9, 1e9])
            else:
                # RC
                p0 = [-10, 10, 2e-4]
                bounds = ([-20, 0, 0], [0, 20, 1e3])
            
            popt, pcov = curve_fit(model.fn, t_data, v_data, p0=p0, bounds=bounds)

            ### The following is from AI
            residuals = v_data - model.fn(t_data, *popt)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((v_data - np.mean(v_data))**2)
            r_squared = 1 - (ss_res / ss_tot)

            eigenvalues = np.linalg.eigvalsh(pcov)
            condition_number = np.max(eigenvalues) / np.min(eigenvalues)

            perr_absolute = np.sqrt(np.diag(pcov))

            with np.errstate(divide='ignore', invalid='ignore'):
                relative_errors = perr_absolute / np.abs(popt)
                # Replace infinite or NaN relative errors with a large penalty or ignore them
                relative_errors = np.where(np.isnan(relative_errors) | np.isinf(relative_errors), 1e6, relative_errors)

            avg_relative_err = np.mean(relative_errors)
            solutions.append({"model": model, "popt": popt, "avgerr": avg_relative_err})

    least_err_solution = solutions[0]
    for solution in solutions:
        if solution["avgerr"] < least_err_solution["avgerr"]:
            print(f"{solution["model"].name}'s error {solution["avgerr"]} is less than {least_err_solution["model"].name}'s error {least_err_solution["avgerr"]}")
            least_err_solution = solution
    return least_err_solution