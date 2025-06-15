from datetime import datetime

from fastapi import HTTPException, Query
from pydantic import BaseModel, Field, root_validator


class MoonPngParams(BaseModel):
    kind: str = Field(..., description="Tipo de dado meteorológico.")
    model: str = Field(..., description="Modelo numérico utilizado.")
    variable: str = Field(..., description="Variável meteorológica.")
    date: str = Field(default=datetime.utcnow().isoformat(), description="Data da previsão no formato ISO 8601.")
    initDate: str | None = Field(default=None, description="Data inicial do intervalo.")
    endDate: str | None = Field(default=None, description="Data final do intervalo.")
    member: str = Field(
        default="M000", description="Membro do modelo para previsões, se aplicável."
    )

    source: str = Field(default="/data", description="Diretório de origem dos dados.")
    aggregation: str | None = Field(
        default=None, description="Tipo de agregação temporal dos dados."
    )
    smoothed: bool = Field(
        default=False, description="Se os dados devem ser suavizados."
    )
    resolution: float | None = Field(default=None, description="Resolução da imagem.")
    extent: str | None = Field(
        default=None, description="Extensão geográfica do recorte."
    )

    yclim: int = Field(default=1991, description="Ano base da climatologia.")
    title: str | None = Field(default=None, description="Título da figura.")
    cbar_cfg: str | None = Field(
        default=None, description="Configuração personalizada de colorbar."
    )
    colorbar: str | None = Field(default=None, description="Colorbar utilizada.")
    showcolorbar: bool = Field(
        default=True, description="Se o colorbar deve ser exibido."
    )
    titlevariable: str | None = Field(default=None, description="Título da variável.")
    dt_isoline: str | None = Field(
        default=None, description="Delta de tempo entre isolinhas."
    )

    shapecontours: str | None = Field(
        default=None, description="Contornos de shapefiles."
    )
    mask: str | None = Field(default=None, description="Máscara geográfica aplicada.")
    pad: float = Field(
        default=0.75, description="Espaçamento entre elementos do gráfico."
    )
    points: str | None = Field(
        default=None, description="Pontos geográficos a destacar."
    )

    legend: str | None = Field(default=None, description="Legenda personalizada.")
    polygon_color: str | None = Field(
        default=None, description="Cor de polígonos adicionados."
    )
    alpha: float = Field(default=0.5, description="Transparência da imagem.")
    dpi: int = Field(default=100, description="Resolução da imagem.")
    grid: bool = Field(default=True, description="Se exibe grade no mapa.")
    ocean: bool = Field(default=True, description="Se desenha o oceano.")
    pltmethod: str | None = Field(default=None, description="Método de plotagem.")
    interpolation: str = Field(
        default="nearest", description="Método de interpolação da imagem."
    )

    @root_validator(skip_on_failure=True)
    def validate_combination(cls, values):
        kind = values.get("kind")
        model = values.get("model")
        variables = values.get("variable")
        date = values.get("date")

        if model == "chimera_as" and "500hPa_geopotential_height" in variables:
            raise HTTPException(
                status_code=400,
                detail="O modelo ECMWF não suporta a variável '10m_wind_speed'.",
            )

        if kind == "observed" and datetime.fromisoformat(date) > datetime.utcnow():
            raise HTTPException(
                status_code=400,
                detail="Não é permitido usar datas passadas com kind=forecast.",
            )

        if model not in VALID_MODELS[kind]:
            raise HTTPException(
                status_code=400,
                detail=f"Modelo '{model}' não é válido para o tipo '{kind}'",
            )

        return values

    class Config:
        json_schema_extra = {
            "example": {
                "kind": "forecast",
                "model": "gfs_glo",
                "variable": "2m_air_temperature",
                "date": "2025-06-14T12:00:00Z",
            }
        }


