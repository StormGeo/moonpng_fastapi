from fastapi import APIRouter, Body, Query
from fastapi.responses import StreamingResponse
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np
import cartopy.crs as ccrs

from models.params import MoonPngParams
import utils.netcdf as nc_utils
import utils.paths as path_utils
import utils.plot as plot_utils
import utils.aggregations as aggregations
from utils.levels import get_levels
from utils.bounding_box import get_bbox
import utils.mask as mask_utils
import utils.colorbar as colorbar_utils

router = APIRouter()


@router.get("/moonpng", summary="obter dados meteorológicos")
def moonpng(params: MoonPngParams = Query(...)):
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

        return StreamingResponse(image, media_type="image/png")

    finally:
        if dataset is not None:
            nc_utils.close_and_destroy(dataset)
        if figure is not None:
            plt.close(figure)


@router.post("/moonpng", summary="Obter dados meteorológicos para múltiplas variáveis via POST")
def moonpng_post(params_list: list[MoonPngParams] = Body(...)):
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
    return StreamingResponse(image, media_type="image/png")
