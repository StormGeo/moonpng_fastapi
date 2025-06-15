import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import cartopy.crs as ccrs


def compress_image(im, quality=92):
    buffer = BytesIO()
    im = Image.open(im)
    im2 = im.convert('RGBA', palette=Image.ADAPTIVE)
    im2.save(
        buffer,
        format='PNG',
        optimize=True,
        quality=quality,
        transparent=True)
    buffer.seek(0)
    return buffer


def plot(params, lons, lats, data):

    fig = plt.figure(figsize=(15, 20), constrained_layout=True)
    ax = plt.axes(projection=ccrs.PlateCarree())

    #ax.set_extent(extent, crs=ccrs.PlateCarree())

    ax.contourf(
        lons,
        lats,
        data,
        #levels=params.levels,
        #cmap=params.cmap,
        #extend=params.extend,
    )
    #dataset.contourf(ax=ax)

    ax.set_title(f"{params.variable} over time")

    return fig