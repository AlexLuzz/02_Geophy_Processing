from src.loaders.ert_loader import ERTLoader
from config.paths import ProjectPaths
from src.visualization.basic_plotting import plot_sensors
import matplotlib.pyplot as plt

def test_loading(source: str, file_path, load_function):
    """Test loading a single file using a specific loader function."""
    df = load_function(source, file_path)
    print(f"Shape: {df.shape}")
    print(df.head())

if __name__ == "__main__":
    # 1. Initialize your tools
    loader = ERTLoader()
    
    # Swap to 'alexi' if you are on your home computer
    paths = ProjectPaths(user='AQ96560') 
                    
    bb_geom = loader.load_geometry(paths.MCM_GEO_ELECS_POS)

    plot_sensors(bb_geom)

    plt.show()