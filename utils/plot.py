import matplotlib

matplotlib.use("Agg")
from io import BytesIO

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from PIL import Image
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LATITUDE_FORMATTER
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER
import geopandas as gpd


def draw_gridlines(ax, params):
    # CFG_GRIDLINES = {"size": 20, "color": "black"}

    if isinstance(params.gridlines, dict):
        gridlines = ax.gridlines(
            color=params.gridlines["color"], 
            draw_labels=True, 
            zorder=params.gridlines["zorder"],
            linewidth=params.gridlines["linewidth"],
            alpha=params.gridlines["alpha"],
            linestyle=params.gridlines["linestyle"],
            # xlocs=params.gridlines["xlocs"],
            # ylocs=params.gridlines["ylocs"],
        )

        gridlines.xformatter = LONGITUDE_FORMATTER
        gridlines.yformatter = LATITUDE_FORMATTER

        if params.gridlines.get("top_labels", None) is not None:
            gridlines.top_labels = bool(params.gridlines["top_labels"])
        
        if params.gridlines.get("bottom_labels", None) is not None:
            gridlines.bottom_labels = bool(params.gridlines["bottom_labels"])
        
        if params.gridlines.get("right_labels", None) is not None:
            gridlines.right_labels = bool(params.gridlines["right_labels"])
        
        if params.gridlines.get("left_labels", None) is not None:
            gridlines.left_labels = bool(params.gridlines["left_labels"])
        
        # if params.gridlines.get("xlabel_style", None) is not None:
        #     gridlines.xlabel_style = params.gridlines["xlabel_style"]

        # if params.gridlines.get("ylabel_style", None) is not None:
        #     gridlines.ylabel_style = params.gridlines["ylabel_style"]
        
    else:
        if params.gridlines is True:
            CFG_GRIDLINES = {"size": 20, "color": "black"}

            gridlines = ax.gridlines(color="black", draw_labels=True, zorder=3)
            gridlines.top_labels = False
            gridlines.xformatter = LONGITUDE_FORMATTER
            gridlines.yformatter = LATITUDE_FORMATTER
            gridlines.xlabel_style = CFG_GRIDLINES
            gridlines.ylabel_style = CFG_GRIDLINES

def draw_details(ax, params):
    ADMIN_0_STATES_PROVINCES = cfeature.NaturalEarthFeature(category='cultural', name='admin_0_boundary_lines_land',
                                        scale='50m', facecolor='none')
    ADMIN_1_STATES_PROVINCES = cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces',
                                                scale='50m', facecolor='none')
    
    if not params.ocean:
        ax.add_feature(
                cfeature.OCEAN.with_scale("50m"),
                zorder=1,
                facecolor='white')

    if isinstance(params.shapecontours, dict):
        for name, config in params.shapecontours.items():
            shape_feature = cfeature.ShapelyFeature(
                gpd.read_file(f"data/cmaps/geojsons/{name}.geojson").geometry, 
                ccrs.PlateCarree(),
                facecolor="none", 
                edgecolor="black", 
                zorder=4000
            )
            ax.add_feature(shape_feature)
    elif isinstance(params.shapecontours, str):
        shape_feature = cfeature.ShapelyFeature(
            gpd.read_file(f"data/cmaps/geojsons/{params.shapecontours}.geojson").geometry, 
            ccrs.PlateCarree(),
            facecolor="none", 
            edgecolor="black", 
            zorder=4000
        )
        ax.add_feature(shape_feature)

    if isinstance(params.details, dict):
        for name, config in params.details.items():
            if name == "ADMIN_0_STATES_PROVINCES":
                ax.add_feature(
                    ADMIN_0_STATES_PROVINCES,
                    edgecolor=config["edgecolor"],
                    facecolor=config["facecolor"],
                    zorder=config["zorder"]
                )
            elif name == "ADMIN_1_STATES_PROVINCES":
                ax.add_feature(
                    ADMIN_1_STATES_PROVINCES,
                    edgecolor=config["edgecolor"],
                    facecolor=config["facecolor"],
                    zorder=config["zorder"]
                )
            else:              
                ax.add_feature(
                    getattr(cfeature, name).with_scale(config["scale"]),
                    edgecolor=config["edgecolor"],
                    facecolor=config["facecolor"],
                    zorder=config["zorder"]
                )
    else:
        ax.add_feature(
            cfeature.COASTLINE.with_scale("50m"),
            edgecolor='k',
            facecolor="#F5E9D3",
            zorder=3)
        ax.add_feature(
            cfeature.BORDERS.with_scale("50m"),
            zorder=3,
            edgecolor="black",
            facecolor="#F5E9D3")
        ax.add_feature(
            ADMIN_0_STATES_PROVINCES,
            facecolor="none", edgecolor="black",
            zorder=3)
        ax.add_feature(
            ADMIN_1_STATES_PROVINCES,
            facecolor="none", edgecolor="black",
            zorder=3)
        # ax.add_feature(
        #     STATES.with_scale("50m"),
        #     facecolor="none", edgecolor="black",
        #     zorder=3)
        ax.add_feature(
            cfeature.LAND.with_scale("50m"),
            edgecolor='k',
            facecolor="#F5E9D3",
            zorder=-1)



def compress_image(im, quality=92):
    buffer = BytesIO()
    im = Image.open(im)
    im2 = im.convert("RGBA", palette=Image.ADAPTIVE)
    im2.save(buffer, format="PNG", optimize=True, quality=quality, transparent=True)
    buffer.seek(0)
    return buffer

