import matplotlib.pyplot as plt
from src.mesh.gmesh_tools import build_gmsh_mesh 
from src.visualization.basic_plotting import plot_array_on_mesh, extract_polygons, plot_sensors
from src.loaders.ert_loading_tools import load_geometry
from config.paths import ProjectPaths
from pygimli.meshtools import readGmsh

def test_build_MCM_GEO_gmsh():
    paths = ProjectPaths(user='alexi')            
    bb_geom = load_geometry(
        paths.MCM_GEO_ELECS_POS,
        params={
            "absolute_pos": True, 
            "inverse_order": True,
            "projection": {"type": "best_fit", "output_axis": "X"}
        }
    )
    mesh = build_gmsh_mesh(bb_geom, out_path=paths.OUTPUT_DIR / "MCM_GEO_mesh")
    mesh_polygons = extract_polygons(mesh)
    ax, coll = plot_array_on_mesh(mesh_polygons, edgecolor='black', alpha=0.2)
    plot_sensors(bb_geom, ax)
    print(f"MCM_GEO Mesh has {mesh.cellCount()} cells and {mesh.nodeCount()} nodes.")


def test_build_MCM_M2m_gmsh():
    paths = ProjectPaths(user='alexi')            
    bb_geom = load_geometry(
        paths.MCM_MONO2M_ELECS_POS,
        params={
            "absolute_pos": True, 
            "inverse_order": False,
            "projection": {"type": "distance", "output_axis": "X"}
        }
    )

    # You can pass gmsh sizing params here to mimic the old area/quality controls
    _ = build_gmsh_mesh(
        bb_geom, 
        params={"size_surface": 0.2, "size_depth": 3.0},
        out_path=paths.OUTPUT_DIR / "MCM_M2m_mesh"
    )

    mesh = readGmsh(paths.OUTPUT_DIR / "MCM_M2m_mesh.msh")
    
    mesh_polygons = extract_polygons(mesh)
    ax, coll = plot_array_on_mesh(mesh_polygons, edgecolor='black', alpha=0.2, top_offset=5.0)
    plot_sensors(bb_geom, ax)
    print(f"MCM_M2m Mesh has {mesh.cellCount()} cells and {mesh.nodeCount()} nodes.")


if __name__ == "__main__":
    #test_build_MCM_GEO_gmsh()
    test_build_MCM_M2m_gmsh()
    
    plt.show()