def get_params(
    kind: str = Query(..., description="Tipo de dado meteorológico."),
    model: str = Query(..., description="Modelo numérico utilizado."),
    variable: str = Query(
        ..., description="Variável ou lista de variáveis meteorológicas."
    ),
    date: str | None = Query(default=datetime.utcnow(), description="Data da previsão no formato ISO 8601."),
    member: str = Query(
        "M000", description="Membro do modelo para previsões, se aplicável."
    ),
    source: str = Query("/data", description="Diretório de origem dos dados."),
    initDate: str | None = Query(None, description="Data inicial do intervalo."),
    endDate: str | None = Query(None, description="Data final do intervalo."),
    hours: int = Query(0, description="Número de horas a considerar."),
    aggregation: str | None = Query(None, description="Tipo de agregação temporal."),
    smoothed: bool = Query(False, description="Se os dados devem ser suavizados."),
    resolution: float | None = Query(None, description="Resolução da imagem."),
    extent: str | None = Query(None, description="Extensão geográfica do recorte."),
    windlevel: str | None = Query(None, description="Nível vertical do vento."),
    vmin: float | None = Query(None, description="Valor mínimo da escala de cores."),
    vmax: float | None = Query(None, description="Valor máximo da escala de cores."),
    freq: str | None = Query(None, description="Frequência temporal dos dados."),
    yclim: int = Query(1991, description="Ano base da climatologia."),
    title: str | None = Query(None, description="Título da figura."),
    cbar_cfg: str | None = Query(
        None, description="Configuração personalizada do colorbar."
    ),
    colorbar: str | None = Query(None, description="Colorbar utilizada."),
    showcolorbar: bool = Query(True, description="Exibir colorbar."),
    titlevariable: str | None = Query(None, description="Título da variável."),
    dt_isoline: str | None = Query(
        None, description="Intervalo de tempo para isolinhas."
    ),
    contourf: bool | None = Query(None, description="Se usa contornos preenchidos."),
    isolines: bool | None = Query(None, description="Se desenha isolinhas."),
    barbs: bool | None = Query(None, description="Se desenha flechas de vento."),
    quivers: bool | None = Query(None, description="Se desenha vetores de vento."),
    shapecontours: str | None = Query(None, description="Contornos de shapefiles."),
    mask: str | None = Query(None, description="Máscara geográfica aplicada."),
    pad: float = Query(0.75, description="Espaçamento entre elementos."),
    points: str | None = Query(None, description="Pontos geográficos."),
    transparent: bool = Query(True, description="Se a imagem deve ser transparente."),
    legend: str | None = Query(None, description="Legenda personalizada."),
    polygon_color: str | None = Query(None, description="Cor de polígonos."),
    alpha: float = Query(0.5, description="Transparência da imagem."),
    dpi: int = Query(100, description="Resolução da imagem."),
    width: int = Query(15, description="Largura da imagem."),
    height: int = Query(20, description="Altura da imagem."),
    grid: bool = Query(True, description="Se exibe grade no mapa."),
    ocean: bool = Query(True, description="Se desenha o oceano."),
    pltmethod: str | None = Query(None, description="Método de plotagem."),
    interpolation: str = Query("nearest", description="Método de interpolação."),
    projection: str = Query("PlateCarree", description="Projeção cartográfica."),
    basemap: str | None = Query(None, description="Basemap customizado."),
) -> MoonPngParams:
    return MoonPngParams(
        kind=kind,
        model=model,
        variable=variable,
        member=member,
        source=source,
        date=date,
        initDate=initDate,
        endDate=endDate,
        hours=hours,
        aggregation=aggregation,
        smoothed=smoothed,
        resolution=resolution,
        extent=extent,
        windlevel=windlevel,
        vmin=vmin,
        vmax=vmax,
        freq=freq,
        yclim=yclim,
        title=title,
        cbar_cfg=cbar_cfg,
        colorbar=colorbar,
        showcolorbar=showcolorbar,
        titlevariable=titlevariable,
        dt_isoline=dt_isoline,
        contourf=contourf,
        isolines=isolines,
        barbs=barbs,
        quivers=quivers,
        shapecontours=shapecontours,
        mask=mask,
        pad=pad,
        points=points,
        transparent=transparent,
        legend=legend,
        polygon_color=polygon_color,
        alpha=alpha,
        dpi=dpi,
        width=width,
        height=height,
        grid=grid,
        ocean=ocean,
        pltmethod=pltmethod,
        interpolation=interpolation,
        projection=projection,
        basemap=basemap,
    )


