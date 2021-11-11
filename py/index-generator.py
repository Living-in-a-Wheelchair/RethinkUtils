import tika
tika.initVM()
from tika import parser
import os
import sqlite3
from pybloom import BloomFilter
import re
import pickle
import json

REINDEX = False
MAIN_PATH = "C:\\Users\\arman\Documents\\ProjectRogerFaulknerRethink\\IPFS_Roger_Dropbox_Archive_Proprietary"
IPFS_FOLDER = "QmZG4ktRNuvptneiYDFDzjL3Ssd9FUS4BnJeEYQmhfXDqE" # with this, then we can call the ipfs files using ipfs get $IPFS_FOLDER/<usual filesystem path from the root directory>

def get_file_paths(verbose=False):
    count = 0
    paths = []
    # Also, blacklist hidden directions and files (starting with .) and files like DS_STORE or _MACOSX.
    directory_blacklist = ["rethink secrecy"]
    path_to_name = {}
    for root, directory_name, file_names in os.walk(MAIN_PATH):
        for file_name in file_names:
            file_path = os.path.join(root, file_name)
            if verbose:
                print(file_path)
            if any([dir not in file_path for dir in directory_blacklist]):
                # Filters out paths containing "rethink secrecy" in the name
                paths.append(file_path)
                path_to_name[file_path] = file_name
                count += 1
    if verbose:
        print("Number of files to process: {}".format(count))
    return paths, path_to_name

def process(paths, path_to_name, verbose=False):
    # con = sqlite3.connect("index.db")
    # cur = con.cursor()
    # cur.execute('''''') # Create a table
    files = {}
    for file_path in paths:
        parsed = parser.from_file(file_path)
        content = str(parsed["content"])
        if verbose:
            # TODO: Figure out what all those five-word files are called and blacklist them from get_file_paths().
            # TODO: Only process certain files that Tika supports
            print("{} contains {} words".format(path_to_name[file_path], parsed["content"]))
        files[file_path] = content
    # I should add more processing steps like stemming and removing common words (a, the, etc). https://www.stavros.io/posts/bloom-filter-search-engine/
    # Change from list to set
    processed_files = {name: list(re.split("\W+", contents.lower())) for name, contents in files.items()}
    return processed_files

def create_filters(processed_file_texts):
    filters = {}
    for name, words in processed_file_texts.items():
        filters[name] = BloomFilter(capacity=len(words), error_rate=0.1)
        for word in words:
            filters[name].add(word)
    return filters

def search(filters, search_string):
    search_terms = re.split("\W+", search_string)
    return [name for name, filter in filters.items() if all(term in filter for term in search_terms)]

if __name__ == "__main__":
    if REINDEX:
        file_paths, path_to_name = get_file_paths(verbose=True)
        processed_file_texts = process(file_paths, path_to_name, verbose=True)
        bloom_filters = create_filters(processed_file_texts)
        with open("filters.pickle", "wb") as handle:
            pickle.dump(bloom_filters, handle, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        with open("filters.pickle", "rb") as handle:
            filters = pickle.load(handle)
        # print(len(search(filters, "coal gasification")))
        file_paths, path_to_name = get_file_paths(verbose=True)
        processed_file_texts = process(file_paths, path_to_name, verbose=True)
        procfile_dumps = json.dumps(processed_file_texts)
        print(procfile_dumps)

