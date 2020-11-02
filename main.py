import requests
from collections import deque
from bs4 import BeautifulSoup
import requests.exceptions
from urllib.parse import urlsplit
from urllib.parse import urlparse
import os
import errno

output_directory = "output/"

def create_output_directory():
    if not os.path.exists(os.path.dirname(output_directory)):
        try:
            os.makedirs(os.path.dirname(output_directory))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def write_on_file(response, name):
    soup = BeautifulSoup(response.text, "lxml")
    
    with open(output_directory + "/%s.txt" % name, 'w', encoding="utf-8") as out:
        out.write(response.url + '\n')
        for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5" , "p"]):
            # print(heading.name + ' ' + heading.text.strip())    
            out.write(heading.text.strip() + '\n')
        out.close()
    return name + 1


def find_all_links(response):
    soup = BeautifulSoup(response.text, "lxml")
    return soup.find_all('a', href=True)

def check_url_type(requested_url, current_url, local_urls, foreign_urls):

    parts = urlsplit(requested_url)
    base = "{0.netloc}".format(parts)
    strip_base = base.replace("www.", "")
    base_url = "{0.scheme}://{0.netloc}".format(parts)
    path = requested_url[:requested_url.rfind('/')+1] if '/' in parts.path else requested_url


    anchor = current_url.attrs["href"] if 'href' in current_url.attrs else '' 
    if anchor.startswith('/'):        
        local_link = base_url + anchor        
        local_urls.add(local_link)    
    elif strip_base in anchor:       
        local_urls.add(anchor)    
    elif not anchor.startswith('http'):        
        local_link = path + anchor        
        local_urls.add(local_link)    
    else:        
        foreign_urls.add(anchor)


def add_new_urls(local_urls, new_urls, processed_urls):
    for i in local_urls:
        if not i in processed_urls:    
            new_urls.append(i)

def main():
	
    start_urls = ['https://www.arzdigital.com',
                    'https://isignal.ir', 
                    'https://donya-e-eqtesad.com',
                    'https://tejaratnews.com',
                    'https://www.khanesarmaye.com',
                    'https://itbfx.com/fa',
                    'https://www.irifc.asia',
                    'https://tejaratafarin.com',
                    'https://www.bourseiness.com',
                    'https://pforex.vip'                    
    ]
    new_urls = deque(start_urls)
    processed_urls = set()
    broken_urls = set()
    local_urls = set()
    foreign_urls = set()
    url_count = 1

    create_output_directory()

    while len(new_urls):
        url = new_urls.popleft()
        processed_urls.add(url)
        print(str("Processing %s" % url).encode('utf-8') , flush=True)
        
        try:    
            response = requests.get(url)
        except(requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema):    
            broken_urls.add(url)   
            continue
        
        url_count = write_on_file(response, url_count)
        
        for link in find_all_links(response):
            check_url_type(url, link, local_urls, foreign_urls)
        
        add_new_urls(local_urls, new_urls, processed_urls)
        


if __name__ == "__main__":
    main()