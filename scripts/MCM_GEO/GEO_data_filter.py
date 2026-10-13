from config.paths import ProjectPaths
from src.loaders.ert_loading_tools import load_geometry
from src.mesh.gmesh_tools import *
from src.loaders.ert_loader import ERTLoader
from src.visualization.ERT.single_filtrated_report import FiltratedDataReport
from src.processing.data.data_preparator import DataPreparator

from datetime import datetime

def filter_GEO(dd: bool = True, sc: bool = False, rec_err: float = 30, plot_report: bool = False):
    paths = ProjectPaths(user='AQ96560', project_name='MCM_GEO') 
        
    geom_geo = load_geometry(paths.MCM_GEO_ELECS_POS, params={
            "absolute_pos": True, 
            'inverse_order': True,
            "projection": {"type": "best_fit", "output_axis": "X"}
        })
    
    loader = ERTLoader(site_id="MCM_GEO", elec_pos=geom_geo)

    if dd:
        loader.load_sas4000(source=paths.ERT_MCM_2026E / "MCM_GEO_DD_DDrecip.AMP")
    if sc:
        loader.load_sas4000(source=paths.ERT_MCM_2026E / "MCM_GEO_SC.AMP")

    df = loader.data

    now = datetime.now().strftime("%Y%m%d_%H%M")
    folder = paths.ACTIVE_PROJECT_DIR / f"{now}"

    preparator = DataPreparator(memory=True)
    thresholds = {
        "Vmn (mV)": {"min": 0.1},
        "R (Ohm)": {"min": 0.01},
        "err_stk (%)": {"max": 20.0},
        "err_rec (%)": {"max": rec_err},
    }

    df_clean = preparator.filter_standard_survey(df, thresholds)

    if plot_report:
        report = FiltratedDataReport.print(
            folder_path=folder,
            df_raw=df,
            df_clean=df_clean,
            geom_df=geom_geo,
            preparator=preparator
        )

    return report.df_clean

if __name__ == "__main__":
    filter_GEO(plot_report=True)