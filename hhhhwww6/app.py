from __future__ import division
from flask import Flask, render_template, jsonify, request
import requests
import json
import decimal

movie_response = requests.get('https://api.themoviedb.org/3/trending/movie/day?api_key=0cb4bcce49dd222da8658304855509d2')
tv_response = requests.get('https://api.themoviedb.org/3/tv/airing_today?api_key=0cb4bcce49dd222da8658304855509d2&language=en-US&page=1')
#print(movie_response)
#print(tv_response)
movie_jason = movie_response.json()
#movie_jason = movie_jason['results'][0]['title']
movie_jason = movie_jason['results'][:5]
#print(movie_jason)

movielist = []
for result in movie_jason:
 movielist.append({'title': result['title'], 'path': result['backdrop_path'], 'date': result['release_date']})
print(movielist)

tv_jason = tv_response.json()
tv_jason = tv_jason['results'][:5]
tvlist = []
for result in tv_jason:
 tvlist.append({'name': result['name'], 'path': result['backdrop_path'], 'date': result['first_air_date']})
print(tvlist)
#print(tv_jason)
data = [movielist,tvlist]

def genre(result,cate,num):
    if cate == 1:
        resp = requests.get('https://api.themoviedb.org/3/genre/movie/list?api_key=0cb4bcce49dd222da8658304855509d2&language=en-US')
    if cate == 2:
        resp = requests.get('https://api.themoviedb.org/3/genre/tv/list?api_key=0cb4bcce49dd222da8658304855509d2&language=en-US')
    
    resp = resp.json()
    resp = resp['genres']
    genre_ids = []
    
    if num == 0:
        for x in result['genre_ids']:
            for y in resp:
                if x == y['id']:
                    genre_ids.append(y['name'])
    if num == 1:
        for x in result['genres']:
            genre_ids.append(x['name'])
    return genre_ids

app = Flask(__name__)

@app.route('/')
def home():
   return app.send_static_file('hw6_home.html')
   
@app.route('/search',methods=['GET'])
def search():
    return jsonify(data)
    
@app.route('/detail',methods=['GET','POST'])
def detail():
    id = request.form["id"]
    type = request.form["type"]
    print(id,type)
    if type == "movie":
        url = 'https://api.themoviedb.org/3/movie/'+id+'?api_key=0cb4bcce49dd222da8658304855509d2&language=en-US';
        credit = 'https://api.themoviedb.org/3/movie/'+id+'/credits?api_key=0cb4bcce49dd222da8658304855509d2&language=en-US';
        review = 'https://api.themoviedb.org/3/movie/'+id+'/reviews?api_key=0cb4bcce49dd222da8658304855509d2&language=en-US&page=1';
    if type == "tv":
        url = 'https://api.themoviedb.org/3/tv/'+id+'?api_key=0cb4bcce49dd222da8658304855509d2&language=en-US';
        credit = 'https://api.themoviedb.org/3/tv/'+id+'/credits?api_key=0cb4bcce49dd222da8658304855509d2&language=en-US';
        review = 'https://api.themoviedb.org/3/tv/'+id+'/reviews?api_key=0cb4bcce49dd222da8658304855509d2&language=en-US&page=1';
    print(url)
    print(credit)
    print(review)
    creditresp = requests.get(credit)
    reviewresp = requests.get(review)
    response = requests.get(url)
    credits = creditresp.json()
    reviews = reviewresp.json()
    credits = credits['cast'][:8]
    reviews = reviews['results'][:5]
    search = response.json()
    print("reviews:",reviews)
    print("credits:",credits)
    print("search:",search)
    searchlist = []
    credit = []
    review = []
    for result in credits:
        credit.append({'name':result['name'],'profile_path':result['profile_path'],'character':result['character']})
    for result in reviews:
        if result['author_details']['rating'] is None:
            vote = ""
        else:
            vote = float(result['author_details']['rating'])/2
        review.append({'username':result['author_details']['username'],'content':result['content'],'rating':vote,'created_at':result['created_at']})
    if type == "movie":
        genre_ids = genre(search,1,1)
        vote = float(search['vote_average'])/2
        searchlist.append({'id': search['id'], 'title': search['title'], 'runtime': search['runtime'], 'date': search['release_date'], 'spoken_languages': search['spoken_languages'], 'vote_avg': vote, 'vote_count': search['vote_count'], 'poster_path': search['poster_path'], 'backdrop_path':search['backdrop_path'], 'genre': genre_ids})
    
    if type == "tv":
        genre_ids = genre(search,2,1)
        vote = float(search['vote_average'])/2
        searchlist.append({'id': search['id'], 'title': search['name'], 'runtime': search['episode_run_time'], 'date': search['first_air_date'], 'spoken_languages': search['spoken_languages'], 'vote_avg': vote, 'vote_count': search['vote_count'], 'poster_path': search['poster_path'], 'backdrop_path':search['backdrop_path'], 'genre': genre_ids, 'overview':search['overview'], 'number_of_seasons':search['number_of_seasons']})
    print(credit)
    print(review)
    wrap = [searchlist, credit, review]
    #print(searchlist)
    return jsonify(wrap)
     
@app.route('/result',methods=['GET','POST'])
def result():
    print(request.method)
    if request.method == "POST":
        d={}
        key = request.form["key"]
        #key = str(key).split()
        key.replace(" ", "%20")
        
        cate = request.form["cate"]
        
        #print(key,cate)
        url = 'https://api.themoviedb.org/3/search/' + str(cate) + '?api_key=0cb4bcce49dd222da8658304855509d2' + '&language=en-US&query='+key+'&page=1&include_adult=false'
        print(url)
        response = requests.get(url)
        search = response.json()
        #print(search)
        if cate == "multi":
            for item in search['results']:
                print(item['media_type'])
                if item['media_type'] == "person":
                    search['results'].remove(item);
        
        search = search['results'][:10]
        print(search)
        searchlist = []
        genre_ids = []
        if cate == "movie" :
            for result in search:
                genre_ids = genre(result,1,0)
                vote = float(result['vote_average'])/2
                searchlist.append({'id': result['id'], 'title': result['title'], 'overview': result['overview'], 'path': result['poster_path'], 'date': result['release_date'], 'vote_avg': vote, 'vote_count': result['vote_count'], 'genre': genre_ids, 'media_type':"movie"})
                
        elif cate == "tv" :
            for result in search:
                genre_ids = genre(result,2,0)
                vote = float(result['vote_average'])/2
                searchlist.append({'id': result['id'], 'title': result['name'], 'overview': result['overview'], 'path': result['poster_path'], 'date': result['first_air_date'], 'vote_avg': vote, 'vote_count': result['vote_count'], 'genre': genre_ids,  'media_type':"tv"})
        else :
            for result in search:
                genre_ids = genre(result,2,0)
                vote = float(result['vote_average'])/2
                if result['media_type'] == "movie":
                    searchlist.append({'id': result['id'], 'title': result['title'], 'overview': result['overview'], 'path': result['poster_path'], 'date': result['release_date'], 'vote_avg': vote, 'vote_count': result['vote_count'], 'genre': genre_ids,  'media_type':result['media_type']})
                if result['media_type'] == "tv":
                    searchlist.append({'id': result['id'], 'title': result['name'], 'overview': result['overview'], 'path': result['poster_path'], 'date': result['first_air_date'], 'vote_avg': vote, 'vote_count': result['vote_count'], 'genre': genre_ids,  'media_type':result['media_type']})
        
        print(searchlist)
        return jsonify(searchlist)
    
        
        
        
   


if __name__ == '__main__':
   app.run()


 