FORECAST_MODELS = [
    "Ons_preveolico",
    "arpege_glo",
    "chimera_as",
    "chimera_dev",
    "csv_fit",
    "ct2w15_as",
    "ct2w15_glo",
    "ct2w40_as",
    "ct_near_as",
    "ctss_icon_glo",
    "ecmwf_as",
    "ecmwf_fct",
    "ecmwfe_as",
    "ecmwfe_as_bc",
    "efvm",
    "eta40_as",
    "eta_as",
    "fct_glo",
    "geps_glo",
    "gfs_glo",
    "gfsai_glo",
    "gfswave_glo",
    "gfswave_gsouth",
    "hycom_as",
    "icon_glo",
    "mercartor_as",
    "meteorologist",
    "meteorologist_hookgrid",
    "mlwets",
    "mgb",
    "mgb_extractions",
    "mgb_rs",
    "opticalflow_sad",
    "pestana",
    "pirambeira",
    "rap_cns",
    "regcm40_as",
    "silam_glo",
    "storm_lightning_as",
    "test.txt",
    "tigre",
    "ukmo_as",
    "w27a_as",
    "w27b_as",
    "w9p5a_as",
    "wcpt_as",
    "wets",
    "wets_ma",
    "wets_rs",
    "wets_sc",
    "wets_sp",
    "wets_vparaiba",
    "wideam_co",
    "wsema_poa",
    "wsema_rs",
    "wsema_su",
    "ww3_as",
    "ww3_rj",
]

OBSERVED_PRODUCTS = [
    "2m_relative_humidity_max_24hrs",
    "2m_relative_humidity_max_over_24hrs",
    "2m_relative_humidity_min_24hrs",
    "2m_relative_humidity_min_over_24hrs",
    "abi-goes16",
    "abi-l2-acmf",
    "abi-l2-acmf-unidata",
    "abi-l2-aodf",
    "abi-l2-cmipf",
    "abi-l2-cmipf-unidata",
    "abi-l2-codf",
    "abi-l2-codf-unidata",
    "abi-l2-dsrf",
    "abi-l2-dsrf-new",
    "abi-l2-fdcf",
    "abi-l2-fdcf-unidata",
    "abi-l2-lstf",
    "abi-l2-lstf-unidata",
    "abi-l2-rrqpef",
    "abi-l2-rrqpef-unidata",
    "abi-l2-visibility",
    "cpc_glo",
    "ct_near_as",
    "ct_near_dev",
    "ct_near_merge",
    "ct_observed_as",
    "ct_observed_dsrf",
    "current_weather",
    "fnl_glo",
    "glm-l2-lcfa",
    "glm-l2-lcfa-unidata",
    "horus_historic",
    "merge_as",
    "merge_daily_as",
    "mergestorm_as",
    "mergestorm_br",
    "nrt_as",
    "radar_al1",
    "radar_ara",
    "radar_arma10v4",
    "radar_arma11v4",
    "radar_arma1v4",
    "radar_arma3v4",
    "radar_arma4v4",
    "radar_arma5v4",
    "radar_arma6v4",
    "radar_arma7v4",
    "radar_arma8v4",
    "radar_arma9v4",
    "radar_ar01v4",
    "radar_ar05v4",
    "radar_ar07v4",
    "radar_ar08v4",
    "radar_braa",
    "radar_brbv",
    "radar_brcp",
    "radar_brcz",
    "radar_brgv",
    "radar_brni",
    "radar_brpc",
    "radar_brqa",
    "radar_brrr",
    "radar_brsn",
    "radar_brsr",
    "radar_brtt",
    "radar_brua",
    "radar_brsr",
    "radar_bv1",
    "radar_bz22",
    "radar_cgc",
    "radar_chc",
    "radar_co_bgt",
    "radar_co_crmg",
    "radar_co_crz",
    "radar_co_gvr",
    "radar_co_mcq",
    "radar_co_sa",
    "radar_co_se",
    "radar_co_tbz",
    "radar_coand",
    "radar_cobar",
    "radar_cocar",
    "radar_cocor",
    "radar_comun",
    "radar_cosan",
    "radar_cotab",
    "radar_crj",
    "radar_cu00",
    "radar_cu01",
    "radar_cu04",
    "radar_cu05",
    "radar_cu07",
    "radar_cz1",
    "radar_gam",
    "radar_gf01",
    "radar_jg1",
    "radar_list",
    "radar_lnt",
    "radar_lon",
    "radar_mc1",
    "radar_mclc5",
    "radar_mcp",
    "radar_mig",
    "radar_mn1",
    "radar_mxca5",
    "radar_mxcc2",
    "radar_mxam5",
    "radar_mxqt3",
    "radar_ninu",
    "radar_pach",
    "radar_panm3",
    "radar_pbr",
    "radar_pco",
    "radar_pe1",
    "radar_poa",
    "radar_ptv",
    "radar_sf1",
    "radar_slu",
    "radar_sn1",
    "radar_spz",
    "radar_sr1",
    "radar_st1",
    "radar_stg",
    "radar_sv1",
    "radar_svlag",
    "radar_svana",
    "radar_svana60",
    "radar_svpar",
    "radar_svpar60",
    "radar_svmig",
    "radar_svmig60",
    "radar_svvic",
    "radar_svvic60",
    "radar_svzac",
    "radar_svzac60",
    "radar_tbt",
    "radar_tf1",
    "radar_tm1",
    "radar_ttba",
    "radar_ttpa2",
    "radar_ttul2",
    "radar_ua1",
    "radar_wpl",
    "real_as",
    "samet_daily_as",
    "samet_hourly_as",
    "samet_hourly_dev",
    "soil",
    "topo",
    "wildfire_collector",
]

