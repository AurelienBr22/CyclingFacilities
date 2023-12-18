import requests

def get_lat_lon(address, url='https://api-adresse.data.gouv.fr/search'):

    params = {'q': address, 'citycode': 75056}
    r = requests.get(url, params)
    try: return r.json()['features'][0]['geometry']['coordinates'][::-1]
    except: print(f'ERROR : {address}, STATUS CODE : {r.status_code}')
