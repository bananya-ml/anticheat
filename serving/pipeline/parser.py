from awpy import DemoParser
import os
import pandas as pd


def parser(file_loc):

    demo_id = os.path.splitext(os.path.basename(file_loc))[0]
    demo_dir = os.path.join(
        "D:\\anticheat\\serving\\data", demo_id, "csv")
    json_dir = os.path.join(
        "D:\\anticheat\\serving\\data", demo_id, "json")

    os.makedirs(demo_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)

    demo_parser = DemoParser(file_loc, demo_id=demo_id,
                             parse_rate=128, outpath=json_dir)

    data = demo_parser.parse(return_type='df')

    for df_name, df in data.items():
        if isinstance(df, pd.core.frame.DataFrame):
            csv_filename = os.path.join(demo_dir, f"{df_name}.csv")
            df.to_csv(csv_filename, index=False)

    # Create a dataframe with the remaining items from the 'data' dictionary
    remaining_data = {k: v for k, v in data.items(
    ) if not isinstance(v, pd.core.frame.DataFrame)}
    info_df = pd.DataFrame.from_dict(
        remaining_data, orient='index', columns=['Value'])
    info_csv_filename = os.path.join(demo_dir, f"info.csv")
    info_df.to_csv(info_csv_filename, index=True, header=True)

    return demo_dir
