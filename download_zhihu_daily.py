from concurrent.futures import ThreadPoolExecutor
import os
import threading
import requests
from loguru import logger
import json
import datetime
fail_list = []


def load_stories_by_date(date_text):
  try:
    url = f"https://news-at.zhihu.com/api/7/stories/before/{date_text}?client=0"
    payload = {}
    headers = {
        'host': 'news-at.zhihu.com',
        'x-uuid': '79524F3F-096F-4435-9663-F8CF7F898E5B',
        'authorization': 'Bearer M7l4cf42SKW7oNK2fx0mLg',
        'x-device': 'iPhone15,3/D74AP',
        'accept': '*/*',
        'x-os': 'iOS 18.1',
        'x-b3-traceid': 'BD89D9D081FC4D63',
        'x-b3-spanid': 'BD89D9D081FC4D63',
        'accept-language': 'zh-Hans-CN;q=1',
        'x-bundle-id': 'com.zhihu.daily',
        'x-api-version': '7',
        'user-agent': 'zhi hu ri bao/3.1.6 (iPhone; iOS 18.1; Scale/3.00)',
        'x-app-version': '3.1.6',
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
      # logger.info(
      #     f"load stories by date {date_text} successfully, response: {response.status_code}")
      return response.json()
    else:
      logger.error(
          f"load {date_text} fail, response: {response.status_code}")
      fail_list.append(date_text)
      return {}
  except Exception as e:
    logger.error(f"load {date_text} fail, error: {e}")
    return {}


def save_stories_by_date(date_text, stories):
  try:
    file_name = f"./zhihu_daily_data/{date_text}.json"
    if not stories:
      logger.error(f"{threading.current_thread().name} save {file_name} fail, stories is empty")
      return
    with open(file_name, "w+") as f:
      f.write(json.dumps(stories, indent=2, ensure_ascii=False))
    logger.info(f"{threading.current_thread().name} save {file_name} successfully")
  except Exception as e:
    logger.error(f"{threading.current_thread().name} save {file_name} fail, error: {e}")

def req_and_save_stories_by_date(date_text):
  file_name = f"./zhihu_daily_data/{date_text}.json"
  if os.path.exists(file_name):
    logger.w(f"{threading.current_thread().name} {file_name} already exists")
    return
  stories = load_stories_by_date(date_text)
  save_stories_by_date(date_text, stories)

def to_date_list(start_date="20240901"):
    now_date = datetime.datetime.now()
    start_date = datetime.datetime.strptime(start_date, "%Y%m%d")
    data_list = []
    for i in range((now_date - start_date).days + 1):
      data_list.append((start_date + datetime.timedelta(days=i)).strftime("%Y%m%d"))
    return data_list

if __name__ == "__main__":
  # 从今天往前推一个月
  old_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y%m%d")
  logger.info(f"start download zhihu daily data, old_date: {old_date}")
  data_list = to_date_list(old_date)
  logger.info(f"start download zhihu daily data, total: {len(data_list)}")
  threadPool = ThreadPoolExecutor(
      max_workers=32, thread_name_prefix="zhihu_daily")
  for date_text in data_list:
      future = threadPool.submit(req_and_save_stories_by_date, date_text)
  threadPool.shutdown(wait=True)
  logger.info(f"download zhihu daily data finished, data_list: {len(data_list)}")
  
