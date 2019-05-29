#!/usr/bin/env python3
# Standard Library Imports
import argparse
import logging
from logging import config
import threading
from random import choice
import queue

# Third Party Imports
import requests
from colorama import init
from termcolor import colored

LOGGING_DICT = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "file_handler": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "mode": "w",
            "filename": "py_buster.log"  # /temp/py_buster.log
        }
    },
    "loggers": {
        "": {  # root logger
            "level": "DEBUG",
            "handlers": ["file_handler"],
            "propagate": True
        }
    }
}


def parse_args():
    parser = argparse.ArgumentParser(description="Python directory buster. Supply a wordlist with -wl "
                                                 "option and a target url")
    parser.add_argument("url", type=str,
                        help="Please enter a url that will be used to search for hidden directories")
    parser.add_argument("-ua", "--User_Agent", help="Set User Agent", type=str, required=False,
                        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                                " (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36")
    parser.add_argument("-proxy", "--proxy-file", default=None, required=False,
                        help="Path for proxy file. Proxies need to be separated by newline "
                             "and in username:password@ip:port or ip:port format.")
    parser.add_argument("-user", "--proxy_username", type=str, required=False, default=None,
                        help="Username for proxies. Only use if all proxies have same username and"
                             "if proxy file does not include user info. Ex. format, ip:port")
    parser.add_argument("-pass", "--proxy_password", type=str, required=False, default=None,
                        help="Password for proxies. Only use if all proxies have same pass and if "
                             "proxy file does not include user info. Ex. format, ip:port")
    parser.add_argument("-wl", "--wordlist", required=True, help="Path for word list file.")

    return parser.parse_args()


def read_proxy_file(proxy_file):
    with open(proxy_file, "r") as fi:
        proxy_list = ["http://" + proxy.rstrip() for proxy in fi.readlines()]
    return proxy_list


def read_wordlist_file(wordlist_file):
    with open(wordlist_file) as fi:
        wordlist = [word.rstrip() for word in fi.readlines()]
    return wordlist


def populate_url_queue(wordlist, _queue):
    for word in wordlist:
        try:
            _queue.put(args.url + "/" + word.rstrip())
        except AttributeError as e:
            pass
    # return _queue


def make_request(get_url):
    if args.proxy_file:
        proxy_list = read_proxy_file(args.proxy_file)
        if args.proxy_password:
            proxies = {"http": f"http://{args.proxy_username}:{args.proxy_password}@{choice(proxy_list)}",
                       "https": f"https://{args.proxy_username}:{args.proxy_password}@{choice(proxy_list)}"}
        else:
            proxies = {"http": f"http://{choice(proxy_list)}", "https": f"http://{choice(proxy_list)}"}
    else:
        proxies = None
    try:
        url = get_url(block=False)
    except queue.Empty as e:
        return
    headers = {"User_Agent": args.User_Agent}
    try:
        req = requests.get(url, headers=headers, proxies=proxies)
        if req.status_code == 200:
            logger.info(f"200 - {url}")
            print(colored(f"200 - {url}", "green"))
        elif req.status_code >= 400:
            pass
        else:
            logging.info(f"{req.status_code} - {url}")
    except requests.exceptions.ConnectionError as e:
        print(colored(f'Connection error for {url}. Check Logs for more details', 'red'))
        logger.exception(f"Connection error for {url}")
    q.task_done()


def bust_dir(_queue):
    wordlist = read_wordlist_file(args.wordlist)
    populate_url_queue(wordlist, _queue)
    print(f"{_queue.qsize()} items in queue")
    while _queue.qsize() > 0:
        print(_queue.qsize())
        for i in range(1, 10):
            thread = threading.Thread(target=make_request, args=(_queue.get,))
            threads.append(thread)
            thread.start()
        print(_queue.qsize())


if __name__ == "__main__":
    args = parse_args()
    init()
    logger = logging.getLogger(__name__)
    logging.config.dictConfig(LOGGING_DICT)
    q = queue.Queue()
    threads = []
    bust_dir(q)
