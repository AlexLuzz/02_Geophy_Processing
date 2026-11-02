from config.paths import ProjectPaths
from src.visualization.DAS.das_taptest_report import TaptestReport
import pandas as pd

if __name__ == "__main__":
    paths = ProjectPaths(user='AQ96560', project_name='DAS_MCM_Tap_test') 
    
    das_files = [
        #"SR_DS_2026-10-28_18-32-41_UTC.h5",
        #"SR_DS_2026-10-28_18-42-41_UTC.h5",
        #"SR_DS_2026-10-28_18-52-41_UTC.h5",
        #"SR_DS_2026-10-28_19-12-41_UTC.h5",
        "SR_DS_2026-10-28_19-22-41_UTC.h5",
        "SR_DS_2026-10-28_19-32-41_UTC.h5",
        #"SR_DS_2026-10-28_19-42-41_UTC.h5",
        #"SR_DS_2026-10-28_19-52-41_UTC.h5",
        #"SR_DS_2026-10-28_20-02-41_UTC.h5"
        ]

    das_files = [paths.MCM_DAS_TAP_TEST_DATA / f for f in das_files]

    csv_arpentage = pd.read_csv(
        paths.MCM_DAS_TAP_TEST_ARPENTAGE / "MCM_2026A2_TapTest_XYZ.csv",
        sep=";")


    for das_file in das_files:
        timestamp = das_file.stem.replace("SR_DS_2026-", "")
        report = TaptestReport.print(
            folder_path=paths.ACTIVE_PROJECT_DIR,
            survey_csv=csv_arpentage,
            file_list=das_files,
            )