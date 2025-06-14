import os
from datetime import datetime

import pandas as pd


def gen_path_template(params):

    dir_in = "{params.source}/{params.kind}/{params.model}/{params.variable}/%Y/%j/"

    if params.kind == "observed":
        file_in = "{params.model}_{params.variable}_%Y%m%d00.nc"
        freq = "1D"

    elif params.kind in ["satellite", "radar"]:
        file_in = "{params.model}_{params.variable}_{params.member}_%Y%m%d%H%M.nc"
        freq = "5min"

    elif params.kind in ["forecast", "seasonal"]:
        file_in = "{params.model}_{params.variable}_{params.member}_%Y%m%d00.nc"
        freq = "1D"

    elif params.kind == ["reanalysis", "climatology"]:
        file_in = "{params.model}_{params.variable}_{params.member}_%Y%m%d.nc"
        freq = "1D"

    return (
        os.path.join(dir_in, file_in).format(params=params),
        freq
    )    
    

def get_paths(params, path_template, freq):
    if params.initDate and params.endDate:
        times = pd.date_range(params.initDate, params.endDate, freq=freq)
        return [time.strftime(path_template) for time in times]

    else:
        return [datetime.fromisoformat(params.date).strftime(path_template)]
