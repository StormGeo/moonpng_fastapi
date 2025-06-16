import os
import time

import netCDF4 as nc
import xarray as xr
from fastapi import HTTPException

CHUNKS = {"time": "auto", "latitude": "auto", "longitude": "auto"}


def close_and_destroy(dataset):
    try:
        dataset.close()
        return True
    except Exception as e:
        print(str(e))
        del dataset
        return False


def run_validate(paths: list, variable: str):
    validated_paths = [p for p in paths if os.path.isfile(p)]

    if not validated_paths:
        msg = {
            "function_name": f"run_validate()",
            "message": f"no valid paths found for variable {variable}",
            "paths": paths,
        }
        raise HTTPException(
            status_code=400,
            detail=msg,
        )

    else:
        return validated_paths


def get_data(path_or_paths: list | str, variable: str):
    try:
        if isinstance(path_or_paths, list) and len(path_or_paths) > 1:
            return xr.open_mfdataset(
                path_or_paths,
                combine="by_coords",
                # parallel=True,
                engine="netcdf4",
                chunks=CHUNKS,
            )[variable]
        elif isinstance(path_or_paths, list) and len(path_or_paths) == 1:
            return xr.open_dataset(path_or_paths[0], engine="netcdf4", chunks=CHUNKS)[
                variable
            ]

        else:
            return xr.open_dataset(path_or_paths, engine="netcdf4", chunks=CHUNKS)[
                variable
            ]

    except Exception as e:
        msg = {
            "function_name": f"get_data()",
            "message": f"something is wrong:\n{path_or_paths}",
            "error": e,
        }
        raise HTTPException(
            status_code=400,
            detail=msg,
        )
