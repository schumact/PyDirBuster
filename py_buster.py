#!/usr/bin/env python3
# Standard Library Imports
import argparse
import asyncio
from random import choice
import logging
from logging import config

# Third Party Imports
import aiohttp
from aiohttp import client_exceptions
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
                             "and in url format. http://user:pass@ip:port or http://ip:port for no auth")
    parser.add_argument("-user", "--proxy-username", type=str, required=False, default=None,
                        help="Username for proxies. Only use if all proxies have same username")
    parser.add_argument("-pass", "--proxy-password", type=str, required=False, default=None,
                        help="Password for proxies. Only use if all proxies have same pass")
    parser.add_argument("-wl", "--wordlist", required=True, help="Path for word list file.")

    return parser.parse_args()


async def fetch(session, url, proxy, proxy_auth):
    try:
        resp = await session.get(url, proxy=proxy, proxy_auth=proxy_auth)
        if resp.status == 200:
            logger.info(f"{resp.status} - {url}")
            print(colored(f"{resp.status} - {url}", "green"))
        elif resp >= 400:
            pass
        else:
            logging.info(f"{resp.status} - {url}")
        resp.close()
    except (client_exceptions.ClientHttpProxyError, client_exceptions.ClientConnectionError) as e:
        #  TODO log error message here. For now, leave print statement
        print(colored(f"Issue when accessing {url}. Check logs for info", "red"))
        logging.exception(f"Issue accessing {url}")


def read_proxy_file(proxy_file):
    with open(proxy_file, "r") as fi:
        proxy_list = ["http://" + proxy.rstrip() for proxy in fi.readlines()]
    return proxy_list


def read_wordlist_file(wordlist_file):
    with open(wordlist_file) as fi:
        wordlist = [word.rstrip() for word in fi.readlines()]
    return wordlist


async def create_tasks(url):
    headers = {"User-Agent": args.User_Agent}
    tasks = []
    wordlist = read_wordlist_file(args.wordlist)
    async with aiohttp.ClientSession(headers=headers) as session:
        if args.proxy_file:
            proxy_list = read_proxy_file(args.proxy_file)
            if args.proxy_password:
                proxy_auth = aiohttp.BasicAuth(args.proxy_username, password=args.proxy_password)
            else:
                proxy_auth = None
            for word in wordlist:
                tasks.append((fetch(session, url + "/" + word, choice(proxy_list), proxy_auth)))
        else:
            for word in wordlist:
                tasks.append((fetch(session, url + "/" + word, None, None)))
        tasks = await asyncio.gather(*tasks, return_exceptions=True)
        return tasks


if __name__ == "__main__":
    args = parse_args()
    init()
    logger = logging.getLogger(__name__)
    logging.config.dictConfig(LOGGING_DICT)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_tasks(args.url))
