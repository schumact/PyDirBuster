# Standard Library Imports
import argparse
import asyncio
from random import choice

# Third Party Imports
import aiohttp
from aiohttp import client_exceptions


def parse_args():
    parser = argparse.ArgumentParser(description='Python directory buster. Supply a wordlist with -wl '
                                                 'option and a target url')
    parser.add_argument('url', type=str,
                        help='Please enter a url that will be used to search for hidden directories')
    parser.add_argument('-ua', '--User_Agent', help='Set User Agent', type=str, required=False,
                        default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                ' (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36')
    parser.add_argument('-proxy', '--proxy-file', default=None, required=False,
                        help='Path for proxy file. Proxies need to be separated by newline '
                             'and in url format. http://user:pass@ip:port or http://ip:port for no auth')
    parser.add_argument('-user', '--proxy-username', type=str, required=False, default=None,
                        help='Username for proxies. Only use if all proxies have same username')
    parser.add_argument('-pass', '--proxy-password', type=str, required=False, default=None,
                        help='Password for proxies. Only use if all proxies have same pass')
    parser.add_argument('-wl', '--wordlist', required=True, help='Path for word list file.')

    return parser.parse_args()


async def fetch(session, url, proxy, proxy_auth):
    try:
        resp = await session.request('GET', url, proxy=proxy, proxy_auth=proxy_auth)
        if resp.status == 200:
            print(url)
        else:
            # print(url + '      ', resp.status)
            pass

    except client_exceptions.ClientHttpProxyError as e:
        #  TODO log error message here. For now, leave print statement
        print(f'Issue when accessing {url}. Check logs for debug info')
        print(e.message)


def read_proxy_file(proxy_file):
    with open(proxy_file, 'r') as fi:
        proxy_list = ['http://' + proxy.rstrip() for proxy in fi.readlines()]
    return proxy_list


def read_wordlist_file(wordlist_file):
    with open(wordlist_file) as fi:
        wordlist = [word.rstrip() for word in fi.readlines()]
    return wordlist


async def create_tasks(url):
    headers = {'User-Agent': args.User_Agent}
    tasks = []
    wordlist = read_wordlist_file(args.wordlist)
    async with aiohttp.ClientSession(headers=headers) as session:
        if args.proxy_file:
            print('gathering proxies')
            proxy_list = read_proxy_file(args.proxy_file)
            if args.proxy_password:
                proxy_auth = aiohttp.BasicAuth(args.proxy_username, password=args.proxy_password)
            else:
                proxy_auth = None
            for word in wordlist:
                tasks.append((fetch(session, url + '/' + word, choice(proxy_list), proxy_auth)))
        else:
            for word in wordlist:
                tasks.append((fetch(session, url + '/' + word, None, None)))
        tasks = await asyncio.gather(*tasks, return_exceptions=True)
        return tasks

if __name__ == '__main__':
    args = parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_tasks(args.url))
