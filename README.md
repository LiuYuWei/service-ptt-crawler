# service-ptt-crawler
Use python to craw the ptt content.

## Demand:

- [ ] 每筆 row data 必須確保是 unique
- [ ] 須考慮機器如因不可預期狀況停機,後續如何追朔未擷取之資料
- [ ] 須考慮爬蟲會被部署在多台機器架構下的狀況
- [ ] 須考量如何監控爬蟲狀態及相關異常通知
- [X] 須考量如何才能概括大部份的分類看板<br>
(在src/etl/ptt_crawler_etl.py去做呈現)
- [X] 須考量如何避免因過度快速擷取頁面而造成的網路資安問題<br>
(解決方式:透過time.sleep3秒讓爬蟲速度降低，如有需要可以對秒數進行random，讓動作更像是人在作業的樣子)

## How to use this?
- build the docker images:
```bash
$ docker build -t="service-ptt-crawler" .
```
- Run the docker container:
```bash
$ docker run --rm -v "$PWD":/home/app/workdir --name "service-ptt-crawler" service-ptt-crawler
```