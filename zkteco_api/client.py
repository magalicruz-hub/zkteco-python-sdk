import base64
import requests
from typing import Dict, List, Optional, Any

class ZKTecoAPIException(Exception):
    """Excepción personalizada para errores de la API ZKTeco."""
    pass

class ZKTecoClient:
    def __init__(self, base_url: str = "http://example.com/api/", timeout: int = 10):
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.timeout
            )
            if response.status_code >= 400:
                raise ZKTecoAPIException(f"Error HTTP {response.status_code}: {response.text}")
            return response.json()
        except requests.RequestException as e:
            raise ZKTecoAPIException(f"Error de conexión: {str(e)}")

    # Device Endpoints
    def get_devices(self, sn: Optional[str] = None, terminal_name: Optional[str] = None) -> List[Dict]:
        params = {}
        if sn: params["sh"] = sn
        if terminal_name: params["terminal_name"] = terminal_name
        return self._request("GET", "device/", params=params)

    def get_device(self, device_id: int) -> Dict:
        return self._request("GET", f"device/{device_id}/")

    def reboot_device(self, sn: str) -> Dict:
        return self._request("POST", "device/reboot/", data={"sn": sn})

    # User Endpoints
    def get_users(self) -> List[Dict]:
        return self._request("GET", "user/")

    def update_user(self, pin: int, first_name: Optional[str] = None, 
                    device_password: Optional[str] = None, dev_privilege: int = 0, 
                    card_no: Optional[str] = None, verify_mode: int = 0) -> Dict:
        payload = {"pin": pin, "dev_privilege": dev_privilege, "verify_mode": verify_mode}
        if first_name: payload["first_name"] = first_name
        if device_password: payload["device_password"] = device_password
        if card_no: payload["card_no"] = card_no
        return self._request("POST", "user/update_user/", data=payload)

    def delete_users(self, user_pins: List[int]) -> Dict:
        return self._request("POST", "user/delete_users/", data={"users": user_pins})

    # BioPhoto Endpoints
    def get_bio_photo(self, user_pin: int) -> Dict:
        return self._request("GET", "bio-photo/", params={"user": user_pin})

    def update_bio_photo(self, user_pin: int, photo_base64: str, device_sn: str) -> Dict:
        payload = {"user": user_pin, "photo_base64": photo_base64, "device": device_sn}
        return self._request("POST", "bio-photo/update_bio_photo/", data=payload)

    def delete_bio_photo(self, user_pin: int, device_sn: str) -> Dict:
        return self._request("POST", "bio-photo/delete_bio_photo/", data={"user": user_pin, "device": device_sn})

    # BioData Endpoints
    def get_bio_data(self, user_pin: Optional[int] = None, bio_type: Optional[int] = None, bio_index: Optional[int] = None) -> List[Dict]:
        params = {}
        if user_pin is not None: params["user"] = user_pin
        if bio_type is not None: params["bio_type"] = bio_type
        if bio_index is not None: params["bio_index"] = bio_index
        return self._request("GET", "biodata/", params=params)

    def update_bio_data(self, user_pin: int, device_sn: str, bio_tmp: str, 
                        bio_type: int = 1, bio_no: int = 0, bio_index: int = 0,
                        major_ver: Optional[str] = None, minor_ver: Optional[str] = None, bio_format: int = 0) -> Dict:
        payload = {
            "user": user_pin, "device": device_sn, "bio_tmp": bio_tmp,
            "bio_type": bio_type, "bio_no": bio_no, "bio_index": bio_index, "bio_format": bio_format
        }
        if major_ver: payload["major_ver"] = major_ver
        if minor_ver: payload["minor_ver"] = minor_ver
        return self._request("POST", "biodata/update_bio_data/", data=payload)

    def clear_bio_data(self, device_sn: str) -> Dict:
        return self._request("POST", "biodata/clear_bio_data/", data={"device": device_sn})

    # Transaction Endpoints
    def get_transactions(self, user_pin: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        params = {}
        if user_pin: params["user_pin"] = user_pin
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        return self._request("GET", "transaction/", params=params)

def encode_image_to_base64(file_path: str) -> str:
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')