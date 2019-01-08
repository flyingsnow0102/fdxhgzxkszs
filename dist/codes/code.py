#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author: kraho
@license: LGPL
@contact: kraho@outlook.com
@software: None
@file: code.py
@time: 2019年1月7日 13点18分
@desc: 一个帮助FD信号工在线考试的脚本
'''
from collections import namedtuple
import os, os.path
import re
import xlrd
import logging, myloggingConfig

logger = logging.getLogger(__name__)
Question = namedtuple("Question", 'index content options answer notes')

class Questions(object):
    def __init__(self, path):
        self.__path = path
        self.__questions = []
        if 'xls' == self.__path.split(".")[1]:
            '''通过xls生成题库'''
            self.__from_xls()

        elif 'txt' == self.__path.split(".")[1]:
            '''通过txt生成试卷'''
            self.__from_txt()

    @property
    def questions(self):
        return self.__questions

    def __from_txt(self):
        '''读取txt试卷'''
        with open(self.__path, 'r',encoding='UTF-8') as fp:
            text = fp.read()
        docs = re.findall(r'显示全部未答已答标记隐藏全部(.*)点击展开答题卡>> 答题卡', text, re.S)[0]
        sections = docs.split('显示全部未答已答标记隐藏全部')
        for section in sections:
            header = re.findall(r'.*题（每题\d+分，共\d+题）', section)[0]
            section = section.replace(header, "", 1)
            questions = re.findall(r'(^\d+)(.*)', section, re.M)
            if "判断" not in header:
                items = re.findall(r'(^A..*|^B..*|^C..*|^D..*|^E..*|^F..*)+(B..*)?(C..*)?(D.*)?(E..*)?(F..*)?', section, re.M)
                itemls = []
                for item in items:
                    if re.match(r'^A.*', item[0]):
                        itemls.append(" ".join(item).strip())
                        if len(itemls) > 1:
                            itemls[-1] = re.sub(r'\s+', " ", itemls[-1])
                        # else:
                        #     pass
                    else:
                        itemls[-1] += " %s"%(" ".join(item).strip())
                if len(questions) == len(itemls):
                    for key, value in enumerate(questions):
                        # print(value[0], value[1])
                        # print(itemls[key])
                        self.__questions.append(Question(index=int(value[0]), content=re.sub(r'\s+', '', value[1]), options=itemls[key], answer="", notes=""))
                # else:
                #     pass
            else:
                for value in questions:
                    # print(value[0], value[1])
                    self.__questions.append(Question(index=int(value[0]), content=re.sub(r'\s+', '', value[1]), options="", answer="", notes=""))

    def __from_xls(self):
        """获取excel数据源"""
        try:
            book = xlrd.open_workbook(self.__path)
            #抓取所有sheet页的名称
            # worksheets = book.sheet_names()
            # print("该Excel包含的表单列表为：\n")
            # for sheet in worksheets:
            #     print ('%s,%s' %(worksheets.index(sheet),sheet))
            # inp = input('请输入表单名对应的编号，对应表单将自动转为json:')
            sheet = book.sheet_by_index(0)
            header = sheet.row(0)    #第一行是表单标题
            nrows=sheet.nrows       #行号
            ncols=sheet.ncols       #列号   
            if 10 == ncols and "序号题目内容选项A选项B选项C选项D选项E选项F标准答案答案说明" == "".join([x.value for x in header]):
                for i in range(1, nrows):
                    record = [int(x.value) if 2 == x.ctype and 0.0 == x.value % 1 else x.value for x in sheet.row(i)]
                    temp = Question(index=record[0], content=re.sub(r'\s+', '', record[1]), options=" ".join([str(x) for x in record[2:8]]).strip(), answer=record[8], notes=record[9])
                    self.__questions.append(temp)
            else:
                print("题库文件不符合标准")

        except Exception as e:
            print('初始化题库失败：%s' %e)

    def __repr__(self):
        return '<Questions length = %d>'%len(self.__questions)

    def __getitem__(self, position):
        return self.__questions[position]

    def contains(self, ques):
        '''贪婪的匹配'''
        content = ques.content
        for item in self.__questions:
            if content in item.content:
                return item
        return None

    def equal(self, ques):
        '''严格的匹配'''
        content = ques.content
        for item in self.__questions:
            if content == item.content:
                return item
        return None


if __name__ == "__main__":
    basedir = os.getcwd()
    paper_path = os.path.join(basedir, 'sources', 'paper.txt')
    bank_path = os.path.join(basedir, 'sources', 'bank.xls')
    bank = Questions(bank_path)
    paper = Questions(paper_path)

    ''' 模式配置avaricious
        True: 贪婪模式，子串匹配
        False： 非贪婪模式，整串匹配
    '''
    avaricious = True
    answers = []
    for ques in paper:
        logger.info("[QUES][%03d][ ]%s"%(ques.index, ques.content))
        if avaricious:
            result = bank.contains(ques)
        else:
            result = bank.equal(ques)
        if result is not None:
            logger.info("[BANK][%03d][%s]%s"%(result.index, result.answer, result.content))
            answers.append(result.answer)
        else:
            logger.info("None")
            answers.append("*")
        # answers.append(Answer(index=ques.index, answer=result.answer)) if result else answers.append(Answer(index=ques.index, answer="*"))
    print('以下答案仅供参考，其中*表示答案未知，请自行解答')
    print("贪婪模式：%r"%avaricious)
    for key, value in enumerate([answers[i:i + 5] for i in range(0, len(answers), 5)]):
        print("%2d-%2d"%(key*5+1, key*5+5), "  ".join(value))
    print("完整解答请看./logs最新日志")
    input("Press Enter to Exit!")