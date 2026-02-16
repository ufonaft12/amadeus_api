import requests
import pandas as pd
from typing import Optional, List, Dict, Any

class AmadeusClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.token: Optional[str] = None
        self.base_url = "https://test.api.amadeus.com/v1"

    def get_token(self) -> bool:
        """Получение OAuth 2.0 токена"""
        auth_url = f"{self.base_url}/security/oauth2/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret
        }
        try:
            res = requests.post(auth_url, data=payload, timeout=10)
            res.raise_for_status()
            self.token = res.json().get("access_token")
            return True
        except Exception as e:
            print(f"Ошибка авторизации: {e}")
            return False

    def fetch_locations_paginated(self, keyword: str, page_limit: int = 10, max_pages: int = 3) -> pd.DataFrame:
        """Инкрементальная загрузка данных с пагинацией"""
        all_records = []
        # Мы используем page_limit из аргументов вместо захардкоженного limit
        
        for i in range(max_pages):  # <-- ИСПРАВЛЕНО: было pages
            offset = i * page_limit
            params = {
                "subType": "CITY,AIRPORT",
                "keyword": keyword,
                "page[limit]": page_limit,
                "page[offset]": offset
            }
            headers = {"Authorization": f"Bearer {self.token}"}
            
            try:
                print(f"Загрузка страницы {i+1} (смещение {offset})...")
                res = requests.get(f"{self.base_url}/reference-data/locations", headers=headers, params=params)
                res.raise_for_status()
                batch = res.json().get('data', [])
                
                if not batch: break
                all_records.extend(batch)
                
            except Exception as e:
                print(f"Ошибка на странице {i+1}: {e}")
                break

        # Создаем DataFrame и удаляем возможные дубликаты
        df = pd.json_normalize(all_records)
        return df.drop_duplicates(subset=['iataCode']) if not df.empty else df