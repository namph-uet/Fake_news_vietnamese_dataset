import requests
from bs4 import BeautifulSoup
import pickle
import os
from urllib.parse import urlparse, unquote
from urllib.parse import parse_qs
import pandas as pd
import json
import csv
import re
import time

class FacebookCrawler:
    # We need the email and password to access Facebook, and optionally the text in the Url that identifies the "view full post".
    def __init__(self, email, password, post_url_text='Full Story'):
        self.email = email
        self.password = password
        self.headers = {  # This is the important part: Nokia C3 User Agent
            'User-Agent': 'NokiaC3-00/5.0 (07.20) Profile/MIDP-2.1 Configuration/CLDC-1.1 Mozilla/5.0 AppleWebKit/420+ (KHTML, like Gecko) Safari/420+'
        }
        self.session = requests.session()  # Create the session for the next requests
        self.cookies_path = 'session_facebook.cki'  # Give a name to store the session in a cookie file.

        # At certain point, we need find the text in the Url to point the url post, in my case, my Facebook is in
        # English, this is why it says 'Full Story', so, you need to change this for your language.
        # Some translations:
        # - English: 'Full Story'
        # - Spanish: 'Historia completa'
        self.post_url_text = post_url_text

        # Evaluate if NOT exists a cookie file, if NOT exists the we make the Login request to Facebook,
        # else we just load the current cookie to maintain the older session.
        if self.new_session():
            self.login()

        self.posts = []  # Store the scraped posts
    
    # We need to check if we already have a session saved or need to log to Facebook
    def new_session(self):
        if not os.path.exists(self.cookies_path):
            return True

        f = open(self.cookies_path, 'rb')
        cookies = pickle.load(f)
        self.session.cookies = cookies
        return False

    # Utility function to make the requests and convert to soup object if necessary
    def make_request(self, url, method='GET', data=None, is_soup=True):
        if len(url) == 0:
            raise Exception(f'Empty Url')

        if method == 'GET':
            resp = self.session.get(url, headers=self.headers)
        elif method == 'POST':
            resp = self.session.post(url, headers=self.headers, data=data)
        else:
            raise Exception(f'Method [{method}] Not Supported')

        if resp.status_code != 200:
            raise Exception(f'Error [{resp.status_code}] > {url}')

        if is_soup:
            return BeautifulSoup(resp.text, 'lxml')
        return resp

    # The first time we login
    def login(self):
        # Get the content of HTML of mobile Login Facebook page
        url_home = "https://mbasic.facebook.com/"
        soup = self.make_request(url_home)
        if soup is None:
            raise Exception("Couldn't load the Login Page")

        # Here we need to extract this tokens from the Login Page
        lsd = soup.find("input", {"name": "lsd"}).get("value")
        jazoest = soup.find("input", {"name": "jazoest"}).get("value")
        m_ts = soup.find("input", {"name": "m_ts"}).get("value")
        li = soup.find("input", {"name": "li"}).get("value")
        try_number = soup.find("input", {"name": "try_number"}).get("value")
        unrecognized_tries = soup.find("input", {"name": "unrecognized_tries"}).get("value")

        # This is the url to send the login params to Facebook
        url_login = "https://mbasic.facebook.com/login/device-based/regular/login/?refsrc=https%3A%2F%2Fm.facebook.com%2F&lwv=100&refid=8"
        payload = {
            "lsd": lsd,
            "jazoest": jazoest,
            "m_ts": m_ts,
            "li": li,
            "try_number": try_number,
            "unrecognized_tries": unrecognized_tries,
            "email": self.email,
            "pass": self.password,
            "login": "Iniciar sesión",
            "prefill_contact_point": "",
            "prefill_source": "",
            "prefill_type": "",
            "first_prefill_source": "",
            "first_prefill_type": "",
            "had_cp_prefilled": "false",
            "had_password_prefilled": "false",
            "is_smart_lock": "false",
            "_fb_noscript": "true"
        }
        soup = self.make_request(url_login, method='POST', data=payload, is_soup=True)
        if soup is None:
            raise Exception(f"The login request couldn't be made: {url_login}")

        redirect = soup.select_one('a')
        if not redirect:
            raise Exception("Please log in desktop/mobile Facebook and change your password")

        url_redirect = redirect.get('href', '')
        resp = self.make_request(url_redirect)
        if resp is None:
            raise Exception(f"The login request couldn't be made: {url_redirect}")

        # Finally we get the cookies from the session and save it in a file for future usage
        cookies = self.session.cookies
        f = open(self.cookies_path, 'wb')
        pickle.dump(cookies, f)

        return {'code': 200}
        
    login_basic_url = 'https://mbasic.facebook.com/login'
    login_mobile_url = 'https://m.facebook.com/login'
    base_url = 'https://mbasic.facebook.com'
    payload = {
            'email': 'hoangdeiq@gmail.com',
            'pass': 'namphuet.vnu'
        }

    def parse_html(self, request_url):
        with requests.Session() as session:
            post = session.post(self.login_basic_url, data=self.payload)
            parsed_html = session.get(request_url)
            print(post.content)
        return parsed_html
    
    def crawl_post_content(self):
        with open('politifact_content_no_ignore.csv', mode='a', encoding="utf-8", newline='') as post_content:
            # with open('fake_post.csv', mode='r') as csv_file:
            #     csv_reader = csv.DictReader(csv_file)

            #     fieldnames = ['id', 'label', 'content']
                # writer = csv.DictWriter(post_content, fieldnames=fieldnames)
                # writer.writeheader()

                # for row in csv_reader:
                #     id = row['id']
                #     print(id)
                #     REQUEST_URL = f'https://mbasic.facebook.com/story.php?story_fbid={id}&id=415518858611168'
                
                #     # soup = self.make_request(REQUEST_URL)
                #     soup = self.make_request(REQUEST_URL)
                #     print(soup)
                #     content = soup.find_all('p')
                #     post_content = []
                #     for lines in content:
                #         post_content.append(lines.text)
                
                #     post_content = ' '.join(post_content)  

                #     # remove emoji
                #     remove_emojis = re.compile("["
                #                u"\U0001F600-\U0001F64F"  # emoticons
                #                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                #                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                #                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                #                u"\U00002500-\U00002BEF"  # chinese char
                #                u"\U00002702-\U000027B0"
                #                u"\U00002702-\U000027B0"
                #                u"\U000024C2-\U0001F251"
                #                u"\U0001f926-\U0001f937"
                #                u"\U00010000-\U0010ffff"
                #                u"\u2640-\u2642"
                #                u"\u2600-\u2B55"
                #                u"\u200d"
                #                u"\u23cf"
                #                u"\u23e9"
                #                u"\u231a"
                #                u"\ufe0f"  # dingbats
                #                u"\u3030"
                #             "]+", flags=re.UNICODE)
                #     post_content = remove_emojis.sub(r'', post_content)
                #     post_content = post_content.replace('*', ' ')
                #     post_content = re.sub(r"<([^>]*)>", "", post_content)
                #     post_content = ' '.join(post_content.split())

                #     writer.writerow({'id': id, 'label': 0, 'content': post_content})
                #     print(post_content)
                #     time.sleep(5)
            
            with open('temp.csv', mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                fieldnames = ['id', 'label', 'content']
                writer = csv.DictWriter(post_content,fieldnames)

                for row in csv_reader:
                    id = row['id']
                    print(id)
                    REQUEST_URL = f'https://mbasic.facebook.com/story.php?story_fbid={id}&id=415518858611168'
                
                    # soup = self.make_request(REQUEST_URL)
                    soup = soup = self.make_request(REQUEST_URL)
                    content = soup.find_all('p')
                    post_content = []
                    for lines in content:
                        post_content.append(lines.text)
                
                    post_content = ' '.join(post_content) 

                    # remove emoji
                    remove_emojis = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                            "]+", flags=re.UNICODE)
                    post_content = remove_emojis.sub(r'', post_content)
                    post_content = post_content.replace('*', ' ')
                    post_content = re.sub(r"<([^>]*)>", "", post_content)
                    post_content = ' '.join(post_content.split())

                    writer.writerow({'id': id, 'label': 1, 'content': post_content})
                    print(post_content)
                    time.sleep(5)

    def crawl_post_comment(self):
        with open('politifact_comment_no_ignore.csv', mode='a', encoding="utf-8", newline='') as post_content:
            fieldnames = ['id', 'comment']
            writer = csv.DictWriter(post_content, fieldnames=fieldnames)

            with open('temp.csv', mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    id = row['id']
                    print(id)
                    REQUEST_URL = f'https://mbasic.facebook.com/story.php?story_fbid={id}&id=415518858611168'
                    soup = self.make_request(REQUEST_URL)
                    print(soup)
                    all_comments = ''
                    div_container = soup.find('div', {'id': 'm_story_permalink_view'})
                    while div_container == None:
                        time.sleep(60)
                        soup = self.make_request(REQUEST_URL)
                        print(soup)
                        div_container = soup.find('div', {'id': 'm_story_permalink_view'})

                    temp = div_container.findAll('div', {'class': 'ea'})
                    first_comment = True;
                    for e in temp:
                        if first_comment:
                            all_comments += re.sub(r'[^\w]', ' ', e.text)
                            first_comment = False
                        else:
                            if e.text != '':
                                all_comments += r'::' + re.sub(r'[^\w]', ' ', e.text)

                    page = 10
                    while True:
                        time.sleep(20)
                        soup2 = self.make_request(REQUEST_URL+'&p='+str(page))
                        print(REQUEST_URL+'&p='+str(page))
                        print(soup2)
                        div_container = soup2.find('div', {'id': 'm_story_permalink_view'})
                        if div_container == None: break
                        
                        temp2 = div_container.findAll('div', {'class': 'eb'})
                        if temp2 == None or temp2 == []: break
                        page += 10
                        for e in temp2:
                            if e.text != '':
                                all_comments += r'::' + re.sub(r'[^\w]', ' ', e.text)

                    # remove emoji
                    remove_emojis = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                            "]+", flags=re.UNICODE)
                    all_comments = remove_emojis.sub(r'', all_comments)
                    all_comments = all_comments.replace('*', ' ')
                    all_comments = re.sub(r"<([^>]*)>", "", all_comments)
                    all_comments = ' '.join(all_comments.split())

                    writer.writerow({'id': id, 'comment': all_comments})
                    print(all_comments)
                    time.sleep(20)

            # with open('real_post.csv', mode='r') as csv_file:
            #     csv_reader = csv.DictReader(csv_file)

            #     for row in csv_reader:
            #         id = row['id']
            #         print(id)
            #         REQUEST_URL = f'https://mbasic.facebook.com/story.php?story_fbid={id}&id=415518858611168'
            #         soup = self.make_request(REQUEST_URL)

            #         all_comments = ''
            #         div_container = soup.find('div', {'id': 'm_story_permalink_view'})
            #         temp = div_container.findAll('div', {'class': 'cv'})
            #         first_comment = True;
            #         for e in temp:
            #             if first_comment:
            #                 all_comments += re.sub(r'[^\w]', ' ', e.text)
            #                 first_comment = False
            #             else:
            #                 if e.text != '':
            #                     all_comments += r'::' + re.sub(r'[^\w]', ' ', e.text)

            #         page = 10
            #         while True:
            #             soup2 = self.make_request(REQUEST_URL+'&p='+str(page))
            #             div_container = soup2.find('div', {'id': 'm_story_permalink_view'})
            #             if div_container == None: break
                        
            #             temp2 = div_container.findAll('div', {'class': 'cx'})
            #             if temp2 == None: break
            #             page += 10
            #             for e in temp2:
            #                 if e.text != '':
            #                     all_comments += r'::' + re.sub(r'[^\w]', ' ', e.text)
            #             time.sleep(3)
                    
            #         # remove emoji
            #         remove_emojis = re.compile("["
            #                    u"\U0001F600-\U0001F64F"  # emoticons
            #                    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            #                    u"\U0001F680-\U0001F6FF"  # transport & map symbols
            #                    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            #                    u"\U00002500-\U00002BEF"  # chinese char
            #                    u"\U00002702-\U000027B0"
            #                    u"\U00002702-\U000027B0"
            #                    u"\U000024C2-\U0001F251"
            #                    u"\U0001f926-\U0001f937"
            #                    u"\U00010000-\U0010ffff"
            #                    u"\u2640-\u2642"
            #                    u"\u2600-\u2B55"
            #                    u"\u200d"
            #                    u"\u23cf"
            #                    u"\u23e9"
            #                    u"\u231a"
            #                    u"\ufe0f"  # dingbats
            #                    u"\u3030"
            #                 "]+", flags=re.UNICODE)
            #         all_comments = remove_emojis.sub(r'', all_comments)
            #         all_comments = all_comments.replace('*', ' ')
            #         all_comments = re.sub(r"<([^>]*)>", "", all_comments)
            #         all_comments = ' '.join(all_comments.split())

            #         writer.writerow({'id': id, 'comment': all_comments})
            #         print(all_comments) 
            #         time.sleep(3)

def main():
    email = '0373262971'
    password = 'Nam@1234567'

    crawler = FacebookCrawler(email, password, post_url_text='Full Story')
    # crawler.crawl_post_content()
    crawler.crawl_post_comment()

if __name__ == '__main__':
    main()

       