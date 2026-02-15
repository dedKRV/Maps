import requests


def reverse_geocode(lon, lat):
    """Обратное геокодирование: получение адреса по координатам"""
    server_address = 'http://geocode-maps.yandex.ru/1.x/?'
    api_key = '8013b162-6b42-4997-9691-77b7074026e0'
    geocode_param = f"{lon},{lat}"
    geocoder_request = f'{server_address}apikey={api_key}&geocode={geocode_param}&format=json&kind=house'
    response = requests.get(geocoder_request)
    if response:
        try:
            json_response = response.json()
            feature_member = json_response["response"]["GeoObjectCollection"]["featureMember"]
            if not feature_member:
                print(f"Ничего не найдено по координатам: {lon},{lat}")
                return None
            toponym = feature_member[0]["GeoObject"]
            toponym_coordinates = toponym["Point"]["pos"]
            envelope = toponym["boundedBy"]['Envelope']
            l, d = envelope['lowerCorner'].split()
            r, t = envelope['upperCorner'].split()
            dx = abs(float(r) - float(l)) / 2
            dy = abs(float(t) - float(d)) / 2
            span = f"{dx},{dy}"
            coords = ','.join(toponym_coordinates.split())
            full_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            postal_code = None
            metadata = toponym["metaDataProperty"]["GeocoderMetaData"]
            if "Address" in metadata:
                address_data = metadata["Address"]
                if "postal_code" in address_data:
                    postal_code = address_data["postal_code"]
            return coords, span, full_address, postal_code
        except (KeyError, IndexError, TypeError) as e:
            print(f"Ошибка при обработке ответа для координат '{lon},{lat}': {e}")
            return None
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        return None


def geocode_coords(geocode):
    server_address = 'http://geocode-maps.yandex.ru/1.x/?'
    api_key = '8013b162-6b42-4997-9691-77b7074026e0'

    # Готовим запрос с указанием типа ответа
    geocoder_request = f'{server_address}apikey={api_key}&geocode={geocode}&format=json&kind=house'

    # Выполняем запрос.
    response = requests.get(geocoder_request)
    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()

        # ПРОВЕРКА: есть ли результаты поиска
        try:
            feature_member = json_response["response"]["GeoObjectCollection"]["featureMember"]
            if not feature_member:  # Если список пустой
                print(f"Ничего не найдено по запросу: {geocode}")
                return None

            # Получаем первый топоним из ответа геокодера.
            toponym = feature_member[0]["GeoObject"]
            toponym_coordinates = toponym["Point"]["pos"]
            envelope = toponym["boundedBy"]['Envelope']
            l, d = envelope['lowerCorner'].split()
            r, t = envelope['upperCorner'].split()
            dx = abs(float(r) - float(l)) / 2
            dy = abs(float(t) - float(d)) / 2
            span = f"{dx},{dy}"
            coords = ','.join(toponym_coordinates.split())
            full_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            postal_code = None
            metadata = toponym["metaDataProperty"]["GeocoderMetaData"]
            if "Address" in metadata:
                address_data = metadata["Address"]
                if "postal_code" in address_data:
                    postal_code = address_data["postal_code"]
            return coords, span, full_address, postal_code
        except (KeyError, IndexError, TypeError) as e:
            print(f"Ошибка при обработке ответа для запроса '{geocode}': {e}")
            return None
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        return None