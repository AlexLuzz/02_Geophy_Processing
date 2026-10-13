from config.paths import ProjectPaths
from src.processing.inversion.ert_processor import ERTProcessor
from src.visualization.ERT.inversion_data_report import InversionDataReport
from datetime import datetime

from GEO_gmsh import build_MCM_GEO
from scripts.MCM_GEO.GEO_data_filter import filter_GEO


def run_GEO():
    paths = ProjectPaths(user='AQ96560', project_name='MCM_GEO') 

    geom, mesh = build_MCM_GEO()

    df_clean = filter_GEO(plot_report=True)

    now = datetime.now().strftime("%Y%m%d_%H%M")
    folder = paths.ACTIVE_PROJECT_DIR / f"{now}"

    processor = ERTProcessor(mesh=mesh, electrode_positions=geom, df=df_clean)
    paraDomain = processor.paraDomain

    params = {
        'lam': 50,
        'robustData': True,
        'blockyModel': False,  
        #'startModel': start_model,
        'zWeight': 0.7,
        'limits': [0.1, 20000],
        'err_values': False
    }
    
    results = processor.run_single(params=params)

    processor.save_results(folder_path=folder, results_list=results, params=params)
    
    InversionDataReport.print(
        folder_path=folder,
        results=results,
        elec_pos=geom,
        mesh=mesh,
        paradomain=paraDomain,
        logs=processor.memory_handler.logs
    )

if __name__ == "__main__":
    run_GEO()