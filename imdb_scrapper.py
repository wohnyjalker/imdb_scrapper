from requests import get
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from re import findall
from typing import Union



class Movie:

    IMDB_SEARCH_URL = 'https://www.imdb.com/find?ref_=nv_sr_fn&q={}'
    IMDB_URL = 'https://www.imdb.com{}'

    def __init__(self, title, title_url=None, rating=None, avg_time=None, img_url=None, soup=None):
        self.title = title.title()
        self.title_url = title_url #self.get_from_imdb(self.title)
        self.rating = rating
        self.avg_time = avg_time
        self.img_url = img_url
        self.soup = soup


    def __repr__(self):
        return f'{self.title}\nRating: {self.rating}\nAvg time: {self.avg_time}\nCover url:{self.img_url}'


    @staticmethod
    def get_from_imdb(title_to_find) -> Union[str, None]:
        '''bierze title oddaje url, url do title_url nastepnie przekazac do get_soup_from_url'''
        
        title_to_find = Movie.IMDB_SEARCH_URL.format(title_to_find.replace(' ', '+'))
        search = get(title_to_find).text
        soup = BeautifulSoup(search, 'lxml')
        url = soup.find('td', {'result_text'}).a.get('href')
        #print(url)
        return Movie.IMDB_URL.format(url)


    def get_soup_from_url(self):
        # bez .text zwraca <Response [200]> jak pobierze html
        # lub 404 itp itd
        # mozna uzyc do obslugi wyjatku
        try:
            temp = get(self.title_url).text
            self.soup = BeautifulSoup(temp, 'lxml')
        except:
            self.soup = None
            print("get soup error")
    
    def soup_to_soup(self, soup):
        self.soup = soup

    def get_rating(self):
        #soup = get(self.title_url)
        try:
            rating = self.soup.find('span', {'itemprop': 'ratingValue'}).text
            self.rating = rating.strip()
        except AttributeError as e:
            self.rating = None
            print(f"get rating error {e}")


    def get_avg_time(self):
        time = self.soup.find('time')
        time = findall('\d', time.text)
        try:
            h = int(time[0])*60
            m = int(''.join(time[1:]))
            if len(time) == 1:
                self.avg_time = int(time)
            elif len(time) == 3:
                self.avg_time = h + m   
            self.avg_time = h + m
        except ValueError as e:
            self.avg_time = None
            print(f"get_avg_time error:{e}")
            

    def get_cover(self):
        ''' zwraca url do okladki'''
        title_alt = self.title + ' Poster'
        try:
            cover = self.soup.find('img', {'alt': title_alt})
            img_url = cover.get('src')
            self.img_url = img_url
        except AttributeError as e:
            self.img_url = None
            print(f"get_cover error {e}")


class Series(Movie):
    '''class Series'''
    def __init__(self, title, title_url=None, rating=None,
                        avg_time=None, img_url=None, soup=None,
                        seasons=None, episodes=None,):
        super().__init__(title, title_url=None, rating=None, avg_time=None, img_url=None, soup=None)
        self.seasons = seasons
        self.episodes = episodes


    def __repr__(self):
        return f'{self.title}\nRating: {self.rating}\nNo of seasons: {self.seasons} \
            \nNo of episodes: {self.episodes}\nEp time: {self.avg_time} \
            \nCover url:{self.img_url}'


    def get_avg_time(self):
        ''' zwraca czas odcinka w minutach'''
        time = self.soup.find('time')
        time = findall('\d', time.text)
        # time bedzie miec liste jezeli czas odcinka to 21min
        # to: ['2','1']
        # jezeli bedzie miec ['1'] tzn ze jest to 1h czyli zmienic w minuty
        if len(time) == 1:
            self.avg_time = 60
        else:
            self.avg_time = int(''.join(time))


    def get_seasons(self):
        '''przyjmuje soup, zwraca liste(str) sezonów '''
        try:
            seasons_soup = self.soup.find('div', {'class': 'seasons-and-year-nav'})
            # print(seasons_soup.children) zwraca <list_iterator object at 0x0>
            # trzeba zmienic na liste
            seasons_mess = list(seasons_soup.children)[7].text
            seasons = findall('\d', seasons_mess)
            self.seasons = int(max(seasons))
        except AttributeError as e:
            self.seasons = None
            print("seasons error: {e}")


    def get_episodes(self):
        '''zwraca liczbe odcinkow'''
        try:
            episodes = self.soup.find('span', {'class': 'bp_sub_heading'}).text
            if int(episodes.split(' ')[0]) >= 2019:
                self.episodes = self.soup.find('span', {'class': 'bp_heading'}).text
            self.episodes = int(episodes.split(' ')[0])
        except AttributeError as e:
            print(f"e: {e}")
            self.episodes = None

            
def is_series(title):
    '''sprawdza czy to film czy serial return tuple(Boolean, soup)
        ------------------------------------------
        zwraca soup aby nie wywolywac get_soup_from_url()
        i uniknac dwukrotnego wywolania requests.get dla jednego url'''

    title_url = Movie.get_from_imdb(title)    
    try:
        temp = get(title_url).text
        soup = BeautifulSoup(temp, 'lxml')
    except:
        soup = None
        print("cos nie tak")
        # <script>
        # <title>Stranger Things (TV Series 2016– ) - IMDb</title>
    is_series = soup.find('title').text
    if 'TV Series' in is_series:
        return True, soup
    return False, soup


def main():

    title_list = ['gra o tron', 'joker', 'terminator', 'peaky blinders', 'altered carbon', 'i am mother', 'gomorra']
    # title_list = ['peaky blinders', 'altered carbon']

    title = 'wounds'

    test = Movie(title)
    test.title_url = test.get_from_imdb(test.title)
    test.get_soup_from_url()
    test.get_avg_time()
    test.get_cover()
    test.get_rating()
    print(test)

    output = []
    for title in title_list:
        series, soup = is_series(title)
        if series:
            s = Series(title)
            # s.get_from_imdb(s.title)
            #s.get_soup_from_url()
            s.soup_to_soup(soup)
            s.get_rating()
            s.get_avg_time()
            s.get_episodes()
            s.get_seasons()
            s.get_cover()
            output.append(s)
        else:
            m = Movie(title)
            # m.get_from_imdb(m.title)
            # m.get_soup_from_url()
            m.soup_to_soup(soup)
            m.get_rating()
            m.get_avg_time()
            m.get_cover()
            output.append(m)

    for o in output:
        print(o)
        print('\n')        

if __name__ == '__main__':
    main()

