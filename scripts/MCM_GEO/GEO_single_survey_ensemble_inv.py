from config.paths import ProjectPaths
from src.processing.inversion.ert_processor import ERTProcessor
from src.visualization.ERT.inversion_data_report import InversionDataReport
from datetime import datetime

from GEO_gmsh import build_MCM_GEO
from scripts.MCM_GEO.GEO_data_filter import filter_GEO


def run_GEO(dd, sc, rec_err):
    paths = ProjectPaths(user='AQ96560', project_name='MCM_GEO') 

    geom, mesh = build_MCM_GEO()

    df_clean = filter_GEO(dd, sc, rec_err, plot_report=True)

    now = datetime.now().strftime("%Y%m%d_%H%M")
    folder = paths.ACTIVE_PROJECT_DIR / f"{now}"

    processor = ERTProcessor(mesh=mesh, electrode_positions=geom, df=df_clean)
    paraDomain = processor.paraDomain

    param_grid = {
            'lam': [50],
            'robustData': [False],
            'blockyModel': [False],
            'zWeight': [0.1],
            'limits': [[0.1, 20000]],
            'err_values': [15]
        }

    
    results = processor.run_ensemble(param_grid=param_grid)

    processor.save_results(folder_path=folder, results_list=results, params=param_grid)
    
    InversionDataReport.print(
        folder_path=folder,
        results=results,
        elec_pos=geom,
        mesh=mesh,
        paradomain=paraDomain,
        logs=processor.memory_handler.logs
    )

if __name__ == "__main__":
    #run_GEO(dd=True, sc=False, rec_err=60)
    run_GEO(dd=False, sc=True, rec_err=30)
    #run_GEO(dd=True, sc=False, rec_err=10)
    #run_GEO(dd=True, sc=True, rec_err=10)
    #run_GEO(dd=False, sc=True)