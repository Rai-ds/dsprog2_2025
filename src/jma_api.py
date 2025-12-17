import requests

AREA_URL = "http://www.jma.go.jp/bosai/common/const/area.json"

def fetch_area_list():
    response = requests.get(AREA_URL)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    data = fetch_area_list()
    class20s = data["class20s"]

    
    for i, (code, info) in enumerate(class20s.items()):
        print(code, info["name"])
        if i == 4:
            break

