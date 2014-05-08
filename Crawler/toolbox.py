'''
Created on 06.05.2014

@author: user
'''
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
    