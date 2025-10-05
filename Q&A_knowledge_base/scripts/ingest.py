#!/usr/bin/env python
import argparse
from lr.logging_setup import setup_logging
from lr.io.readers import gather_input
from lr.rag.retrieve import index_texts

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", default="./input")
    args = parser.parse_args()
    setup_logging()
    pairs = gather_input(args.folder)
    res = index_texts(pairs)
    print(res)

if __name__ == "__main__":
    main()
