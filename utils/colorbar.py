import json
import numpy as np
from matplotlib.cm import colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


def add_colorbar(colorbar: str | dict):  

    if isinstance(colorbar, dict):
        name = list(colorbar.keys())[0]
        levels_scale = colorbar[name]["scale"]
        array_colors = np.array(colorbar[name]['cmap']) / 255.0
        cmap = colors.ListedColormap(array_colors, name)
        norm = colors.BoundaryNorm(levels_scale, cmap.N)
        return levels_scale, cmap, norm

    elif isinstance(colorbar, str):
        with open(f"data/cmaps/{colorbar}.json") as file:
            data = json.load(file)
        levels_scale = data[f"{colorbar}"]["scale"]
        array_colors = np.array(data[f"{colorbar}"]['cmap']) / 255.0
        cmap = colors.ListedColormap(array_colors, colorbar)
        norm = colors.BoundaryNorm(levels_scale, cmap.N)
        return levels_scale, cmap, norm
    
    else:
        raise HTTPException(status_code=400, detail="Invalid colorbar format. Expected a string or a dictionary.")


def show_colorbar(im, axes):
    cax = inset_axes(axes,
                                   width="45%",  # 80%
                                   height="3%",
                                   loc='lower right',
                                   borderpad=5)  # 1.65)
    
    cbar = plt.colorbar(im, cax=cax, orientation='horizontal', alpha=1)
    cbar.ax.xaxis.set_label_coords(-0.1, 0.5)
    cbar.solids.set_alpha(1)
    cbar.ax.tick_params(colors="black", labelsize=12)
    cbar.ax.yaxis.set_tick_params(color="black")
    cbar.update_ticks()

    # logo_img = Image.open('moonpng/configs/statics/logo.png')

    # inner_ax = inset_locator.inset_axes(cax, width="30%", height="250%",
    #                                     loc='lower right', borderpad=3)
    # inner_ax.set_axis_off()
    # inner_ax.imshow(logo_img, zorder=200, alpha=1)
