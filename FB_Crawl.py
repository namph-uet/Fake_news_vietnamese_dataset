import requests
from bs4 import BeautifulSoup
import re
import csv
import time

class FaceBookBot():
    login_basic_url = 'https://mbasic.facebook.com/login'
    login_mobile_url = 'https://m.facebook.com/login'
    base_url = 'https://mbasic.facebook.com'
    payload = {
            'email': 'hoangdeiq@gmail.com',
            'pass': 'namphuet.vnu'
        }
    post_ID = "526323195195086"

    def parse_html(self, request_url):
        with requests.Session() as session:
            post = session.post(self.login_basic_url, data=self.payload)
            parsed_html = session.get(request_url)
            print(post.content)
        return parsed_html

    def post_content(self):
        with open('politifact_content_no_ignore.csv', mode='w', encoding="utf-8", newline='') as post_content:
            with open('fake_post.csv', mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file)

                fieldnames = ['id', 'label', 'content']
                writer = csv.DictWriter(post_content, fieldnames=fieldnames)
                writer.writeheader()

                for row in csv_reader:
                    id = row['id']
                    print(id)
                    REQUEST_URL = f'https://mbasic.facebook.com/story.php?story_fbid={id}&id=415518858611168'
                
                    soup = BeautifulSoup(self.parse_html(REQUEST_URL).content, "html.parser")
                    content = soup.find_all('p')
                    post_content = []
                    for lines in content:
                        post_content.append(lines.text)
                
                    post_content = ' '.join(post_content)  
                    writer.writerow({'id': id, 'label': 0, 'content': post_content})
                    print(soup)
            
            with open('real_post.csv', mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file)

                fieldnames = ['id', 'label', 'content']
                writer = csv.DictWriter(post_content, fieldnames=fieldnames)
                writer.writeheader()

                for row in csv_reader:
                    id = row['id']
                    print(id)
                    REQUEST_URL = f'https://mbasic.facebook.com/story.php?story_fbid={id}&id=415518858611168'
                
                    soup = BeautifulSoup(self.parse_html(REQUEST_URL).content, "html.parser")
                    content = soup.find_all('p')
                    post_content = []
                    for lines in content:
                        post_content.append(lines.text)
                
                post_content = ' '.join(post_content)  
                writer.writerow({'id': id, 'label': 1, 'content': post_content})
                print(content)

    def date_posted(self):
        REQUEST_URL = f'https://mbasic.facebook.com/story.php?story_fbid={self.post_ID}&id=415518858611168'
        
        soup = BeautifulSoup(self.parse_html(REQUEST_URL).content, "html.parser")
        date_posted = soup.find('abbr')
        return date_posted.text

    def post_likes(self):
        limit = 200
        REQUEST_URL = f'https://mbasic.facebook.com/ufi/reaction/profile/browser/fetch/?limit={limit}&total_count=17&ft_ent_identifier={self.post_ID}'

        soup = BeautifulSoup(self.parse_html(REQUEST_URL).content, "html.parser")
        names = soup.find_all('h3')
        people_who_liked = []
        for name in names:
            people_who_liked.append(name.text)
        people_who_liked = [i for i in people_who_liked if i] 
        return people_who_liked

    def post_shares(self):        
        REQUEST_URL = f'https://m.facebook.com/browse/shares?id={self.post_ID}'
        
        with requests.Session() as session:
            post = session.post(self.login_mobile_url, data=self.payload)
            parsed_html = session.get(REQUEST_URL)
        
        soup = BeautifulSoup(parsed_html.content, "html.parser")
        names = soup.find_all('span')
        people_who_shared = []
        for name in names:
            people_who_shared.append(name.text)
        return people_who_shared

    def post_comment(self):
        REQUEST_URL = f'https://mbasic.facebook.com/story.php?story_fbid={self.post_ID}&id=415518858611168'
        soup = BeautifulSoup(self.parse_html(REQUEST_URL).content, "html.parser")

        #     all_comments += r'::' + re.sub(r'[^\w]', ' ', e.text)
        #     print(all_comments)

        #
        all_comments = ''
        div_container = soup.find('div', {'id': 'm_story_permalink_view'})
        temp = div_container.findAll('div', {'class': 'cx'})
        first_comment = True;
        for e in temp:
            if first_comment:
                all_comments += re.sub(r'[^\w]', ' ', e.text)
                first_comment = False
            else:
                all_comments += r'::' + re.sub(r'[^\w]', ' ', e.text)

        page = 10
        while True:
            soup2 = BeautifulSoup(self.parse_html(REQUEST_URL+'&p='+str(page)).content, "html.parser")
            div_container = soup2.find('div', {'id': 'm_story_permalink_view'})
            if div_container == None: break
            
            temp2 = div_container.findAll('div', {'class': 'cz'})
            if temp2 == None: break
            page += 10
            for e in temp2:
                all_comments += r'::' + re.sub(r'[^\w]', ' ', e.text)
        
        with open('politifact_comment_no_ignore.csv', mode='w', encoding="utf-8") as csv_file:
            fieldnames = ['id', 'comment']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerow({'id': self.post_ID, 'comment': all_comments})
                


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
                    print(REQUEST_URL)
                    soup = BeautifulSoup(requests.get(REQUEST_URL).text, "html.parser")
                    print(soup)
                    all_comments = ''
                    div_container = soup.find('div', {'id': 'm_story_permalink_view'})
                    temp = div_container.findAll('div', {'class': 'dc'})
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
                        time.sleep(10)
                        soup2 = BeautifulSoup(requests.get(REQUEST_URL+'&p='+str(page)).text, "html.parser")
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
                    time.sleep(15)

            
    #def crawl_post_have_video(self):

# from facebook_scraper import get_posts

# with open('real_post.csv', mode='w', newline='') as csv_file:
#     fieldnames = ['id']
#     writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

#     writer.writeheader()
#     for post in get_posts('tintucvtv24', pages=100000, timeout=10000):
#         print(post['post_id'])
#         writer.writerow({'id': post['post_id']})


bot = FaceBookBot();
# bot.post_comment()
bot.crawl_post_comment()

# from facebook_scraper import get_posts
# for post in get_posts(timeout=10000, post_urls='story.php?story_fbid=526323195195086&id=415518858611168'):
#     print(post)