from config.paths import ProjectPaths
from src.visualization.ERT.inversion_data_report import InversionDataReport
from src.loaders.ert_loading_tools import load_geometry

def run_plot_mono1m():
    paths = ProjectPaths(user='alexi', project_name='MCM_MONO1M_TLERT_9012') 

    geom = load_geometry(paths.MCM_MONO1M_ELECS_POS_TRUE, params={
            "absolute_pos": True, 
            'inverse_order': False,
            "projection": {"type": "distance", "output_axis": "X"}
        })

    InversionDataReport.print_relative(
        folder_path=paths.PROJECTS_DIR / 'MCM_MONO1M_TLERT_9012' / '20260909_0042',
        elec_pos=geom
    )

if __name__ == "__main__":
    run_plot_mono1m()