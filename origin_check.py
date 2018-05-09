#!/usr/bin/env python3
import concurrent.futures
import logging
import requests
from sys import argv, exit
from urllib.parse import urlparse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.30 Safari/537.36'
}
MIN_RESPONSE_LENGTH = 100
NUM_WORKERS = 10

urls = []

if len(argv) < 2:
    exit("Please specify a URLs file.")

with open(argv[1]) as f:
    urls = [line.rstrip() for line in f]


def check(url):
    # Issue a GET request
    r = requests.get(url, timeout=5, allow_redirects=False, headers=HEADERS)
    response_size = len(r.text)
    if r.status_code != 200 or response_size < MIN_RESPONSE_LENGTH:
        logging.debug("Ignoring %s: response %d, response size %d.",
                      url, r.status_code, response_size)
        return None

    # Issue a second request to check for stability (200 + same response size)
    r = requests.get(url, timeout=5, allow_redirects=False, headers=HEADERS)
    if r.status_code != 200 or response_size != len(r.text):
        logging.debug("URL %s is unstable.", url)
        return None
    logging.info("URL %s is stable.", url)

    # If the URL is stable, try adding a same-origin Origin header
    parsed_url = urlparse(r.url)
    origin = parsed_url.scheme + '://' + parsed_url.netloc
    logging.debug('Sending same-origin Origin %s for %s...', origin, url)

    result = {
        'url': url,
        'SAMEORIGIN_OK': False,
        'CROSSORIGIN_OK': False,
        'SAMEORIGIN_KO_STATUS': False,
        'SAMEORIGIN_KO_RESPONSE': False,
        'CROSSORIGIN_KO_STATUS': False,
        'CROSSORIGIN_KO_RESPONSE': False
    }

    r = requests.get(url, timeout=5, allow_redirects=False,
                     headers={**HEADERS, **{'Origin': origin}})
    if r.status_code != 200:
        logging.info(
            "[SAME ORIGIN] URL %s changed status code to %d.", url, r.status_code)
        result['SAMEORIGIN_KO_STATUS'] = r.status_code
        return result
    if response_size != len(r.text):
        logging.info(
            "[SAME ORIGIN] URL %s changed response size to %d.", url, len(r.text))
        result['SAMEORIGIN_KO_RESPONSE'] = True
        return result
    result['SAMEORIGIN_OK'] = True

    # If same-origin Origin header is OK, try a cross-origin one.
    logging.debug('Sending cross-origin Origin for URL %s.', url)
    r = requests.get(url, timeout=5, allow_redirects=False, headers={
                     **HEADERS, **{'Origin': 'https://example.org'}})
    if r.status_code != 200:
        logging.info(
            "[CROSS ORIGIN] URL %s changed status code to %d.", url, r.status_code)
        result['CROSSORIGIN_KO_STATUS'] = r.status_code
        return result
    if response_size != len(r.text):
        logging.info(
            "[CROSS ORIGIN] URL %s changed response size to %d.", url, len(r.text))
        result['CROSSORIGIN_KO_RESPONSE'] = True
        return result
    result['CROSSORIGIN_OK'] = True

    return result


with open('results.csv', 'w') as w:
    print('url,SAMEORIGIN_OK,CROSSORIGIN_OK,SAMEORIGIN_KO_STATUS,SAMEORIGIN_KO_RESPONSE,CROSSORIGIN_KO_STATUS,CROSSORIGIN_KO_RESPONSE', file=w)
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        future_to_result = {executor.submit(check, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_result):
            try:
                result = future.result()
            except:
                continue
            else:
                if result:
                    print('{},{},{},{},{},{},{}'.format(result['url'],
                                                        int(result['SAMEORIGIN_OK']),
                                                        int(result['CROSSORIGIN_OK']),
                                                        int(result['SAMEORIGIN_KO_STATUS']),
                                                        int(result['SAMEORIGIN_KO_RESPONSE']),
                                                        int(result['CROSSORIGIN_KO_STATUS']),
                                                        int(result['CROSSORIGIN_KO_RESPONSE'])
                                                        ), file=w)