SEASONAL_REANALYTIC_MODELS = [
    "Ons_preveolico",
    "canesm5_glo",
    "cfs_glo",
    "cfs_glo_daily",
    "cfsv2_glo",
    "chimera_subseas_as",
    "cmcc_subseas_glo",
    "csv_fit",
    "ct2s2w_as",
    "ct2w180_as",
    "ct2w180_glo",
    "ct2w180_interpol",
    "ct2w270_as",
    "ct2w270_glo",
    "ct2w270_interpol",
    "ct2w45_as",
    "ct2w45_glo",
    "ct2w45_interpol",
    "ct2w_clim",
    "ct2w_clim_dev",
    "ct4s_as",
    "ctclim",
    "ctss_glo",
    "dwd_subseas_glo",
    "eccc_subseas_glo",
    "ecmwf_fullrange",
    "ecmwf_subseas_glo",
    "ecmwfe46_glo",
    "gfdlspead_glo",
    "gefs_glo",
    "gem52nemo_glo",
    "jma_subseas_glo",
    "meteo_france_subseas_glo",
    "meteorologist",
    "naasgeos5v2_glo",
    "ncarccsm4_glo",
    "ncarcesm1_glo",
    "ncep_subseas_glo",
    "nmme_glo",
    "reference_config",
    "regcm_as",
    "ukmo_subseas_glo",
]

CLIMATOLOGY_MODELS = ["cfsr_glo", "cpc_glo", "era5_glo", "merge_as", "samet_daily_as"]

VALID_MODELS = {
    "forecast": FORECAST_MODELS,
    "observed": OBSERVED_PRODUCTS,
    "seasonal": SEASONAL_REANALYTIC_MODELS,
    "reanalysis": SEASONAL_REANALYTIC_MODELS,
    "climatology": CLIMATOLOGY_MODELS,
    "radar": OBSERVED_PRODUCTS,
    "satellite": OBSERVED_PRODUCTS,
}

VALID_KINDS = [
    "forecast",
    "observed",
    "seasonal",
    "reanalysis",
    "climatology",
    "satellite",
    "radar",
]
