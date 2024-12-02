from fastapi import FastAPI, Response, HTTPException
import os
from server.daily_to_rss import read_daily_json, to_rss_feed , read_latest_date
from loguru import logger

app = FastAPI()


@app.get('/rss/latest')
def get_latest_rss():
    """获取最新的RSS feed"""
    try:
        date = read_latest_date()
        return get_daily_rss(date)
    except Exception as e:
        logger.error(f"获取最新RSS时出错: {e}")
        raise HTTPException(status_code=500, detail="获取最新数据失败")


@app.get('/rss/daily/{date}')
def get_daily_rss(date: str):
    """获取指定日期的RSS feed"""
    
    # 验证日期格式
    if not date.isdigit() or len(date) != 8:
        logger.error(f"无效的日期格式，请使用YYYYMMDD格式: {date}")
        raise HTTPException(status_code=400, detail="无效的日期格式，请使用YYYYMMDD格式")
    
    # 生成RSS内容
    data = read_daily_json(date)
    if not data:
        logger.error(f"未找到 {date} 的数据")
        raise HTTPException(status_code=500, detail="数据处理错误")
    
    # 直接获取RSS字符串
    rss_content = to_rss_feed(data)
    if not rss_content:
        logger.error(f"RSS生成失败")
        raise HTTPException(status_code=500, detail="RSS生成失败")
    return Response(content=rss_content, media_type='application/xml')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=6008) 