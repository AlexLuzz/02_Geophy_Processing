from config.paths import ProjectPaths
from src.loaders.ert_loader import ERTLoader
from src.loaders.ert_loading_tools import load_geometry
from src.visualization.raw_data_report import RawDataReport
from datetime import datetime

import pandas as pd

def process_ert_site(site_id, geom_path, source_paths, offset_elec=None):
        """Helper function to load geometry, parse PRIME data, and export the raw data report."""
        
        geom = load_geometry(geom_path, params={
            "absolute_pos": True, 
            "inverse_order": False,
            "projection": {"type": "distance", "output_axis": "X"}})

        loader = ERTLoader(site_id=site_id, elec_pos=geom)
        
        load_kwargs = {}
        if offset_elec is not None:
            load_kwargs['offset_elec'] = offset_elec

        df = None
        for source in source_paths:
            df = loader.load_prime(source=source, **load_kwargs)

        temp_corr = False
        
        if temp_corr:
            t1, T1 = pd.Timestamp("2026-08-01 00:00"), 11
            t2, T2 = pd.Timestamp("2026-09-15 10:00"), 13
        
            df["temp_model"] = T1 + (T2-T1) * (
                (df["date_survey"]-t1) / (t2-t1))

            df["rhoa (Ohm.m)"] = df["rhoa (Ohm.m)"] * (
                1 + 0.02 * (df["temp_model"] - 11))

        rel = False

        if rel:
            ref = pd.Timestamp("2026-08-01 00:00")
            survey_dates = df["date_survey"].drop_duplicates()
            ref_survey = survey_dates.iloc[(survey_dates - ref).abs().argmin()]
            print(ref_survey)

            keys = ["A", "B", "M", "N"]

            r = df[df["date_survey"] == ref_survey][keys + ["rhoa (Ohm.m)"]]
            r = r.rename(columns={"rhoa (Ohm.m)": "rhoa_ref"})

            df = df.merge(r, on=keys, how="left")
            df["rhoa (Ohm.m)"] = (df["rhoa (Ohm.m)"] / df["rhoa_ref"] - 1) * 100

             
        suffix = site_id.split('_')[-1] 
        RawDataReport.print(
            filename=f"{today}_RawData_TLERT_{suffix}.pdf",
            folder_path=report_path,
            df=df,
            elec_pos=geom,
            #max_groups=10
            )

if __name__ == "__main__":
    paths = ProjectPaths(user='alexi') 

    report_path = paths.OUTPUT_DIR / "RAW_DATA_TLERT_MONOS" 
    report_path.parent.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")

    process_ert_site(
        site_id="MCM_MONO2M",
        geom_path=paths.MCM_MONO2M_ELECS_POS_TRUE,
        source_paths=[paths.TLERT_MONO2M_9011, paths.TLERT_MONO2M_7001])

    process_ert_site(
        site_id="MCM_MONO1M",
        geom_path=paths.MCM_MONO1M_ELECS_POS_TRUE,
        source_paths=[paths.TLERT_MONO1M_9012, paths.TLERT_MONO1M_7002],
        offset_elec=-40)