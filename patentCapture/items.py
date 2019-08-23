# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


# region 非专利引用
class LitrefItem(scrapy.Item):
    nr = scrapy.Field()
    litref_item_list = scrapy.Field()


class LitrefBaseItem(scrapy.Item):
    ref = scrapy.Field()
    fullref = scrapy.Field()
    refnr = scrapy.Field()


# endregion


# region 专利的引用表
class PatRefItem(scrapy.Item):
    nr = scrapy.Field()
    ref_item_list = scrapy.Field()


class PatRefBaaseItem(scrapy.Item):
    nr = scrapy.Field()
    patnr = scrapy.Field()
    date = scrapy.Field()
    name = scrapy.Field()
    is_belong_us = scrapy.Field()
    refnr = scrapy.Field()


# endregion


class CitingItem(scrapy.Item):
    patnr = scrapy.Field()
    tc = scrapy.Field()
    citing = scrapy.Field()


# 专利类别信息表
class UsClassItem(scrapy.Item):
    nr = scrapy.Field()
    usclass = scrapy.Field()
    classnr = scrapy.Field()


# 专利权人信息表
class AssItem(scrapy.Item):
    assignee = scrapy.Field()  # Assignee
    city = scrapy.Field()
    state = scrapy.Field()
    country = scrapy.Field()
    assnr = scrapy.Field()


# 专利基本信息表
class TiItem(scrapy.Item):
    nr = scrapy.Field()
    patnr = scrapy.Field()
    ti = scrapy.Field()
    year = scrapy.Field()
    date = scrapy.Field()
    ab = scrapy.Field()  # Abstract
    applnr = scrapy.Field()  # Appl. No.
    filed = scrapy.Field()
    current_International_class = scrapy.Field()  # Current International Class
    field_of_search = scrapy.Field()  # Field of Search
    primary_examiner = scrapy.Field()  # Primary Examiner
    assistant_examiner = scrapy.Field()  # Assistant Examiner
    attorney = scrapy.Field()  # Attorney, Agent or Firm


# region 发明人信息表
class InvItem(scrapy.Item):
    nr = scrapy.Field()
    inv_base_item = scrapy.Field()


class InvBaseItem(scrapy.Item):
    inventors = scrapy.Field()
    invnr = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    country = scrapy.Field()
# endregion


class ListItem(scrapy.Item):
    num = scrapy.Field()
    PAT_NO = scrapy.Field()
    title = scrapy.Field()
    detail_url = scrapy.Field()


class DetailItem(scrapy.Item):
    response = scrapy.Field()
    nr = scrapy.Field()
    patnr = scrapy.Field()
    ti = scrapy.Field()
    date = scrapy.Field()
    ab = scrapy.Field()  # Abstract
    applnr = scrapy.Field()  # Appl. No.
    filed = scrapy.Field()
    current_International_class = scrapy.Field()  # Current International Class
    field_of_search = scrapy.Field()  # Field of Search
    primary_examiner = scrapy.Field()  # Primary Examiner
    assistant_examiner = scrapy.Field()  # Assistant Examiner
    attorney = scrapy.Field()  # Attorney, Agent or Firm
    assignee = scrapy.Field()
    inventors = scrapy.Field()
    litref = scrapy.Field()
    us_patref = scrapy.Field()
    foreign_patref = scrapy.Field()


class PatentcaptureItem(scrapy.Item):
    list_item = scrapy.Field()
    detail_item = scrapy.Field()
    cited_list = scrapy.Field()
