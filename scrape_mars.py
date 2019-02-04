from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from bs4 import BeautifulSoup
import time
import pandas as pd


def init_browser():
    executable_path = {"executable_path": "c:/util/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)
    
def scrape():
    browser = init_browser()

    #NASA Mars News
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    time.sleep(1)    
    soup = BeautifulSoup(browser.html, 'html.parser')

    article = soup.find('li', class_='slide')
    news_title = article.find('h3').text
    news_p = article.find('div', class_='article_teaser_body').text  
    mars_news = {"news_title": news_title, "news_p": news_p}

    #JPL Mars Space Images
    url = 'https://www.jpl.nasa.gov'
    search_string = '/spaceimages/?search=&category=Mars'
    browser.visit(url + search_string)
    time.sleep(1)
    soup = BeautifulSoup(browser.html, 'html.parser')

    featured_image_url = url + soup.find('section', class_='main_feature').\
        find('div', class_='carousel_items').\
        find('footer').\
        find('a')["data-fancybox-href"].\
        replace('mediumsize', 'largesize').\
        replace('_ip.jpg', '_hires.jpg')

    #Mars Weather
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)
    time.sleep(1)
    soup = BeautifulSoup(browser.html, 'html.parser')

    items = soup.find('div', class_='stream').ol.find_all('li', class_='js-stream-item stream-item stream-item')

    for item in items:
        if item.find('div', class_='js-tweet-text-container').find('p', class_='TweetTextSize').text[:3] == 'Sol':
            mars_weather_tag = item.find('div', class_='js-tweet-text-container').find('p', class_='TweetTextSize')
            mars_weather = mars_weather_tag.text.replace(mars_weather_tag.a.text, '')
            break

    #Mars Facts
    url = 'http://space-facts.com/mars/'
    tables = pd.read_html(url)
    df = tables[0]
    df.columns = ['description', 'value']
    mars_facts = df.set_index('description').T.to_dict('records')[0]

    #Mars Hemispheres
    url = 'https://astrogeology.usgs.gov'
    search_string = '/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url + search_string)
    time.sleep(1)
    soup = BeautifulSoup(browser.html, 'html.parser')    

    #get the tags for all the Hemispheres
    items = soup.find('div', class_='full-content').\
      find('div', class_='collapsible results').\
      find_all('div', class_='item')

    #first loop to pull out the title and the link to the individual page for the hires image
    hemisphere_image_urls = []
    for item in items:
        hemisphere_image_urls.append(
            {"title": item.find('div', class_='description').h3.text
            , "page_url": f"{url}{item.a['href']}"
            , "img_url_orignal": ""
            , "img_url_full": ""
            }
        )  

    #second loop to iterate over the list and replace the img_url with the actial hires image url
    for i, url in enumerate(hemisphere_image_urls):
        browser.visit(url['page_url'])
        time.sleep(1)
        soup = BeautifulSoup(browser.html, 'html.parser')  
        hemisphere_image_urls[i]['img_url_orignal'] = soup.find('div', class_='downloads').\
            ul.\
            find_all('li')[1].\
            a['href']
        hemisphere_image_urls[i]['img_url_full'] = soup.find('div', class_='downloads').\
            ul.\
            find_all('li')[0].\
            a['href']

    #collate all scaped data into
    mars_data = {
        "mars_data" : [
            {"mars_news":  mars_news}
            , {"featured_image_url": featured_image_url}  
            , {"mars_weather": mars_weather}
            , {"mars_facts": mars_facts}
            , {"hemisphere_image_urls": hemisphere_image_urls}
        ]
    }
    browser.quit()
    
    return mars_data