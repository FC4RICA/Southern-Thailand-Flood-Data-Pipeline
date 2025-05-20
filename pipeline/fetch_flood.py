import requests
import geopandas as gpd

def fetch_flood_data(api_key: str, base_url: str, bbox: list) -> gpd.GeoDataFrame:
  divided_bbox= divide_bbox(bbox, divisions = 12)
  records  = {}

  for sub_bbox in divided_bbox:
    print(f'Fetching data for bbox: {sub_bbox}')
    features = fetch_data_for_bbox(api_key, base_url, sub_bbox)

    for feature in features:
      records[feature['id']] = feature

  gdf = gpd.GeoDataFrame.from_features(records.values())
  return gdf

def divide_bbox(bbox: list, divisions: int = 4) -> list:
  min_lon, min_lat, max_lon, max_lat = bbox
  lon_step = (max_lon - min_lon) / divisions
  lat_step = (max_lat - min_lat) / divisions

  sub_boxes = []
  for i in range(divisions):
    for j in range(divisions):
      sub_boxes.append(
        [
          min_lon + i * lon_step,
          min_lat + j * lat_step,
          min_lon + (i + 1) * lon_step,
          min_lat + (j + 1) * lat_step,
        ]
      )
  return sub_boxes

def fetch_data_for_bbox(api_key: str, base_url: str, bbox: str, limit=10000) -> list:
  all_features = []
  offset = 0

  while True:
    url = f'{base_url}?bbox={','.join(map(str, bbox))}&limit={limit}&offset={offset}'
    try:
      response = requests.get(url, headers={'accept': 'application/json', 'API-Key': api_key})
      response.raise_for_status() 

      data = response.json()

      results = data.get('features', [])
      all_features.extend(results)

      # Break if there's no more data
      if len(results) < limit:
        break 

      offset += limit

    except requests.RequestException as e:
      print(f'An error occurred: {e}')
      break
  
  return all_features