import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Union

import gmsh
import pandas as pd
import numpy as np

from pygimli.meshtools import readGmsh

from src.visualization.basic_plotting import plot_array_on_mesh, extract_polygons, plot_sensors
import matplotlib.pyplot as plt
from src.loaders.ert_loading_tools import load_geometry
from config.paths import ProjectPaths
import pygimli as pg
import pygimli.meshtools as mt

def build_gmsh_layered(
    df: pd.DataFrame,
    depth: float = 15.0,
    interface_depth: float = 2.5,
    extension: float = 10.0,
    size_surface: float = 0.5,
    size_interface: float = 2.0,
    size_depth: float = 15.0,
    params: Optional[Dict[str, Any]] = None,
):
    """
    Builds a 2D ERT mesh with a distinct structural interface (e.g., overburden vs tailings)
    using Gmsh. Includes a smooth mesh density gradient from the surface to depth.
    """
    params = params or {}
    data = df.sort_values("X")
    x, z = data["X"].to_numpy(), data["Z"].to_numpy()
    
    x_min, x_max = x.min(), x.max()
    z_min = z.min()
    
    # 1. INITIALIZATION
    gmsh.initialize()
    gmsh.model.add("layered_ert_mesh")

    try:
        geo = gmsh.model.geo

        # 1. POINTS
        # Surface points (Electrodes)
        e_pts = [geo.addPoint(xi, zi, 0) for xi, zi in zip(x, z)]
        # Interface points (Perfectly parallel to surface)
        i_pts = [geo.addPoint(xi, zi - interface_depth, 0) for xi, zi in zip(x, z)]
        
        # Extensions
        tl = geo.addPoint(x_min - extension, z[0], 0)
        tr = geo.addPoint(x_max + extension, z[-1], 0)
        
        il = geo.addPoint(x_min - extension, z[0] - interface_depth, 0)
        ir = geo.addPoint(x_max + extension, z[-1] - interface_depth, 0)
        
        bl = geo.addPoint(x_min - extension, z_min - depth, 0)
        br = geo.addPoint(x_max + extension, z_min - depth, 0)

        # 2. LINES
        surf_center = [geo.addLine(e_pts[i], e_pts[i+1]) for i in range(len(e_pts)-1)]
        surf_full = [geo.addLine(tl, e_pts[0])] + surf_center + [geo.addLine(e_pts[-1], tr)]
        
        int_center = [geo.addLine(i_pts[i], i_pts[i+1]) for i in range(len(i_pts)-1)]
        int_full = [geo.addLine(il, i_pts[0])] + int_center + [geo.addLine(i_pts[-1], ir)]

        right_top = geo.addLine(tr, ir)
        left_top = geo.addLine(il, tl)
        
        right_bot = geo.addLine(ir, br)
        bottom = geo.addLine(br, bl)
        left_bot = geo.addLine(bl, il)

        # 3. CURVE LOOPS & SURFACES
        # int_full goes Left->Right. To close the top loop, we reverse it using -tag
        int_reversed = [-tag for tag in reversed(int_full)]
        
        loop_top = geo.addCurveLoop(surf_full + [right_top] + int_reversed + [left_top])
        domain_top = geo.addPlaneSurface([loop_top])

        loop_bot = geo.addCurveLoop(int_full + [right_bot, bottom, left_bot])
        domain_bot = geo.addPlaneSurface([loop_bot])

        geo.synchronize()

        # 4. PHYSICAL GROUPS
        gmsh.model.addPhysicalGroup(1, surf_full, tag=-1) # Surface
        gmsh.model.addPhysicalGroup(1, [right_top, right_bot, bottom, left_bot, left_top], tag=-2) # Outer boundaries
        #gmsh.model.addPhysicalGroup(1, int_full, tag=10)  # Structural Interface marker
        
        gmsh.model.addPhysicalGroup(2, [domain_top, domain_bot], tag=2) # Overburden
        #gmsh.model.addPhysicalGroup(2, [domain_bot], tag=3) # Tailings
        
        gmsh.model.addPhysicalGroup(0, e_pts, tag=99) # Electrodes

        # 5. MESH DENSITY FIELDS
        
        # Field 1 & 2: Distance to topography and interface
        gmsh.model.mesh.field.add("Distance", 1)
        gmsh.model.mesh.field.setNumbers(1, "CurvesList", surf_full)
        
        gmsh.model.mesh.field.add("Distance", 2)
        gmsh.model.mesh.field.setNumbers(2, "CurvesList", int_full)

        # Field 3: Top Layer Threshold (Grades size_surface -> size_interface)
        gmsh.model.mesh.field.add("Threshold", 3)
        gmsh.model.mesh.field.setNumber(3, "InField", 1)
        gmsh.model.mesh.field.setNumber(3, "SizeMin", size_surface)
        gmsh.model.mesh.field.setNumber(3, "SizeMax", size_interface)
        gmsh.model.mesh.field.setNumber(3, "DistMax", interface_depth)

        # Field 4: Bottom Layer Threshold (Grades size_interface -> size_depth)
        gmsh.model.mesh.field.add("Threshold", 4)
        gmsh.model.mesh.field.setNumber(4, "InField", 2)
        gmsh.model.mesh.field.setNumber(4, "SizeMin", size_interface)
        gmsh.model.mesh.field.setNumber(4, "SizeMax", size_depth)
        gmsh.model.mesh.field.setNumber(4, "DistMax", depth)

        # ---------------------------------------------------------
        # THE FIX: ISOLATE THE FIELDS TO THEIR SPECIFIC LAYERS
        # ---------------------------------------------------------
        
        # Field 5: Force Field 3 to ONLY apply to domain_top
        gmsh.model.mesh.field.add("Restrict", 5)
        gmsh.model.mesh.field.setNumber(5, "InField", 3)
        gmsh.model.mesh.field.setNumbers(5, "SurfacesList", [domain_top])

        # Field 6: Force Field 4 to ONLY apply to domain_bot
        gmsh.model.mesh.field.add("Restrict", 6)
        gmsh.model.mesh.field.setNumber(6, "InField", 4)
        gmsh.model.mesh.field.setNumbers(6, "SurfacesList", [domain_bot])

        # Field 7: Take the minimum of the restricted fields
        gmsh.model.mesh.field.add("Min", 7)
        gmsh.model.mesh.field.setNumbers(7, "FieldsList", [5, 6])
        gmsh.model.mesh.field.setAsBackgroundMesh(7)
        
        # --- CRITICAL FLAGS FOR BACKGROUND MESH ---
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
        
        # Force pure triangles and use Frontal-Delaunay (Alg 6)
        gmsh.option.setNumber("Mesh.RecombineAll", 0)
        gmsh.option.setNumber("Mesh.Algorithm", params.get("algorithm", 6))
        gmsh.option.setNumber("Mesh.MshFileVersion", 2.2) 

        gmsh.model.mesh.generate(2)

        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "layered_mesh.msh")
            gmsh.write(path)
            mesh = readGmsh(path, verbose=params.get("verbose", False))
            mesh = mt.appendTriangleBoundary(mesh, marker=0, 
                                             xbound=2*extension, ybound=1.5*depth, isSubSurface=True)

    finally:
        gmsh.finalize()

    return mesh

