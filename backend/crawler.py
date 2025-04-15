import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time, json, os
from collections import deque
import asyncio
from http_tester import send_http_request

class Crawler:
    def __init__(self, json_filename='crawl_results.json'): #this feels incorrect but idk how else to handle json
        self.start_url = ''
        self.depth = ''
        self.max_pages = ''
        self.user_agent_string = ''
        self.delay = ''
        self.proxy = ''
        self.requests_per_sec = 0.0
        self.crawl_time = 0.0
        self.visited_urls = set()
        self.tree_structure = {}
        self.crawled_urls = []
        self.json_filename = json_filename  # Initialize the JSON filename
        self.total_pages = 0  # Track total pages to crawl
        self.stop_flag = False
        self.pause_flag = False
        # here use the user agent string for requests

    def fetch_page(self, url):
        try:
            headers = {}
            if self.user_agent_string:
                headers["User-Agent"] = self.user_agent_string
            
            #using http requester from team 6 here
            result = send_http_request(url, method="GET", headers=headers)
            if result.get("status_code") == 200:
                return result
            else:
                return None
        except Exception as e:
            print(f"[fetch_page ERROR] {e}")
            return None

    def retreieve_links_to_crawl(self, parsed_html, base_url):
        """Extracts and returns valid links from an HTML page."""
        links = set()
        for a_tag in parsed_html.find_all("a", href=True):
            full_url = urljoin(base_url, a_tag["href"])
            if self.is_valid_url(full_url):
                links.add(full_url)
        return links

    def is_valid_url(self, url): #I think I wrote this wrong but this should effectively avoid a looping issue where the url visits itself or visits one from before
        parsed = urlparse(url)
        return parsed.netloc == urlparse(self.start_url).netloc and url not in self.visited_urls
    
    #retrieves information asked for EXCEPT Errors (will ask, not sure what this entry would look like), and adds to JSON type format, (not quite json though watch out)

    def retreive_url_info(self, parsed_html, url, links, error = False):
        if not url:  # Check if URL is None or empty
            print("Invalid URL: ", url)  # Log invalid URL for debugging
            return  # Early exit if URL is invalid

        text = parsed_html.get_text() if parsed_html else ""
        char_count = len(text)
        words = text.split()
        word_count = len(words)
        link_count = len(links)
        title = parsed_html.title.string if parsed_html and parsed_html.title else "No Title"

        crawled_urls_entry = {
            'id': len(self.crawled_urls),
            'url': url,
            'title': title,
            'word_count': word_count,
            'char_count': char_count,
            'link_count': link_count,
            'error': error  # Adding error field (True if error occurred, False otherwise)
        }
        # url_info = CrawledURLInfo(url, title, word_count, char_count, link_count, words)
        # return url_info
        self.crawled_urls.append(crawled_urls_entry)

    # this function adds the results to the json file, WILL NEED TO CHANGE TO SAVE ON DB
    def save_json(self):
        try:

            file_path = os.path.join("outputs_crawler", self.json_filename)  # Save in outputs_crawler
            
            with open(file_path, 'w') as json_file:
                crawled_data = []
                for index, entry in enumerate(self.crawled_urls, start=1): #adding enumeration so we have workign ID 
                    if 'url' in entry:
                        crawled_data.append({
                            'id': index,  # Assign an ID starting from 1
                            'url': entry['url'],
                            'title': entry['title'],
                            'word_count': entry['word_count'],
                            'char_count': entry['char_count'],
                            'link_count': entry['link_count'],
                            'error': entry['error']
                        })
                    else:
                        print(f"Warning: 'url' key missing in entry: {entry}") #trying to find where that empty URL is coming from
                json.dump(crawled_data, json_file, indent = 4)
            print(f"Results saved to {file_path}") #quick print to know where it saved 
        except Exception as e:
            print(f"Error saving JSON: {e}")


    async def start_crawl(self, crawler_params): # starting crawling sequence

        #sets up crawler state and params
        self.configure_crawler(crawler_params)
        self.stop_flag = False
        self.total_pages = self.max_pages if self.max_pages else float('inf')  # Set total pages
        start = time.time()
        queue = deque([self.start_url])
        self.tree_structure[self.start_url] = []

        processed_requests = 0
        filtered_requests = 0

        while queue:
            if self.stop_flag:
                break
            url = queue.popleft()

            #allows pause and stop
            await asyncio.sleep(0.5) 
            while self.pause_flag:
                await asyncio.sleep(0.5) 

            #counts the depth of the current path and skips url if too deep
            if self.depth != '' and url != self.start_url:
                curr_url_path = urlparse(url).path
                url_depth = curr_url_path.count('/')
                if url_depth > self.depth:
                    continue

            if url in self.visited_urls:
                continue

            self.visited_urls.add(url)
            fetched_page = self.fetch_page(url)
            
            #status code based on team 6 http requester, if valid begin crawl on that url, else error out
            if fetched_page:
                response = fetched_page
                if response["status_code"] == 200:
                    html = response["body"]  # Use the HTML content from the successful response
                    parsed_html = BeautifulSoup(html, "html.parser")
                    # sets up crawled urls info
                    links = self.retreieve_links_to_crawl(parsed_html, url)
                    self.retreive_url_info(parsed_html, url, links, error=False)  # No error occurred 
                    self.tree_structure[url] = list(links)  # Store links in the tree structure
                    queue.extend(links)  # Add found links to the queue
                    filtered_requests += 1  # Increment filtered requests for successful responses
                else:
                    self.retreive_url_info(None, url, [], error=True) #True if error has indeed occurred
            else:
                self.retreive_url_info(None, url, [], error=True) #True if error has indeed occurred

            processed_requests += 1  # Increment processed requests

            yield {
                **self.crawled_urls[-1],
                "progress": len(self.crawled_urls) / self.total_pages if self.total_pages != float('inf') else None,
                "processed_requests": processed_requests,
                "filtered_requests": filtered_requests,
                "requests_per_second": round(processed_requests / (time.time() - start), 2)
            }

            #allows pause and stop
            await asyncio.sleep(0.5)
            while self.pause_flag:
                await asyncio.sleep(0.5) 

            #if num pages crawled quota reached, strop crawling
            if self.max_pages != '' and len(self.tree_structure) == self.max_pages:
                break

        end = time.time()
        self.crawl_time = end - start
        self.requests_per_sec = round(((len(self.crawled_urls)) / self.crawl_time), 2)
        self.save_json()

    # straight forward
    def stop_crawl(self):
        self.stop_flag = True
    def pause_crawl(self):
        self.pause_flag = True
    def resume_crawl(self):
        self.pause_flag = False

    # config crawler
    def configure_crawler(self, crawler_params):
        self.start_url = crawler_params['url']
        
        config_depth = crawler_params['depth']
        self.depth = config_depth if config_depth == '' else int(config_depth)
        
        config_max_pages = crawler_params['max_pages']
        self.max_pages = config_max_pages if config_max_pages == '' else int(config_max_pages)

        self.user_agent_string = crawler_params['user_agent']
        
        config_delay = crawler_params['delay']
        self.delay = config_delay if config_delay == '' else int(config_delay)

        self.proxy = crawler_params['proxy']