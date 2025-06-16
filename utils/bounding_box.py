import cartopy.crs as ccrs

BBOX_DB = {
    "AS": (-85, -20, -60, 15),
    "BR": (-75, -32, -34, 5.3),
    "FD": (-155, 5, -80, 80),
    "S": (-58.2, -47.9, -34, -22.4),
    "SE": (-53.4, -39.4, -25.5, -14.),
    "SSE": (-65, -35, -35, -12.5),
    "AC": (-74.4, -66.0, -11.6, -6.6),
    "AL": (-38.7, -34.6, -11.0, -8.3),
    "AM": (-74.2, -55.5, -10.3, 2.7),
    "AP": (-55.3, -49.3, -1.7, 4.9),
    "BA": (-47.0, -36.8, -18.8, -8.0),
    "CE": (-41.9, -36.7, -8.3, -2.2),
    "DF": (-48.7, -46.8, -16.5, -15.0),
    "ES": (-42.3, -28.3, -21.7, -17.3),
    "GO": (-53.7, -45.4, -19.9, -11.8),
    "MA": (-49.2, -41.2, -10.7, -0.5),
    "MG": (-51.5, -39.3, -23.4, -13.7),
    "MS": (-58.6, -50.4, -24.5, -16.6),
    "MT": (-62.1, -49.7, -18.5, -6.8),
    "PA": (-59.3, -45.5, -10.3, 3.1),
    "PB": (-43.5, -34.2, -9.9, -5.5),
    "PE": (-41.8, -34.3, -9.9, -6.7),
    "PI": (-46.4, -39.8, -11.4, -2.2),
    "PR": (-55.1, -47.5, -27.2, -22.0),
    "RN": (-39.1, -31.8, -7.4, -3.3),
    "RO": (-67.3, -59.2, -14.0, -7.4),
    "RJ": (-45.3, -40.4, -23.8, -20.2),
    "RR": (-65.3, -58.3, -2.0, 5.7),
    "RS": (-60, -48, -35, -25),
    "SE": (-38.7, -35.8, -12.2, -9.0),
    "SC": (-54.5, -47.8, -29.8, -25),
    "SP": (-54.0, -42.0, -25.8, -19.0),
    "TO": (-51.2, -45.1, -13.9, -4.6),
}

def get_bbox(params):
    if params.extent:
        if isinstance(params.extent, list) and len(params.extent) == 4:
            return params.extent
        elif isinstance(params.extent, str):
            bbox = BBOX_DB.get(params.extent.upper())
            if bbox:
                return bbox
    return None

def set_extent(ax, params, dataset):
    if params.extent:
        if isinstance(params.extent, list) and len(params.extent) == 4:
            extent = params.extent
        elif isinstance(params.extent, str):
            extent = BBOX_DB.get(params.extent.upper())
        ax.set_extent(extent, crs=ccrs.PlateCarree())
        return extent
    return None 