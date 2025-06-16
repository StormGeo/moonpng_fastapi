import geopandas as gpd
import numpy as np
import shapely.vectorized


def get_masked_data(dataset, geojson, extent=None, pad=1):
    gdf = gpd.read_file(f"data/cmaps/geojsons/{geojson}.geojson")
    geoms = gdf.geometry.values
    if extent:
        lon_slice = slice(extent[0] - pad, extent[1] + pad)
        lat_slice = slice(extent[2] - pad, extent[3] + pad)
    else:
        extent = gdf.total_bounds
        extent = [extent[0], extent[2], extent[1], extent[3]]
        lon_slice = slice(extent[0] - pad, extent[1] + pad)
        lat_slice = slice(extent[2] - pad, extent[3] + pad)

    dataset = dataset.sel(longitude=lon_slice, latitude=lat_slice)
    lons2d, lats2d = np.meshgrid(dataset.longitude.values, dataset.latitude.values)
    mask_array = np.zeros_like(lons2d, dtype=bool)
    for geom in geoms:
        mask_array |= shapely.vectorized.contains(geom, lons2d, lats2d)

    data_masked = np.ma.masked_array(dataset.values, ~mask_array)
    return data_masked, lons2d, lats2d, extent
