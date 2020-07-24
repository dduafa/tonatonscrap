import threading, time
import sys, subprocess
from bs4 import BeautifulSoup
import requests
import argparse 
import logging
# from apscheduler.schedulers.background import BackgroundScheduler
# schedule = BackgroundScheduler()

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


def notification(title, information, time):
    logging.warning("Notification sent")

    os_platform = sys.platform.lower()
    if os_platform == 'linux':
        subprocess.call(['notify-send', title, information])
    elif os_platform == 'win32':
        from win10toast import ToastNotifier
        toast = ToastNotifier()
        toast.show_toast(title, information, duration=time)

def get_soup(url):
    logging.warning("Requesting page and preparing html soup")
    raw_data = requests.get(url)
    data_content = raw_data.content
    soup = BeautifulSoup(data_content, "html.parser")
    return soup

def get_ads(item_name, item_category="other"):
    logging.warning("Searching for ads")
    base_url = "https://tonaton.com/en/ads/ghana"
    search_url = f"{base_url}/{item_category}?query="

    categories = ('electronics', 'property','home-garden', 'vehicles',
                    'clothing, health-beauty', 'hobby, sport-kids', 'essentials',
                    'business-industry', 'jobs-in-ghana', 'pets-animals', 'services',
                    'food-agriculture', 'other', 'education', 'overseas-jobs'
                )

    if category in categories:
        search_url = f"{base_url}/{category}?query="
    
    search_url = search_url + item_name
    page_soup = get_soup(search_url)

    card_list = page_soup.find_all("li", {"class": "normal--2QYVk gtm-normal-ad"})

    extracts = []
    for item in card_list:    
        data = {}
        data["Title"] = item.find("span", {"class": "title--3yncE"}).text
        data["Location"] = item.find("div", {"class": "description--2-ez3"}).text
        data["Price"] = item.find("div", {"class": "price--3SnqI color--t0tGX"}).text
        data["update_time"] = item.find("div", {"class": "updated-time--1DbCk"}).text
        
        extracts.append(data)
    
    return extracts

def process(search_item, category):
    threading.Timer(15, process, [search_item, category]).start()
    data = []

    try:
        data = get_ads(search_item, category)
    except(ConnectionError, Exception) as e:
        print(e)

    if len(data) <= 0:
        print("No ads found")
    else:    
        for info in data:
            ad_time = info["update_time"].split(" ")
            if len(ad_time) == 2:
                if ad_time[1] in ["minutes", "hours", "now"]:            
                    notification("Tonaton.com", info['Title'] + "\n" + info['Price'] + "\n" + info['update_time'], 0)
                    time.sleep(10)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Update on new ads from category")
  
    parser.add_argument(
        "search_item",
        metavar="search_item",
        type=str,
        help="The item to search"
    )

    parser.add_argument(
        "-c",
        "--category",
        action="store_true",
        dest="category",
        default=False,
        help="The category of item to search"
    )


    if len(sys.argv) > 1:
        args, unknown = parser.parse_known_args()
        search_item = args.search_item
        category = "other"

        if (args.category):
            category = args.category


        data = get_ads(search_item, category)
        process(search_item, category)
        # schedule.add_job(process, 'interval', seconds=5, args=[search_item, category])
        # schedule.start()
        
        print(data)
    else:
        print("Wrong Command!!!\nautomate.py [search_item] -c [category]")
        # schedule.shutdown()

