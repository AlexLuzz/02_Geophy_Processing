
from src.loaders.das_loader import DASLoader 
from config.paths import ProjectPaths

paths = ProjectPaths(user='AQ96560', project_name='DAS_MCM_Tap_test') 
    
das_file = paths.MCM_DAS_TAP_TEST_DATA / "SR_DS_2026-10-28_18-32-41_UTC.h5"

loader = DASLoader(site_id="MCM_DAS_TapTest")
data = loader.load_h5(source=das_file)
meta, data = loader.retrieve_febus_h5(show=True)