from bs4 import BeautifulSoup
from getpass import getpass
import requests
import json

#Todo: Run through Forum pages
#Todo: Run through all Forum links (Football, Official, Official Club, etc.)
#Todo: Input page numbers to start from

# URLs
base_url = 'http://forum.football365.com/'
login_url = 'http://forum.football365.com/ucp.php?mode=login'

headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

# json_dump = {}

# with requests.Session() as session:
#     post = session.post(url=login_url, headers=headers, data=payload)
#     # print(post.text)
#     r = session.get(url=football_url)
#     # print(r.text)
#     # with open('frontpage.txt', 'w') as f:
#     #     f.write(r.text)

#     soup = BeautifulSoup(r.content, 'html.parser')

#     soup.find('div', class_='forumbg announcement').decompose()

#     topics = soup.find_all('a', class_='topictitle')
#     print(topics)

#     # for i in range(0, len(topics)):
#     for i in range(0, 1):
#         topic_title = soup.find_all('a', class_='topictitle')[i].get_text()
#         topic_url = soup.find_all('a', class_='topictitle')[i]['href']

#         url = base_url + topic_url[2:]
        
#         postbody_list = []
#         while True:
            
#             s = session.get(url=url)
            
#             topic_soup = BeautifulSoup(s.content, 'html.parser')
            
#             postbody = topic_soup.find_all('div', class_='postbody')

#             # Get post info
#             for item in postbody:
#                 if item.find('a', class_='username') == None:
#                     username = item.find('a', class_='username-coloured').get_text()
#                 else:
#                     username = item.find('a', class_='username').get_text()
#                 date = item.find('p', class_='author').get_text()
#                 content = str(item.find('div', class_='content'))

#                 date = date[date.index('»') + 1:].strip()
#                 body_dict = {
#                     'username': str(username),
#                     'date': str(date),
#                     'content': str(content[21:len(content)-6])
#                 }
#                 postbody_list.append(body_dict)

#             # Find if next page exists
#             pagination = topic_soup.find('div', class_='pagination')
#             # print(pagination)
#             next_cls = pagination.find('li', class_='next')

#             if next_cls != None:
#                 next_link = next_cls.find('a')['href']
#                 url = base_url + next_link[2:]
#             else:
#                 break
        
#         json_dump[topic_title] = postbody_list

#         # with open('multipgex.txt', 'w') as f:
#         #     f.write(s.text)

# with open('f365_dump.json', 'w') as f:
#     json.dump(json_dump, f)

def next_url(soup):
    # Find if next page exists
    pagination = soup.find('div', class_='pagination')

    next_cls = pagination.find('li', class_='next')

    # Return url of next page if exists
    if next_cls != None:
        next_link = next_cls.find('a')['href']
        url = base_url + next_link[2:]
        return url
    else:
        return None

def authenticate(session, payload):
    post = session.post(url=login_url, headers=headers, data=payload)
    if post.status_code != 200:
        return None, f'{post.status_code} - {post.text}'
    else:
        return post, None

def scrape_board(session, url):
    while True:
        # Get board content
        r = session.get(url=url)

        soup = BeautifulSoup(r.content, 'html.parser')

        if soup.find('div', class_='forumbg announcement') == None:
            print(soup)
        # Remove announcement topics
        soup.find('div', class_='forumbg announcement').decompose()

        # Get all topics
        topics = soup.find_all('a', class_='topictitle')

        for i in range(0, len(topics)):
            # Get topic title and URL
            topic_title = soup.find_all('a', class_='topictitle')[i].get_text()
            topic_url = soup.find_all('a', class_='topictitle')[i]['href']

            # Remove ./ and prepend base url
            full_topic_url = base_url + topic_url[2:]

            # Scrape topic
            scrape_topic(session, full_topic_url, topic_title)
        
        # Scrape next page url
        url = next_url(soup)
        if not url:
            break

def scrape_topic(session, url, topic_title):
    json_dump = {}
    postbody_list = []

    while True:
        # Get topic content
        s = session.get(url=url)
        
        topic_soup = BeautifulSoup(s.content, 'html.parser')
        
        postbody = topic_soup.find_all('div', class_='postbody')

        # Get post info
        for item in postbody:
            # Username
            if item.find('a', class_='username') != None:
                username = item.find('a', class_='username').get_text()
            elif item.find('a', class_='username-coloured') != None:
                username = item.find('a', class_='username-coloured').get_text()
            elif item.find('span', class_="username") != None:
                username = item.find('span', class_="username").get_text()
            else:
                print('what the fuck')
                
            # Date
            date = item.find('p', class_='author').get_text()
            date = date[date.index('»') + 1:].strip()
            # Content
            content = str(item.find('div', class_='content'))

            # Strip wrapping div from content
            body_dict = {
                'username': str(username),
                'date': str(date),
                'content': str(content[21:len(content)-6])
            }
            postbody_list.append(body_dict)

        url = next_url(topic_soup)
        if not url:
            break

    # Get date of first post for json file. Remove invalid char for windows files (:)
    topic_date = postbody_list[0]['date'].replace(':', '')
    topic_title = topic_title.replace(':', '%')

    json_title = f'{topic_title} - {topic_date}.json'

    # json_dump[json_key] = postbody_list

    write_to_json(postbody_list, json_title)

def write_to_json(data, title):
    with open(f'json_files/{title}', 'w') as f:
        json.dump(data, f)

def main():
    username = input('Username: ')
    password = getpass('Password: ')
    board = input(
        '1 - Football Forum\n' \
        '2 - Official Club Threads\n' \
        '3 - Official Threads\n' \
        '4 - Classic Threads\n'
    )
    if board == '1': url = 'http://forum.football365.com/viewforum.php?f=4'
    elif board == '2': url = 'http://forum.football365.com/viewforum.php?f=5'
    elif board == '3': url = 'http://forum.football365.com/viewforum.php?f=8'
    elif board == '4': url = 'http://forum.football365.com/viewforum.php?f=7'
    else:
        print('Fuck off')
        return
    
    payload = {
        'username': username,
        'password': password,
        'login': 'Login',
        'redirect': './index.php?'
    }

    with requests.Session() as session:
        # Authenticate
        data, err = authenticate(session, payload)
        if err:
            print(err)
            return

        # Scrape chosen board
        scrape_board(session, url)
        
if __name__ == '__main__':
    main()