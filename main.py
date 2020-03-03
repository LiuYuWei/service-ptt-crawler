from src.etl.ptt_crawler_etl import PttCrawlerEtl

if __name__ == "__main__":
    ptt_crawler_etl = PttCrawlerEtl(100, 102, "PublicServan")
    ptt_crawler_etl.parse_articles()