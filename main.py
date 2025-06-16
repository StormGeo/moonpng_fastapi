from fastapi import Depends, FastAPI, HTTPException, Request, Body, Query
from fastapi.responses import StreamingResponse
import matplotlib.pyplot as plt
from io import BytesIO
from models.params import MoonPngParams, get_params
import utils.netcdf as nc_utils
import utils.paths as path_utils
import utils.plot as plot_utils
import utils.aggregations as aggregations
from utils.levels import get_levels
from utils.bounding_box import BBOX_DB, set_extent, get_bbox
import utils.mask as mask_utils
import utils.colorbar as colorbar_utils
import time
from utils.logger import get_logger
from utils.profiler import profile_block
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict
import cartopy.crs as ccrs
import numpy as np
import cartopy.feature as cfeature

logger = get_logger()


app = FastAPI(debug=True, title="MoonPNG API", description="API para geração de imagens meteorológicas em formato PNG")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou liste domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("Starting MoonPNG API")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    log_data = {
        "endpoint": request.url.path,
        "method": request.method,
        "client_ip": request.client.host,
        "user_agent": request.headers.get("user-agent"),
    }

    try:
        response = await call_next(request)
        log_data["status_code"] = response.status_code
    except Exception as e:
        log_data["status_code"] = 500
        log_data["error"] = str(e)
        raise
    finally:
        duration = (time.time() - start_time) * 1000
        log_data["duration_ms"] = round(duration, 2)
        logger.info(log_data)

    return response

def get_image(params: MoonPngParams):
    """
    Gera uma imagem a partir dos parâmetros fornecidos.
    """
    path_template, freq = path_utils.gen_path_template(params)
    raw_paths = path_utils.get_paths(params, path_template, freq)
    validated_paths = nc_utils.run_validate(raw_paths, params.variable)
    dataset = nc_utils.get_data(validated_paths, params.variable)
    dataset = dataset.mean(dim="time")
    lons = dataset.longitude.values
    lats = dataset.latitude.values
    data = dataset.values
    figure, ax = plot_utils.plot(params, lons, lats, data)

    image = BytesIO()

    figure.savefig(
        image,
        format="png",
        dpi=params.dpi,
        pad_inches=0,
        bbox_inches="tight",
    )
    image.seek(0)
    
    #image = plot_utils.compress_image(image)
    return figure, ax, image, figure, dataset

def get_image_profiler(params: MoonPngParams):
    with profile_block("geração da imagem"):

        path_template, freq = path_utils.gen_path_template(params)

        with profile_block("gerar caminhos"):
            raw_paths = path_utils.get_paths(params, path_template, freq)

        with profile_block("validar caminhos"):
            validated_paths = nc_utils.run_validate(raw_paths, params.variable)

        with profile_block("carregar dataset"):
            dataset = nc_utils.get_data(validated_paths, params.variable)
            dataset = dataset.mean(dim="time")

        with profile_block("plotar figura"):
            figure = plot_utils.plot(
                params, 
                dataset.longitude.values, 
                dataset.latitude.values, 
                dataset.values
            )

        with profile_block("gerar PNG"):
            image = BytesIO()

            figure.savefig(
                image,
                format="png",
                dpi=params.dpi,
                pad_inches=0,
                bbox_inches="tight",
            )
            image.seek(0)
            
            #image = plot_utils.compress_image(image)
    return image, figure, dataset

