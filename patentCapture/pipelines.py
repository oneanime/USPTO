# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
from patentCapture.items import *
from scrapy.utils.project import get_project_settings
import os
import json
import pandas as pd


# 保存被引用的专利的url到citiedurl文件夹下
class SaveToJsonPipeline(object):
    def process_item(self, item, spider):
        # 配置文件对象，读取项目配置文件的数据
        settings = get_project_settings()
        citied_list = item['cited_list']
        url_list = list()
        if citied_list is not None:
            for c in citied_list:
                url_list.append(c['detail_url'])
            if len(url_list):
                path_join = os.path.join(settings['DOWNLOAD_CITIE_URL_DIR'], item['detail_item']['patnr'] + '.json')
                with open(path_join, 'w') as f:
                    json.dump({'url': url_list}, f)
                f.close()
        return item


# 保存网页的response
class SaveToHtmlPipeline(object):
    def process_item(self, item, spider):
        settings = get_project_settings()
        page_dir = settings['DOWNLOAD_PAGE_DIR']
        path_join = os.path.join(page_dir, item['detail_item']['patnr'] + '.html')
        with open(path_join, 'wb') as f:
            f.write(item['detail_item']['response'])
        f.close()
        return item


# 清理传过来的数据
class CleanPipeline(object):

    def process_item(self, item, spider):
        detail_item = item['detail_item']
        try:
            assignee = detail_item['assignee']
            assignee = list(filter(lambda x: x.strip() != '', assignee))
            assignee = [i.replace('\n', '') for i in assignee]
            detail_item['assignee'] = assignee
            inventors = detail_item['inventors']
            inventors = list(filter(lambda x: x.strip() != '', inventors))
            inventors = [i.strip() for i in inventors]
            detail_item['inventors'] = inventors
            us_patref = detail_item['us_patref']
            us_patref = list(filter(lambda x: x.strip() != '', us_patref))
            us_patref = [i.strip() for i in us_patref]
            detail_item['us_patref'] = us_patref
            foreign_patref = detail_item['foreign_patref']
            if foreign_patref is not []:
                foreign_patref = detail_item['foreign_patref']
                foreign_patref = list(filter(lambda x: x.strip() != '', foreign_patref))
                foreign_patref = [i.strip() for i in foreign_patref]
                detail_item['foreign_patref'] = foreign_patref
            litref = detail_item['litref']
            if litref is not None:
                litref = [i.strip() for i in litref]
                litref = list(filter(lambda x: x.strip() != '', litref))
                detail_item['litref'] = litref
        except Exception as e:
            print('CleanPipeline:' + detail_item['patnr'])
        finally:
            return item


# 专利著录基本信息表
class CreateTableTiPipeline(object):
    def __init__(self):
        self.flag = True

    def process_item(self, item, spider):
        ti_item = {}
        try:
            ti_item['nr'] = item['detail_item']['nr']
            ti_item['patnr'] = item['detail_item']['patnr']
            ti_item['ti'] = item['detail_item']['ti']
            ti_item['date'] = item['detail_item']['date'].strip()
            ti_item['year'] = ti_item['date'].split(',')[1] if ti_item['date'] is not None else None
            ti_item['ab'] = item['detail_item']['ab']
            ti_item['applnr'] = item['detail_item']['applnr']
            ti_item['filed'] = item['detail_item']['filed']
            ti_item['current_International_class'] = item['detail_item']['current_International_class']
            ti_item['field_of_search'] = item['detail_item']['field_of_search']
            ti_item['primary_examiner'] = item['detail_item']['primary_examiner']
            ti_item['assistant_examiner'] = item['detail_item']['assistant_examiner']
            ti_item['attorney'] = item['detail_item']['attorney']
            data_list = list()
            data_list.append(ti_item)
            df = pd.DataFrame(data_list)
            if self.flag is True:
                df.to_csv(path_or_buf=os.path.dirname(__file__) + '/exporters/ti.csv')
                self.flag = False
            else:
                df.to_csv(path_or_buf=os.path.dirname(__file__) + '/exporters/ti.csv', mode='a', header=None)
        except Exception as e:
            print('TiPipeline:' + item['detail_item']['patnr'])
        finally:
            return item


class CreateTableAssPipeline(object):
    def __init__(self):
        self.flag = True

    def process_item(self, item, spider):
        try:
            ass_item = AssItem()
            assignee = item['detail_item']['assignee']
            assignee = ''.join([i.replace('\n', '') for i in assignee])
            split_assignee = re.split(r'[()]', assignee)
            ass_item['assignee'] = split_assignee[0]
            ass_item['country'] = split_assignee[1].split(',')[1]
            ass_item['city'] = split_assignee[1].split(',')[0]
            data_list = list()
            data_list.append(ass_item)
            df = pd.DataFrame(data_list)
            if self.flag is True:
                df.to_csv(path_or_buf=os.path.dirname(__file__) + '/exporters/ass.csv')
                self.flag = False
            else:
                df.to_csv(path_or_buf=os.path.dirname(__file__) + '/exporters/ass.csv', mode='a', header=None)
        except Exception as e:
            print('CreateTableAssPipeline:' + item['detail_item']['patnr'])
        finally:
            return item


