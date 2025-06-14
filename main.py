import logging

from fastapi import Depends, FastAPI, HTTPException

from models.params import MoonPngParams, get_params
import utils.netcdf as nc_utils
import utils.paths as path_utils

app = FastAPI()

logging.basicConfig(filename="access.log", level=logging.INFO)


@app.get("/moonpng", summary="obter dados meteorológicos")
def moonpng(params: MoonPngParams = Depends(get_params)):

    path_template, freq = path_utils.gen_path_template(params)
    print(path_template)
    raw_paths = path_utils.get_paths(params, path_template, freq)
    print(raw_paths)
    validated_paths = nc_utils.run_validate(raw_paths, params.variable)

    dataset = nc_utils.get_data(validated_paths)
    
    print(dataset)

    return {"message": "Dados meteorológicos obtidos com sucesso!", "params": params, "validated_paths": validated_paths}


@app.post(
    "/moonpng", summary="Obter dados meteorológicos para múltiplas variáveis via POST"
)
def moonpng_post(params_list: list[MoonPngParams] = Depends(get_params)):
    results = []
    for params in params_list:
        path_in = path(params)
        results.append(
            {
                "params": params,
                "path": path_in,
                "message": "Dados meteorológicos processados com sucesso",
            }
        )
    return {"results": results}
