# -*- coding: utf-8 -*-
import scrapy
import os
import json
from scrapy import Selector
from scrapy.utils.project import get_project_settings

from patentCapture.items import *


class CitedpatentSpider(scrapy.Spider):
    name = 'citedpatent'
    allowed_domains = ['www.uspto.gov/']
    start_urls = []

    # 重写start_requests
    def start_requests(self):
        settings = get_project_settings()
        filename_list = [filename for filename in os.listdir(settings['DOWNLOAD_CITIE_URL_DIR'])]
        for filename in filename_list:
            with open(os.path.join(settings['DOWNLOAD_CITIE_URL_DIR'], filename), 'r') as f:
                json_load = json.load(f)
            for i in json_load['url']:
                yield scrapy.Request(i, meta={'origin_patnr': filename.split(r'.')[0]}, dont_filter=True)
        f.close()

    def parse(self, response):
        origin_patnr = response.meta['origin_patnr']
        detail_item = DetailItem()
        detail_item['response'] = response.body
        detail_item['nr'] = origin_patnr
        detail_item['patnr'] = response.xpath(
            '//table//b[text()="United States Patent "]/../following-sibling::td/b/text()').extract_first()
        detail_item['ti'] = response.xpath('//body/font/text()').extract_first()
        detail_item['date'] = response.xpath('//table[2]//tr[2]//td[@align="right"]/b/text()').extract_first()
        detail_item['ab'] = response.xpath(
            '//center/b[text()="Abstract"]/../following-sibling::p[1]/text()').extract_first()
        detail_item['applnr'] = response.xpath(
            "//th[contains(text(),'Appl. No')]/../td/b/text()").extract_first()
        detail_item['filed'] = response.xpath(
            "//th[contains(text(),'Filed')]/../td/b/text()").extract_first()
        detail_item['current_International_class'] = response.xpath(
            '//td/b[contains(text(),"Current International Class")]/../../td[@align="right"]/text()').extract_first()
        detail_item['field_of_search'] = response.xpath(
            '//td/b[contains(text(),"Field of Search")]/../../td[@align="right"]/text()').extract_first()
        detail_item['field_of_search'] = detail_item['field_of_search'].strip() if detail_item[
                                                                                       'field_of_search'] is not None else None
        detail_item['primary_examiner'] = Selector(response=response).re_first(r'<i>Primary Examiner:</i>(.*)')
        detail_item['assistant_examiner'] = Selector(response=response).re_first(r'<i>Assistant Examiner:</i>(.*)')
        detail_item['attorney'] = Selector(response=response).re_first(r'<i>Attorney, Agent or Firm:</i> <coma>(.*)')
        detail_item['assignee'] = response.xpath("//th[contains(text(),'Assignee')]/../td//text()").extract()
        detail_item['inventors'] = response.xpath("//th[contains(text(),'Inventors')]/..//td//text()").extract()
        detail_item['litref'] = response.xpath(
            '//center/b[text()="Other References"]/../following-sibling::tr//td//text()').extract()
        detail_item['us_patref'] = response.xpath(
            '//center/b[text()="U.S. Patent Documents"]/../following-sibling::table[1]//tr//td//text()').extract()
        detail_item['foreign_patref'] = response.xpath(
            '//center/b[text()="Foreign Patent Documents"]/../following-sibling::table[1]//tr//td//text()').extract()
        item = PatentcaptureItem()
        item['detail_item'] = detail_item
        item['list_item'] = None
        item['cited_list'] = None
        yield item
