'''
Created on 06.05.2014

@author: user
'''
import calendar
from datetime import datetime, date
from scrapy import log


def substring(s, leftDelimiter, rightDelimiter):
    """extracts substrings in string that are enclosed by leftDelimiter an rightDelimiter.
    multiple appearances of the delimiters are handeled as well.
    example: "live long and prosper" with delimiter "l" and " " will result in ["ive", "ong"]
    all parameters must be strings
    """
    if isinstance(s, str) and isinstance(leftDelimiter, str) and isinstance(rightDelimiter, str):
        result = []
        leftBorder = 0
        rightBorder = 0
        while True:
            leftBorder = s.find(leftDelimiter, rightBorder)
            if leftBorder == -1:
                break
            rightBorder = s.find(rightDelimiter, leftBorder+len(leftDelimiter))
            result.append(s[leftBorder+len(leftDelimiter):rightBorder])
            leftBorder = rightBorder + 1
        return result
    else:
        log.msg("invalid parametertype used", level=log.DEBUG)
        raise Exception("one or more parameter are not of type str")

def mergeListElements(item):
    """merges n elements of item into one.
    e.g. ["f", "o", "o"] becomes ["foo"].
    item must be a list.
    """
    if isinstance(item, list):
        newItem = ""
        for i in item:
            newItem += i
        return [newItem]
    else:
        log.msg("item is not a list", level=log.DEBUG)
        raise Exception("item is not a list")

def safepop(o, element):
    if hasattr(o, "pop") and type(element)==int:
        if len(o) > 0 and len(o) > element:
            return o.pop(element)
    else:
        return None

def add_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return date(year,month,day)

def validate_date_range(startDate, endDate):
    try:
        start = datetime.strptime(startDate, "%Y-%m")
        end = datetime.strptime(endDate, "%Y-%m")
    except ValueError:
        raise ValueError("The Date-Inputformat is invalid. yyyy-mm is expected.")
    if (end - start).days < 0:
        raise ValueError("The enddate is prior the startdate.")
    return start, end

def init_logger():
    log.start(loglevel='WARNING', logstdout=False)