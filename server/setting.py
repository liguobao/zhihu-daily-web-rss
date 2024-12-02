import os
def get_data_dir():
    return "./zhihu_daily_data" if not os.getenv("DATA_DIR") else os.getenv("DATA_DIR")