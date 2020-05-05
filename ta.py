from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import csv
import asyncio
import threading
colums=['name','address','phone','cusine', 'email', 'state' ]



def init(writer, outFile):

    urls = ['https://www.tripadvisor.in/Restaurants-g28926-oa20-California.html#LOCATION_LIST']

    page = 0
    for url in urls: 
        while True:
            urlSplit = url.split("-")
            # print(page)
            page_url = urlSplit[0]+'-'+urlSplit[1]+'-oa'+str(page)+'-'+urlSplit[3]
            print('reading ', page_url, ' -> page ', int(page/20)+1)
            try:
                uClient = uReq(page_url)
                page_html = uClient.read()
                page_soup = soup(page_html, 'html.parser')
                if page == 0:
                    state_list = page_soup.findAll("div", {"class":"geo_name"})
                else:
                    state_list = page_soup.findAll("ul", {"class":"geoList"})[0].findAll("li")
                
                if not state_list:
                    print('ending page', page/20)
                    break
                # print(state_list)
                for state in state_list:
                    state_url = "https://www.tripadvisor.com"+state.a["href"]
                    state_name = state.a.text
                    print("\treading restaurants in state ",state_name)

                    restaurant_page = 0
                    while True:
                        try:
                            restUrlSplit = state_url.split("-")
                            rests_url = "https://www.tripadvisor.com/RestaurantSearch-"+restUrlSplit[1]+"-oa"+str(restaurant_page)+"-"+restUrlSplit[2]
                            print("\treading in page ", (restaurant_page/20) +1)
                            uClient = uReq(rests_url)
                            page_html = uClient.read()
                            rest_page_html = soup(page_html, 'html.parser')
                            rests = rest_page_html.findAll("div", {"class":"_1llCuDZj"})

                            for rest in rests:
                                try:
                                    rest_url = "https://www.tripadvisor.com"+rest.a["href"]
                                    write(rest_url, writer, state_name,outFile)
                                    # print("\t\t\t",name, address, phone, price, cusine, email)
                                except Exception as e:
                                    print('\t\t\tending', e)
                                    break
                        
                            restaurant_page += 20
                            # break
                            if restaurant_page >= 20000:
                                break
                        except :
                            print('ending rest page', str(restaurant_page/20) + 1)


                page = page+20
                # break
                
            except:
                print('ending page', page/20)
                break


def write_restaurant(rest_url, writer, state_name,outFile):
    # return asyncio.get_event_loop().run_in_executor(write(rest_url, writer, state_name,outFile))
    threading.Thread(target=write, args=(rest_url, writer, state_name,outFile)).start()

def write(rest_url, writer, state_name,outFile):
    print("\t\t\t",rest_url)
    uClient = uReq(rest_url)
    page_html = uClient.read()
    rest_html = soup(page_html, 'html.parser')

    name =  address  = cusine = phone = email=  ''

    try:
        name = rest_html.h1.text
    except:
        print('\t\t\terror reciveing name')
    
    try:
        details = rest_html.findAll("span", {"class": "restaurants-detail-top-info-TopInfo__infoCell--17Pql restaurants-detail-top-info-TopInfo__hideOnMobile--PKe4o"})
        address = details[1].text
        phone = details[2].text
    except:
        print('\t\t\terror recieving address and phone')

    try:
        header = rest_html.findAll("span", { "class":"restaurants-detail-top-info-TopInfo__infoCell--17Pql restaurants-detail-top-info-TopInfo__tags--2stjx"})[0].findAll("a")
        # price = header[0].text
        cusine = ''
        for i in range(len(header)):
                cusine += (header[i].text + ",")
    except:
        print('\t\t\terror reciveing price and cusine')

    try:
        email = rest_html.findAll("div", { "class":"restaurants-detail-overview-cards-LocationOverviewCard__detailLink--iyzJI restaurants-detail-overview-cards-LocationOverviewCard__contactItem--1flT6"})[1].a["href"]
        email = email.split(":")[1].split("?")[0]
    except:
        print('\t\t\terror reciveing email')

    # writing to csv
    # row = [name, address, phone, price, cusine, email, state_name]
    writer.writerow({
        'name': name,
        "address": address,
        "phone": phone,
        "cusine": cusine,
        "email": email,
        "state": state_name,
    })
    outFile.flush()

def main():
    outFile = open("data3.csv", "w", newline='')
    csvWriter = csv.DictWriter(outFile, fieldnames=colums)
    csvWriter.writeheader()
    init(csvWriter, outFile)
main()
