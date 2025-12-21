# -*- coding: utf-8 -*-
# تم توليد هذا الملف بواسطة Thrift Compiler (0.11.0)
# هذا الملف يحتوي على الثوابت البرمجية العامة للمكتبة
# قمنا بتعريب التعليقات لتوضيح دور الملف في ربط البيانات

from thrift.Thrift import TType, TMessageType, TFrozenDict, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec

import sys
from .ttypes import * # استيراد أنواع البيانات المعربة التي تمثل الثوابت

# ملاحظة: هذا الملف عادة ما يكون فارغاً من القيم المباشرة في بروتوكول LINE 
# ولكنه يعمل كجسر (Bridge) لاستدعاء الثوابت من ملف ttypes.py
