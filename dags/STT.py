pip install mecab_ko wordcloud pandas openpyxl konlpy
import os
import requests #naver CLOVA Speech API
import json     #naver CLOVA Speech API
import mecab_ko as MeCab
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import csv
import pandas as pd
from collections import Counter
from konlpy.tag import Okt
from PIL import Image
import numpy as np
