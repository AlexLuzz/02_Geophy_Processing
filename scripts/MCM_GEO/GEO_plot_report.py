from config.paths import ProjectPaths
from src.visualization.ERT.inversion_data_report import InversionDataReport
from src.loaders.ert_loading_tools import load_geometry

def run_GEO():
    paths = ProjectPaths(user='AQ96560', project_name='MCM_GEO') 

    geom_geo = load_geometry(paths.MCM_GEO_ELECS_POS, params={
            "absolute_pos": True, 
            'inverse_order': True,
            "projection": {"type": "best_fit", "output_axis": "X"}
        })

    InversionDataReport.print(
        folder_path=paths.PROJECTS_DIR / 'MCM_GEO' / '20260908_1639',
        elec_pos=geom_geo
    )

if __name__ == "__main__":
    run_GEO()