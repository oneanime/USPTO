# -*- coding: utf-8 -*-

import scrapy
from scrapy.selector import Selector
from copy import deepcopy
from urllib import parse
from patentCapture.items import *
import re


class UspatentSpider(scrapy.Spider):
    name = 'uspatent'
    allowed_domains = ['www.uspto.gov/']
    start_urls = ['http://patft.uspto.gov']

    def parse(self, response):
        advanced_search_url = response.xpath(
            '//div[@class="f01"][1]//a[text()="Advanced Search"]/@href').extract_first()
        advanced_search_url = parse.urljoin(base=self.start_urls[0], url=advanced_search_url)
        yield scrapy.Request(advanced_search_url,
                             callback=self.advanced_search_parse,
                             dont_filter=True)

    def advanced_search_parse(self, response):
        # query_url = response.xpath('//form/@action').extract_first()
        # query_url = parse.urljoin(base=self.start_urls[0], url=query_url)
        # query_string_parameters = {
        #     'Sect1': 'PTO2',
        #     'Sect1': 'HITOFF',
        #     'u': '/netahtml/PTO/search-adv.htm',
        #     'r': 0,
        #     'p': 1,
        #     'f': 'S',
        #     'l': 50,
        #     'Query': r'((TTL/((blu-ray OR bluray) ANDNOT (hd-dvd OR hddvd)) OR ABST/((blu-ray OR bluray) ANDNOT (hd-dvd OR hddvd))) OR SPEC/((blu-ray OR bluray) ANDNOT (hd-dvd OR hddvd)))',
        #     'd': 'PTXT'
        # }
        # query_string = parse.urlencode(query_string_parameters)
        # query_url = query_url + '?' + query_string
        # print(query_url)
        query_url = 'http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=0&p=1&f=S&l=50&Query=ttl%2F%28%28blu-ray+or+bluray%29+andnot+%28hd-dvd+or+hddvd%29%29+or+abst%2F%28%28blu-ray+or+bluray%29+andnot+%28hd-dvd+or+hddvd%29%29+or+spec%2F%28%28blu-ray+or+bluray%29+andnot+%28hd-dvd+or+hddvd%29%29&d=PTXT'
        yield scrapy.Request(url=query_url,
                             callback=self.result_list_parse,
                             dont_filter=True)

    # 解析列表页
    def result_list_parse(self, response):
        tr_list = response.xpath('//body/table//tr')
        for tr in tr_list[1:]:
            list_item = ListItem()
            list_item['num'] = tr.xpath('.//td[1]/text()').extract_first()
            list_item['PAT_NO'] = tr.xpath('.//td[2]/a/text()').extract_first()
            list_item['detail_url'] = parse.urljoin(self.start_urls[0], tr.xpath('.//td[2]/a/@href').extract_first())
            list_item['title'] = tr.xpath('.//td[4]/a/text()').extract_first()
            # 跳转到详细页
            if list_item['detail_url'] is not None:
                yield scrapy.Request(url=list_item['detail_url'], callback=self.detail_parse,
                                     meta={'list_item': list_item}, dont_filter=True)
        # 跳到下一页
        next_url = response.xpath(r'//img[@alt="[NEXT_LIST]"]/../@href').extract_first()
        if next_url is not None:
            next_url = parse.urljoin(self.start_urls[0], next_url)
            yield scrapy.Request(url=next_url, callback=self.result_list_parse, dont_filter=True)

    def detail_parse(self, response):
        list_item = response.meta['list_item']
        detail_item = DetailItem()
        detail_item['response'] = response.body
        detail_item['nr'] = 'nr' + list_item['num']
        detail_item['patnr'] = list_item['PAT_NO']
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
        item['list_item'] = list_item
        item['detail_item'] = detail_item
        item['cited_list'] = None
        # region 跳转到被引用的专利页面
        references_cited_url = response.xpath('//a[text()="[Referenced By]"]/@href').extract_first()
        if references_cited_url is not None:
            references_cited_url = parse.urljoin(self.start_urls[0], references_cited_url)
            yield scrapy.Request(url=references_cited_url, callback=self.cited_list_parse,
                                 meta={'item': deepcopy(item)},
                                 dont_filter=True)
        else:
            yield item
        # endregion

    def cited_list_parse(self, response):
        item = response.meta['item']
        item['cited_list'] = list()
        # 判断是否只有一条被引用，只有一条被引用的话，会直接重定向到详情页，如果跳到了详情页就会有[Referenced By]
        if response.xpath('//a[text()="[Referenced By]"]/@href').extract_first() is None:
            tr_list = response.xpath('//body/table//tr')
            for tr in tr_list[1:]:
                list_item = ListItem()
                list_item['num'] = tr.xpath('.//td[1]/text()').extract_first()
                list_item['PAT_NO'] = tr.xpath('.//td[2]/a/text()').extract_first()
                list_item['detail_url'] = parse.urljoin(self.start_urls[0],
                                                        tr.xpath('.//td[2]/a/@href').extract_first())
                list_item['title'] = tr.xpath('.//td[4]/a/text()').extract_first()
                item['cited_list'].append(list_item)
            next_url = response.xpath(r'//img[@alt="[NEXT_LIST]"]/../@href').extract_first()
            if next_url is not None:
                next_url = parse.urljoin(self.start_urls[0], next_url)
                yield scrapy.Request(url=next_url,
                                     callback=self.cited_list_parse,
                                     meta={'item': deepcopy(item)},
                                     dont_filter=True)
            else:
                yield item
        else:
            list_item = ListItem()
            list_item['num'] = 1
            list_item['PAT_NO'] = response.xpath(
                '//table//b[text()="United States Patent "]/../following-sibling::td/b/text()').extract_first()
            list_item['detail_url'] = response.url
            list_item['title'] = response.xpath('//body/font/text()').extract_first()
            item['cited_list'].append(list_item)
            yield item
