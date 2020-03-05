from src.etl.ptt_crawler_etl import PttCrawlerEtl
from src.system.config_setting import ConfigSetting
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

config_setting = ConfigSetting()
log = config_setting.set_logger("[PttCrawler]")
log.info(datetime.now())

scheduler = BlockingScheduler()
@scheduler.scheduled_job('interval', id='my_job_id', minutes=1)
def time_trigger():
    ptt_crawler_etl = PttCrawlerEtl(100, 102, "PublicServan")
    ptt_crawler_etl.parse_articles()
scheduler.start()