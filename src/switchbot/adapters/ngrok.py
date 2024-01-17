import requests


def get_ngrok_public_url():
    try:
        response = requests.get('http://127.0.0.1:4040/api/tunnels')
        response.raise_for_status()  # 這將在響應代碼不是 200 時引發一個異常

        data = response.json()
        return data.get('tunnels')[0].get('public_url')
    except requests.exceptions.RequestException:
        return None


if __name__ == "__main__":
    print(get_ngrok_public_url())

