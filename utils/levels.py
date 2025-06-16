import numpy as np


def get_levels(params):
    if isinstance(params.levels, list):
        return params.levels
    elif isinstance(params.levels, dict):
        return np.arange(params.levels["min"], params.levels["max"] + params.levels["step"], params.levels["step"])
    else:
        return None