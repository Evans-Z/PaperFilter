import requests
import re
import csv
from bs4 import BeautifulSoup
from constant import PAGES


def get_bs_obj(page_url: str):
    try:
        html = requests.get(page_url)
    except:
        return None
    else:
        return BeautifulSoup(html.content, 'html.parser')


def get_volumes(url, year):
    bs_obj = get_bs_obj(url)
    link_list = bs_obj.find_all('a', text=re.compile(".*" + str(year) + ".*"))
    hrefs = []
    for i in link_list:
        hrefs.append(i.get('href'))
    return hrefs


def get_conf(main_page, year):
    path = main_page[:main_page.rfind("/")]
    conf = path[path.rfind("/"):]
    return [path + conf + str(year) + ".html"]


def get_info(url, result_file, class_find, info):
    bs_obj = get_bs_obj(url)
    with open(result_file, "a+") as csvfile:
        for i in bs_obj.find_all(class_=class_find):
            title = i.find(class_="title")
            title = title.get_text()  # 提取文本
            doi = i.find("a")  # 找到规律，直接拿第一个链接就是了,doi值隐藏在这个链接之后
            doi = doi.get("href")
            doi = str(doi)
            doi = doi.replace("http://", "")  # 除去链接头

            writer = csv.writer(csvfile)
            writer.writerow([title, doi] + info)
    csvfile.close()


def main():
    pages = list(PAGES.items())
    for page in pages:
        journal_name = page[0]
        main_page = page[1][0]
        ccf_rank = page[1][1]
        years = list(range(2015, 2021))

        repeat_url = set()  # 用于去掉重复的url爬取

        for year in years:
            print("{}-{}".format(journal_name, year))

            if "journals" in main_page:
                link_list = get_volumes(main_page, year)
                class_find = "entry article"
            elif "conf" in main_page:
                link_list = get_conf(main_page, year)
                class_find = "entry inproceedings"
            else:
                return []

            for a in link_list:
                if a in repeat_url:
                    continue
                repeat_url.add(a)
                info = [year, ccf_rank, journal_name]
                get_info(a, journal_name + ".csv", class_find,info)


if __name__ == '__main__':
    main()
