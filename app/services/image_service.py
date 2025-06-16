from io import BytesIO

from models.params import MoonPngParams
import utils.netcdf as nc_utils
import utils.paths as path_utils
import utils.plot as plot_utils
from utils.levels import get_levels
from utils.bounding_box import get_bbox
import utils.mask as mask_utils
import utils.colorbar as colorbar_utils
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from utils.profiler import profile_block


def get_image(params: MoonPngParams):
    """Gera uma imagem a partir dos parâmetros fornecidos."""
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

    return image, figure, dataset
