import netCDF4 as nc
import xarray as xr
import time
import os
from fastapi import HTTPException


def close_and_destroy(dataset):
    time.sleep(0.2)
    try:
        dataset.close()
        return True
    except Exception as e:
        print(str(e))
        del dataset
        return False

def run_validate(paths: list, variable: str):
    validated_paths = list()
    for path_in in paths:
        if os.path.isfile(path_in):
            validated_paths.append(path_in)
    
    if validated_paths:

        for path_in in validated_paths:
            try:
                dataset = xr.open_dataarray(path_in, cache=True, engine="netcdf4")
                close_and_destroy(dataset)
                print(f"Validated path: {path_in}")
            except Exception as e:
                msg = {
                    "function_name": f"run_validate()",
                    "message": f"error processing {path_in}",
                    "error": str(e),
                }
                raise HTTPException(
                    status_code=500,
                    detail=msg,
                )
        return validated_paths

    else:
        msg = {
            "function_name": f"run_validate()",
            "message": f"no valid paths found for variable {variable}",
            "paths": paths,
        }
        raise HTTPException(
                status_code=400,
                detail=msg,
            )


def get_data(path_or_paths: list | str):
    try:
        if isinstance(path_or_paths, list) and len(path_or_paths) > 1:
            return xr.open_mfdataset(
                path_or_paths,
                #cache=True,
                combine="by_coords",
                compat="broadcast_equals",
                #engine="netcdf4",
                parallel=True,
            )
        elif isinstance(path_or_paths, list) and len(path_or_paths) == 1:
            return xr.open_dataarray(path_or_paths[0], cache=True, engine="netcdf4")
        
        else:
            return xr.open_dataarray(path_or_paths, cache=True, engine="netcdf4")

    except Exception as e:
        msg = {
            "function_name": f"get_data()",
            "message": f"something is wrong:\n{path_or_paths}",
            "error": e,
        }
        raise Exception(msg)
