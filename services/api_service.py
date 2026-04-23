import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime,date
from html.parser import HTMLParser

class WeatherAPI:
    BASE_URL = "https://api.openweathermap.org"

    DEFAULT_KEY = "7e9d2544799ce0b02bb56046ab0e878e"

    def __init__(self,api_key:str=None):
        self._api_key = api_key or self.DEFAULT_KEY

    def lay_thoi_tiet(self, thanh_pho:str = "Ho CHi Minh City", quoc_gia:str="VN") -> dict:
        params = urllib.parse.urlencode({
            "q": f"{thanh_pho}, {quoc_gia}",
            "appid": self._api_key,
            "units": "metric",
            "lang": "vi",
        })

        url = f"{self.BASE_URL}?{params}"

        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise ConnectionError(f"API lỗi HTTP {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise ConnectionError(f"Không kết nối được: {e.reason}")
        except Exception as e:
            raise ConnectionError(f"Lỗi không xác định: {e}")

        return self._xu_ly_ket_qua(data)

    @staticmethod
    def _xu_ly_ket_qua(data: dict) -> dict:
        weather = data.get("weather", [{}])[0]
        main = data.get("main", {})
        wind = data.get("wind", {})
        sys_ = data.get("sys", {})

        return {
            "thanh_pho": data.get("name", ""),
            "quoc_gia": sys_.get("country", ""),
            "mo_ta": weather.get("description", "").capitalize(),
            "nhiet_do": round(main.get("temp", 0), 1),
            "cam_giac": round(main.get("feels_like", 0), 1),
            "do_am": main.get("humidity", 0),
            "gio": round(wind.get("speed", 0) * 3.6, 1),  # m/s → km/h
            "icon_ma": weather.get("icon", "01d"),
            "icon_emoji": _ma_icon_sang_emoji(weather.get("icon", "01d")),
            "cap_nhat": datetime.now().strftime("%H:%M %d/%m/%Y"),
        }


def _ma_icon_sang_emoji(ma: str) -> str:
    bang = {
        "01": "☀️", "02": "⛅", "03": "☁️", "04": "☁️",
        "09": "🌧️", "10": "🌦️", "11": "⛈️", "13": "❄️", "50": "🌫️",
    }
    prefix = ma[:2]
    return bang.get(prefix, "🌡️")


class _HolidayHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._in_table = False
        self._in_row = False
        self._in_cell = False
        self._cells = []
        self._row = []
        self.holidays = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "table":
            self._in_table = True
        elif tag == "tr" and self._in_table:
            self._in_row = True
            self._row = []
        elif tag in ("td", "th") and self._in_row:
            self._in_cell = True

    def handle_endtag(self, tag):
        if tag == "table":
            self._in_table = False
        elif tag == "tr" and self._in_table:
            self._in_row = False
            if len(self._row) >= 2:
                self.holidays.append({
                    "ngay": self._row[0].strip(),
                    "ten": self._row[1].strip(),
                    "loai": self._row[2].strip() if len(self._row) > 2 else "Lễ",
                })
        elif tag in ("td", "th") and self._in_row:
            self._in_cell = False

    def handle_data(self, data):
        if self._in_cell:
            self._row.append(data)

class HolidayCrawler:
    URL ="https://vi.wikipedia.org/wiki/Các_ngày_lễ_ở_Việt_Nam"

    HOLIDAYS_FALLBACK = [
        {"ngay": "01/01", "ten": "Tết Dương lịch", "loai": "Quốc lễ"},
        {"ngay": "30/04", "ten": "Ngày Giải phóng", "loai": "Quốc lễ"},
        {"ngay": "01/05", "ten": "Ngày Quốc tế Lao động", "loai": "Quốc lễ"},
        {"ngay": "02/09", "ten": "Quốc khánh", "loai": "Quốc lễ"},
        {"ngay": "20/11", "ten": "Ngày Nhà giáo VN", "loai": "Kỷ niệm"},
        {"ngay": "08/03", "ten": "Ngày Quốc tế Phụ nữ", "loai": "Kỷ niệm"},
        {"ngay": "26/03", "ten": "Ngày Thành lập Đoàn", "loai": "Kỷ niệm"},
        {"ngay": "01/06", "ten": "Ngày Quốc tế Thiếu nhi", "loai": "Kỷ niệm"},
    ]

    def lay_ngay_le(self, nam: int = None) -> list[dict]:
        nam = nam or datetime.now().year
        try:
            req = urllib.request.Request(
                self.URL,
                headers={"User-Agent": "Microsoft Edge"}
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                html = resp.read().decode("utf-8", errors="ignore")

            parser = _HolidayHTMLParser()
            parser.feed(html)

            ket_qua = parser.holidays
            # Lọc bỏ header và hàng trống
            ket_qua = [h for h in ket_qua
                       if h["ngay"] and h["ten"]
                       and h["ngay"].lower() not in ("ngày", "date", "")]

            if ket_qua:
                return ket_qua[:20]

        except Exception:
            pass

        return self.HOLIDAYS_FALLBACK

    def ngay_le_sap_den(self, so_ngay: int = 30) -> list[dict]:
        hom_nay = date.today()
        nam = hom_nay.year
        ket_qua = []

        for holiday in self.lay_ngay_le(nam):
            ngay_str = holiday.get("ngay", "")
            # Thử parse DD/MM
            try:
                parts = ngay_str.split("/")
                if len(parts) >= 2:
                    ngay_le = date(nam, int(parts[1]), int(parts[0]))
                    delta = (ngay_le - hom_nay).days
                    if 0 <= delta <= so_ngay:
                        ket_qua.append({**holiday, "con_lai": delta})
            except (ValueError, IndexError):
                continue

        return sorted(ket_qua, key=lambda x: x["con_lai"])


class ExternalDataService:
    CACHE_PHUT = 10

    def __init__(self, weather_api_key: str = None):
        self._weather_api = WeatherAPI(weather_api_key)
        self._crawler = HolidayCrawler()
        self._cache_thoi_tiet: dict = {}
        self._cache_ngay_le: list = []
        self._lan_cuoi_cap_nhat_tt = None
        self._lan_cuoi_cap_nhat_nl = None

    def _het_han_cache(self, thoi_diem) -> bool:
        if thoi_diem is None:
            return True
        delta = (datetime.now() - thoi_diem).total_seconds()
        return delta > self.CACHE_PHUT * 60

    def lay_thoi_tiet(self, thanh_pho: str = "Ho Chi Minh City") -> dict:
        if self._het_han_cache(self._lan_cuoi_cap_nhat_tt):
            try:
                self._cache_thoi_tiet = self._weather_api.lay_thoi_tiet(thanh_pho)
                self._lan_cuoi_cap_nhat_tt = datetime.now()
            except ConnectionError as e:
                self._cache_thoi_tiet = {"loi": str(e)}
        return self._cache_thoi_tiet

    def lay_ngay_le_sap_den(self, so_ngay: int = 30) -> list[dict]:
        if self._het_han_cache(self._lan_cuoi_cap_nhat_nl):
            self._cache_ngay_le = self._crawler.ngay_le_sap_den(so_ngay)
            self._lan_cuoi_cap_nhat_nl = datetime.now()
        return self._cache_ngay_le

    def lay_tat_ca_ngay_le(self) -> list[dict]:
        return self._crawler.lay_ngay_le()