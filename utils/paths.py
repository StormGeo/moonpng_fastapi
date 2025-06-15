import os
from datetime import datetime

from functools import lru_cache
import pandas as pd


def gen_path_template(params):
    print(params)
    dir_in = "{params.source}/{params.kind}/{params.model}/{params.variable}/%Y/%j/"

    if params.kind == "observed":
        file_in = "{params.model}_{params.variable}_%Y%m%d00.nc"
        freq = "1D"

    elif params.kind in ["satellite", "radar"]:
        dir_in = "{params.source}/observed/{params.model}/{params.variable}/%Y/%j/"
        file_in = "{params.model}_{params.variable}_{params.member}_%Y%m%d%H%M.nc"
        freq = "5min"

    elif params.kind in ["forecast", "seasonal"]:
        file_in = "{params.model}_{params.variable}_{params.member}_%Y%m%d00.nc"
        freq = "1D"

    elif params.kind in ["reanalysis", "climatology"]:
        file_in = "{params.model}_{params.variable}_{params.member}_%Y%m%d.nc"
        freq = "1D"

    return (
        os.path.join(dir_in, file_in).format(params=params),
        freq
    )    
    

# def get_paths(params, path_template, freq):
#     if params.initDate and params.endDate:
#         times = pd.date_range(params.initDate, params.endDate, freq=freq)
#         return [time.strftime(path_template) for time in times]

#     else:
#         return [datetime.fromisoformat(params.date).strftime(path_template)]

def get_paths(params, path_template, freq):
    """
    Gera uma lista (ou iterador) de caminhos com base nas datas e frequência.
    Usa generator para memória eficiente.
    """
    if params.initDate and params.endDate:
        date_range = pd.date_range(start=params.initDate, end=params.endDate, freq=freq)
    else:
        if isinstance(params.date, str):
            date_range = [datetime.fromisoformat(params.date)]
        else:
            date_range = [params.date]

    return (dt.strftime(path_template) for dt in date_range)
