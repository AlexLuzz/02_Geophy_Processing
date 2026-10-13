from config.paths import ProjectPaths
from src.loaders.ert_loading_tools import load_geometry
from src.mesh.pygimli_mesh_tools import *
from scripts.MCM_MONOS.mesh_building.MONO_gmsh import build_gmsh_layered
from src.mesh.gmesh_tools import *
from src.processing.inversion.ert_processor import ERTProcessor
from src.loaders.ert_loader import ERTLoader
from src.visualization.ERT.inversion_data_report import InversionDataReport

from datetime import datetime

def run_TL_MONO2M():
    paths = ProjectPaths(user='alexi', project_name='MCM_MONO2M_TLERT_9011') 
        
    geom = load_geometry(paths.MCM_MONO2M_ELECS_POS_TRUE, params={
        "absolute_pos": True, 
        'inverse_order': False,
        "projection": {"type": "distance", "output_axis": "X"}
    })

    mesh = build_gmsh_layered(geom, size_surface=0.3, size_interface=1.0, size_depth=8.0,
                                interface_depth=5.0, extension=10.0, depth=30.0)

    loader = ERTLoader(site_id="MCM_MONO2M", elec_pos=geom)
    df = loader.load_prime(source=paths.TLERT_MONO2M_9011)

    now = datetime.now().strftime("%Y%m%d_%H%M")
    folder = paths.ACTIVE_PROJECT_DIR / f"{now}"

    processor = ERTProcessor(mesh=mesh, electrode_positions=geom, df=df)
    paraDomain = processor.paraDomain

    params = {
        'lam': 20,
        'robustData': False,
        'blockyModel': False,  
        'zWeight': 0.7,
        'err_values': 3
    }
    
    results = processor.run_timelapse(params=params)

    processor.save_results(folder_path=folder, results_list=results, params=params)
    
    InversionDataReport.print_relative(
            baseline_idx=1,

            folder_path=folder,
            results=results,
            elec_pos=geom,
            mesh=mesh,
            paradomain=paraDomain,
            logs=processor.memory_handler.logs
        )

    InversionDataReport.print_absolute(    
                folder_path=folder,
                results=results,
                elec_pos=geom,
                mesh=mesh,
                paradomain=paraDomain,
                logs=processor.memory_handler.logs
            )
    
if __name__ == "__main__":
    run_TL_MONO2M()