class CreateTableInvPipeline(object):
    def __init__(self):
        self.flag = True

    def process_item(self, item, spider):
        inventors = item['detail_item']['inventors']
        inventors = ''.join([i.replace('\n', '') for i in inventors])
        inventors = re.split(r'[()]', inventors)
        inventors = inventors[:-1]
        inventor = inventors[::2]
        zone = inventors[1::2]
        inv_base_item_list = list()
        for i, j in zip(inventor, zone):
            inv_base_item = InvBaseItem()
            inv_base_item['inventors'] = i
            inv_base_item['invnr'] = inventor.index(i) + int(1)
            inv_base_item['city'] = j.split(',')[0]
            inv_base_item['country'] = j.split(',')[1]
            inv_base_item_list.append(inv_base_item)
        inv_item = InvItem()
        inv_item['nr'] = item['detail_item']['nr']
        inv_item['inv_base_item'] = inv_base_item_list

        data_list = list()
        for i in inv_item['inv_base_item']:
            data_list.append({'nr': inv_item['nr'], 'inventors': i['inventors'], 'invnr': i['invnr'], 'city': i['city'],
                              'country': i['country']})
        df = pd.DataFrame(data_list)
        if self.flag is True:
            df.to_csv(path_or_buf=os.path.dirname(__file__) + '/exporters/inv.csv')
            self.flag = False
        else:
            df.to_csv(path_or_buf=os.path.dirname(__file__) + '/exporters/inv.csv', mode='a', header=None)
        return item


# 专利引用信息
class CreateTablePatRefPipeline(object):
    def __init__(self):
        self.flag = True

    def process_item(self, item, spider):
        pat_ref_item = item['detail_item']['us_patref']
        ref_item_list = list()
        for i, j, k in zip(pat_ref_item[::3], pat_ref_item[1::3], pat_ref_item[2::3]):
            ref_item = PatRefBaaseItem()
            ref_item['patnr'] = i
            ref_item['date'] = j
            ref_item['name'] = k
            ref_item['is_belong_us'] = 'Y'
            ref_item['refnr'] = pat_ref_item[::3].index(i) + int(1)
            ref_item_list.append(ref_item)
        foreign_patref_item = item['detail_item']['foreign_patref']
        if foreign_patref_item is not []:
            for i, j, k in zip(foreign_patref_item[::3], foreign_patref_item[1::3], foreign_patref_item[2::3]):
                ref_item = PatRefBaaseItem()
                ref_item['patnr'] = i
                ref_item['date'] = j
                ref_item['name'] = k
                ref_item['is_belong_us'] = 'N'
                ref_item['refnr'] = foreign_patref_item[::3].index(i) + int(1001)
                ref_item_list.append(ref_item)
        pat_ref = PatRefItem()
        pat_ref['nr'] = item['detail_item']['nr']
        pat_ref['ref_item_list'] = ref_item_list
        data_list = list()
        for i in pat_ref['ref_item_list']:
            data_list.append({'nr': pat_ref['nr'], 'patnr': i['patnr'], 'date': i['date'], 'name': i['name'],
                              'is_belong_us': i['is_belong_us'], 'refnr': i['refnr']})
        df = pd.DataFrame(data_list)
        if self.flag is True:
            df.to_csv(path_or_buf=os.path.dirname(__file__) + '/exporters/patref.csv')
            self.flag = False
        else:
            df.to_csv(path_or_buf=os.path.dirname(__file__) + '/exporters/patref.csv', mode='a', header=None)
        return item


# 非专利引用信息表
class CreateTableLitrefPipeline(object):
    def __init__(self):
        self.flag = True

    def process_item(self, item, spider):
        litref_list = item['detail_item']['litref']
        lit_base_item_list = list()
        for litref in litref_list:
            base_item = LitrefBaseItem()
            base_item['ref'] = litref
            base_item['refnr'] = litref_list.index(litref) + int(1)
            lit_base_item_list.append(base_item)
        litref_item = LitrefItem()
        litref_item['nr'] = item['detail_item']['nr']
        litref_item['litref_item_list'] = lit_base_item_list

        data_list = list()
        for i in litref_item['litref_item_list']:
            data_list.append({'nr': litref_item['nr'], 'ref': i['ref'], 'refnr': i['refnr']})
        df = pd.DataFrame(data_list)
        if self.flag is True:
            df.to_csv(path_or_buf=os.path.dirname(__file__) + '/exporters/litref.csv')
            self.flag = False
        else:
            df.to_csv(path_or_buf=os.path.dirname(__file__) + '/exporters/litref.csv', mode='a', header=None)
        return item
