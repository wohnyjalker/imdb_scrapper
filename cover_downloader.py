import imdb_scrapper as imdb
import time
import asyncio
from concurrent.futures import ProcessPoolExecutor


title_list = ['gra o tron', 'joker', 'terminator',
              'peaky blinders', 'altered carbon', 'i am mother', 'gomorra', 'stranger things', 'ozark', 'gossip girl']


def get_cover(_title):
    movie = imdb.Movie(_title)
    movie.title_url = imdb.Movie.get_from_imdb(_title)
    movie.get_soup_from_url()
    movie.get_cover()
    print(movie.img_url)
    # imdb.get aby uniknac podwojnego importowania requests.
    # W imdb_scrapper importowalem requests.get as get
    # nie wiem czy to dobre podejscie, na pewno malo czytelne
    if movie.img_url is not None:
        cover_url_response = imdb.get(movie.img_url)
        if cover_url_response.status_code == 200:
            with open('covers/{}.jpg'.format(_title), 'wb') as cover:
                cover.write(cover_url_response.content)

# async def download_covers(_list, )


print('Petla for i map')
start = time.time()
for _ in map(get_cover, title_list):
    pass
end = time.time()
for_execution_time = end - start

print('ProcessPoolExecutor <-- Executor ekstra nazwa:)')
start = time.time()
with ProcessPoolExecutor(max_workers=10) as executor:
    executor.map(get_cover, title_list)
end = time.time()
pp_executor_execution_time = end - start

msg = '{} {:.3} seconds'
print(msg.format('For loop', for_execution_time))
print(msg.format('Executor:)', pp_executor_execution_time))