def test_build_MCM_M2m():
    paths = ProjectPaths(user='AQ96560')            
    
    geom_mono2m = load_geometry(paths.MCM_MONO2M_ELECS_POS_TRUE, params={
        "absolute_pos": True, 
        'inverse_order': False,
        "projection": {"type": "distance", "output_axis": "X"}
    })

    # Call the new layered Gmsh builder
    mesh = build_gmsh_layered(
        df=geom_mono2m,
        depth=30.0,
        interface_depth=4.0, # The depth of your tailings/overburden boundary
        extension=10.0,
        size_surface=0.3,    # High density near electrodes
        size_interface=1.0,  # Medium density at interface
        size_depth=15.0       # Coarse at depth
    )
    
    mesh_polygons = extract_polygons(mesh)
    
    # Create a quick dummy array based on the region markers (2 and 3) 
    # just to visualize the structural boundary in matplotlib
    markers = np.array([c.marker() for c in mesh.cells()])
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax, coll = plot_array_on_mesh(mesh_polygons, array=markers, ax=ax, cmap='viridis', edgecolor='black', alpha=0.5)
    
    plot_sensors(geom_mono2m, ax)
    
    # Save it safely
    # mesh_path_str = str(paths.OUTPUT_DIR / 'MCM_MONO2M_Layered.bms').replace('\\', '/')
    # safe_mesh_save(mesh, mesh_path_str)
    
    print(f"Mesh has {mesh.cellCount()} cells and {mesh.nodeCount()} nodes.")
    
    # Use PyGIMLi's native viewer to verify the boundary markers (-1, -2, 10)
    ax, _ = pg.show(mesh, markers=True, showMesh=True)
    ax.set_ylim(-50, 10)

if __name__ == "__main__":
    test_build_MCM_M2m()
    plt.show()