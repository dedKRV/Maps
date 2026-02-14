import requests


def geocode_coords(geocode):
    server_address = 'http://geocode-maps.yandex.ru/1.x/?'
    api_key = '8013b162-6b42-4997-9691-77b7074026e0'

    # Готовим запрос.
    geocoder_request = f'{server_address}apikey={api_key}&geocode={geocode}&format=json'

    # Выполняем запрос.
    response = requests.get(geocoder_request)
    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()

        # Получаем первый топоним из ответа геокодера.
        # Согласно описанию ответа, он находится по следующему пути:
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # Координаты центра топонима:
        toponym_coordinates = toponym["Point"]["pos"]
        envelope = toponym["boundedBy"]['Envelope']
        l, d = envelope['lowerCorner'].split()
        r, t = envelope['upperCorner'].split()
        dx = abs(float(r) - float(l)) / 2
        dy = abs(float(t) - float(d)) / 2
        span = f"{dx},{dy}"
        coords = ','.join(toponym_coordinates.split())
        return coords, span
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")