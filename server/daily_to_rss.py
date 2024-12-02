# 将知乎日报数据转换为rss格式
import os
import json
import xml.etree.ElementTree as ET
from loguru import logger
from datetime import datetime
from io import StringIO
import os
from server.setting import get_data_dir

def read_latest_date():
    daily_data_dir = get_data_dir()
    files = [f for f in os.listdir(daily_data_dir) if f.endswith('.json')]
    latest_file = max(files)
    date = latest_file.replace('.json', '')
    logger.info(f"最新日期: {date}")
    return date

def read_daily_json(date_text):
    daily_data_dir = get_data_dir()
    json_file_path = os.path.join(daily_data_dir, f"{date_text}.json")
    if not os.path.exists(json_file_path):
        logger.error(f"JSON文件不存在：{json_file_path}")
        return []
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data

def parse_hint(hint):
    """
    解析hint字段，提取作者和阅读时间
    示例输入: "Ace Zhu · 1 分钟阅读"
    返回: ("Ace Zhu", "1 分钟阅读")
    """
    if not hint:
        return ("未知作者", "未知阅读时间")
    parts = hint.split('·')
    if len(parts) == 2:
        author = parts[0].strip()
        reading_time = parts[1].strip()
        return (author, reading_time)
    else:
        return (hint.strip(), "未知阅读时间")

def to_rss_feed(data):
    """
    将知乎日报数据转换为RSS格式
    Args:
        data: 知乎日报JSON数据
    Returns:
        str: RSS内容的字符串，如果处理失败则返回空字符串
    """
    if not data:
        logger.error("没有有效的JSON数据可用于生成RSS。")
        return ""

    # 创建根元素
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')

    # 添加频道信息
    title = ET.SubElement(channel, 'title')
    title.text = "知乎日报"

    link = ET.SubElement(channel, 'link')
    link.text = "https://www.zhihu.com/daily"

    description = ET.SubElement(channel, 'description')
    description.text = "知乎日报的RSS订阅"

    language = ET.SubElement(channel, 'language')
    language.text = 'zh-cn'

    # 使用JSON中的日期作为最后构建日期
    lastBuildDate = ET.SubElement(channel, 'lastBuildDate')
    try:
        # 将日期格式从 "YYYYMMDD" 转换为 RSS 格式日期
        date_str = data.get('date', '')
        date_obj = datetime.strptime(date_str, "%Y%m%d")
        lastBuildDate.text = date_obj.strftime('%a, %d %b %Y 00:00:00 GMT')
    except ValueError:
        lastBuildDate.text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

    # 添加每一篇文章作为项目
    for story in data.get('stories', []):
        item_element = ET.SubElement(channel, 'item')
        
        item_title = ET.SubElement(item_element, 'title')
        item_title.text = story.get('title', '无标题')
        
        item_link = ET.SubElement(item_element, 'link')
        item_link.text = story.get('url', 'https://www.zhihu.com')
        
        item_description = ET.SubElement(item_element, 'description')
        # 解析hint字段
        hint = story.get('hint', '')
        author, reading_time = parse_hint(hint)
        # 如果有图片，则在描述中加入图片
        images = story.get('images', [])
        if images:
            image_html = f'<img src="{images[0]}" alt="{story.get("title", "图片")}" /><br/>'
        else:
            image_html = ''
        # 添加作者和阅读时间信息
        author_reading_html = f'<p>作者：{author}</p><p>阅读时间：{reading_time}</p>'
        item_description.text = image_html + author_reading_html + story.get('hint', '无描述')
        
        # 使用故事的ID作为唯一标识符
        guid = ET.SubElement(item_element, 'guid')
        guid.text = str(story.get('id', ''))
        guid.set('isPermaLink', 'false')

        # 如果有发布时间，可以加入pubDate
        pubDate = ET.SubElement(item_element, 'pubDate')
        pubDate.text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    # 生成XML字符串
    try:
        output = StringIO()
        tree = ET.ElementTree(rss)
        tree.write(output, encoding='unicode', xml_declaration=True)
        return output.getvalue()
    except Exception as e:
        logger.error(f"生成RSS feed时发生错误: {e}")
        return ""

if __name__ == "__main__":
    json_path = "zhihu_daily_data/20130520.json"
    rss_path = "output/rss_20130520.xml"
    
    data = read_daily_json(json_path)
    rss_content = to_rss_feed(data)
    if rss_content:
        with open(rss_path, 'w', encoding='utf-8') as f:
            f.write(rss_content)
