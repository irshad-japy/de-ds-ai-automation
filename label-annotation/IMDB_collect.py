# This script is used to prepare the IMDB dataset for sentiment analysis.
# To use - download the original dataset from
#
#   https://ai.stanford.edu/~amaas/data/sentiment/
#
# Place this script in the top level directory of that dataset, and run
#
#   python3 IMDB_collect.py
#
# This will parse the dataset into data.csv, with the following format
#
# Header columns:
#   'uid', 'id', 'stars', 'review', 'sentiment', 'type', 'filename', 'url'
# 
# Items     0 - 24999 : Labeled Training Data
# Items 25000 - 74999 : Unlabeled Training Data
# Items 75000 - 99999 : Labeled Test Data

import csv
import os
import re
import random

train_labeled = list(range(0,25000))
random.Random(1111).shuffle(train_labeled)

train_unlabeled = list(range(25000,75000))
random.Random(1122).shuffle(train_unlabeled)

test_labeled = list(range(75000,100000))
random.Random(1133).shuffle(test_labeled)

ids = [train_labeled, train_unlabeled, test_labeled]

id_indexes = [0,0,0]

usage = { 'train': 'Train', 'test': 'Test'}
sentiment = { 'pos': 'Positive', 'neg': 'Negative', 'unsup': '' }
id_reg = re.compile(r'(\d+)_(\d+).txt')

url_directory = {}

headers = ['uid', 'id', 'stars', 'review', 'sentiment', 'type', 'filename', 'url']
dataset = [headers]

for uname, utype in usage.items():
    for lname, ltype in sentiment.items():

        if lname == 'unsup': index = 1
        elif uname == 'test': index = 2
        else:index = 0

        urls_name = uname + '/' + 'urls_' + lname + '.txt'
        if os.path.exists(urls_name):
            with open(urls_name, 'r') as file:
                url_directory[uname+lname] = file.read().splitlines()
        for root, dirs, files in os.walk('./' + uname + '/' + lname):
            for name in files:
                match = id_reg.match(name)
                if match:
                    fname = os.path.join(root, name)
                    dataid = match[1]
                    stars = match[2]
                    with open(fname, 'r') as file:
                        data = file.read()
                        row = [
                            ids[index][id_indexes[index]],
                            dataid,
                            stars,
                            data,
                            ltype,
                            utype,
                            fname,
                            url_directory[uname+lname][int(dataid)]]
                    id_indexes[index] = id_indexes[index]+1
                    dataset.append(row)

def sort_func(x):
    if x[0] == 'uid':
        return -1
    else:
        return x[0]


dataset.sort(key=sort_func)

def write_csv(dataset, start, end, filename):
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows([dataset[0]])
        writer.writerows(dataset[start:end])

write_csv(dataset,1    ,100001, 'IMDB_data.csv')
write_csv(dataset,1    , 25001, 'IMDB_train_labeled.csv')
write_csv(dataset,1    ,   101, 'IMDB_train_labeled_100.csv')
write_csv(dataset,25001, 75001, 'IMDB_train_unlabeled.csv')
write_csv(dataset,25001, 25101, 'IMDB_train_unlabeled_100.csv')
write_csv(dataset,75001,100001, 'IMDB_test_labeled.csv')
write_csv(dataset,75001, 75101, 'IMDB_test_labeled_100.csv')