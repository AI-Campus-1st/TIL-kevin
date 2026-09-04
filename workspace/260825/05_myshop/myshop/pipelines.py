# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


def clean_text(t):
    return t.strip()

class MyshopPipeline:
    def process_item(self, item):
        return item

class CleanPipeline:
    def process_item(self, item, spider):
        item["title"] = clean_text(item["title"])
        item["price"] = float(item["price"].replace("£", "").strip() or 0)
        return item

from itemadapter import ItemAdapter

class CsvPipeline:
    def open_spider(self, spider):
        self.f = open("out.csv", "w", encoding="utf -8-sig", newline="")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        return item
        # # 한줄씩기록
        # self.f.write(item['title']+','+str(item['price']) + '\n')

    def close_spider(self, spider):
        self.f.close()
