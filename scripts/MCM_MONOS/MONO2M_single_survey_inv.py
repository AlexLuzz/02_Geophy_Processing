from config.paths import ProjectPaths
from src.loaders.ert_loading_tools import load_geometry
from src.mesh.pygimli_mesh_tools import *
from scripts.MCM_MONOS.mesh_building.MONO_gmsh import build_gmsh_layered
from src.mesh.gmesh_tools import *
from src.processing.inversion.ert_processor import ERTProcessor
from src.loaders.ert_loader import ERTLoader
from src.visualization.ERT.inversion_data_report import InversionDataReport
from src.visualization.ERT.single_filtrated_report import FiltratedDataReport

from datetime import datetime

def run_MONO2M():
    paths = ProjectPaths(user='alexi', project_name='MCM_MONO2M_Single') 
        
    geom = load_geometry(paths.MCM_MONO2M_ELECS_POS_TRUE, params={
        "absolute_pos": True, 
        'inverse_order': False,
        "projection": {"type": "distance", "output_axis": "X"}
    })

    mesh = build_gmsh_layered(geom, size_surface=0.3, size_interface=1.0, size_depth=12.0,
                                    interface_depth=5.0, extension=10.0, depth=30.0)
    
    loader = ERTLoader(site_id="MCM_MONO2M", elec_pos=geom)
    df = loader.load_prime(source=paths.DATA_DIR / "9011_BGS_2026-09-01_040052.tab")
    df = df[df['reciprocal'] == False]

    now = datetime.now().strftime("%Y%m%d_%H%M")
    folder = paths.ACTIVE_PROJECT_DIR / f"{now}"

    mask = (
        (   (df[['A', 'B', 'M', 'N']] >= 1) &
            (df[['A', 'B', 'M', 'N']] <= 13)).all(axis=1)
        |
        (   (df[['A', 'B', 'M', 'N']] >= 21) &
            (df[['A', 'B', 'M', 'N']] <= 40)).all(axis=1)
    )

    #df_main = df[mask].copy()

    df_main = df.copy()
    #df_main = df_main[abs(df_main['A'] - df_main['B']) < 10]
    #df_main = df_main.iloc[::5]
    #df_rec = df[df['reciprocal'] == True].copy()

    #FiltratedDataReport.print(folder_path=folder, df_raw=df, df_clean=df_main, geom_df=geom, preparator=None)
    #computed_err = compute_error_model(r_meas=df_rec['R (Ohm)'], err_rec=df_rec['err_rec'], model_type='power')

    processor = ERTProcessor(mesh=mesh, electrode_positions=geom, df=df_main)
    paraDomain = processor.paraDomain

    #start_model = build_starting_model(mesh, paraDomain, rhomap=[[2, 1000], [3, 10]])

    params = {
        'lam': 35,
        'robustData': False,
        'blockyModel': False,  
        #'startModel': start_model,
        'zWeight': 0.7,
        #'limits': [0.1, 10000],
        'error_param': 5 
    }

    param_grid = {
        'lam': [5, 20, 50],
        'robustData': [False],
        'blockyModel': [True, False],    
        #'startModel': start_model,
        'zWeight': [0.3, 0.7],
        #'limits': [0.1, 10000],
            }
    
    #results = processor.run_single(params=params)

    results = processor.run_ensemble(param_grid=param_grid)

    processor.save_results(folder_path=folder, results_list=results, params=params)
    
    InversionDataReport.print(
        folder_path=folder,
        results_list=results,
        elec_pos=geom,
        mesh=mesh,
        paradomain=paraDomain,
        logs=processor.memory_handler.logs
    )

if __name__ == "__main__":
    run_MONO2M()