@app.get("/moonpng", summary="obter dados meteorológicos")
def moonpng(params: MoonPngParams = Query(...)): # Depends(get_params)
    figure = plt.figure(figsize=(15, 20))
    ax = plt.axes(projection=ccrs.PlateCarree())
    try:
        path_template, freq = path_utils.gen_path_template(params)
        raw_paths = path_utils.get_paths(params, path_template, freq)
        validated_paths = nc_utils.run_validate(raw_paths, params.variable)
        dataset = nc_utils.get_data(validated_paths, params.variable)

        extent = get_bbox(params)
        if extent:
            dataset = dataset.sel(
                longitude=slice(extent[0], extent[1]),
                latitude=slice(extent[2], extent[3]),
            )
            ax.set_extent(extent, crs=ccrs.PlateCarree())

        dataset = aggregations.apply(dataset, params)
        lons, lats = np.meshgrid(dataset.longitude.values, dataset.latitude.values)

        if params.mask:
            data, lons, lats, extent = mask_utils.get_masked_data(dataset, params.mask, extent=extent, pad=1)
        else:
            data = dataset.values

        levels = get_levels(params)

        if params.contourf:
            cbar = ax.contourf(lons, lats, data, transform=ccrs.PlateCarree(), levels=levels)
            colorbar_utils
            plt.colorbar(
                cbar, 
                ax=ax, 
                orientation="horizontal",
                pad=0.05, 
                aspect=50, 
                label=params.variable
            )

        elif params.contour:
            ax.contour(lons, lats, data, colors=params.color, linewidths=params.linewidths, levels=levels, zorder=params.zorder, transform=ccrs.PlateCarree())

        if params.details:
            plot_utils.draw_details(ax, params)
        
        if params.gridlines:
            plot_utils.draw_gridlines(ax, params)
        image = BytesIO()

        figure.savefig(
            image,
            format="png",
            dpi=params.dpi,
            pad_inches=0,
            bbox_inches="tight",
        )
        image.seek(0)
        
        #image = plot_utils.compress_image(image)
        return StreamingResponse(image, media_type="image/png")

    finally:
        if dataset is not None:
            nc_utils.close_and_destroy(dataset)
        if figure is not None:
            plt.close(figure)



@app.post(
    "/moonpng", summary="Obter dados meteorológicos para múltiplas variáveis via POST"
)
def moonpng_post(params_list: list[MoonPngParams] = Body(...)): # Depends(get_params)
    figure = plt.figure(figsize=(15, 20))
    ax = plt.axes(projection=ccrs.PlateCarree())
    for params in params_list:
        path_template, freq = path_utils.gen_path_template(params)
        raw_paths = path_utils.get_paths(params, path_template, freq)
        validated_paths = nc_utils.run_validate(raw_paths, params.variable)
        dataset = nc_utils.get_data(validated_paths, params.variable)

        extent = get_bbox(params)
        if extent:
            dataset = dataset.sel(
                longitude=slice(extent[0], extent[1]),
                latitude=slice(extent[2], extent[3]),
            )
            ax.set_extent(extent, crs=ccrs.PlateCarree())

        dataset = aggregations.apply(dataset, params)
        lons, lats = np.meshgrid(dataset.longitude.values, dataset.latitude.values)

        if params.mask:
            data, lons, lats, extent = mask_utils.get_masked_data(dataset, params.mask, extent=extent, pad=1)
        else:
            data = dataset.values

        levels = get_levels(params)

        if params.contourf:
            if params.colorbar:
                levels, cmap, norm = colorbar_utils.add_colorbar(params.colorbar)
            
            cbar = ax.contourf(lons, lats, data, transform=ccrs.PlateCarree(), levels=levels, cmap=cmap, norm=norm)
            colorbar_utils.show_colorbar(cbar, ax)

        elif params.contour:
            ax.contour(lons, lats, data, colors=params.color, linewidths=params.linewidths, levels=levels, zorder=params.zorder, transform=ccrs.PlateCarree())

    if params.details:
        plot_utils.draw_details(ax, params)
    
    if params.gridlines:
        plot_utils.draw_gridlines(ax, params)


    image = BytesIO()

    figure.savefig(
        image,
        format="png",
        dpi=params.dpi,
        pad_inches=0,
        bbox_inches="tight",
    )
    image.seek(0)
    nc_utils.close_and_destroy(dataset)
    plt.close(figure)
    #image = plot_utils.compress_image(image)
    return StreamingResponse(image, media_type="image/png")

        # finally:
        #     nc_utils.close_and_destroy(dataset)
        #     plt.close(figure)
            
    # return {"results": results}
