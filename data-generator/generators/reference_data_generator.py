"""
Reference Data Generator
========================

Generates reference data for the EuroStyle Fashion system:
- European geography data
- Fashion calendar events
"""

from generators.base_generator import BaseGenerator

class ReferenceDataGenerator(BaseGenerator):
    """Generates reference data tables."""
    
    def __init__(self, config, db_connector):
        """Initialize the reference data generator."""
        super().__init__(config, db_connector)
    
    def generate_european_geography(self) -> bool:
        """Generate European geography reference data."""
        self.logger.info("🌍 Generating European geography data...")
        
        # European cities and regions data
        geo_data = []
        
        # Netherlands 🇳🇱
        netherlands_cities = [
            {"city": "Amsterdam", "region": "Noord-Holland", "population": 872680, "postal_codes": ["1000", "1001", "1012", "1017"], "lat": 52.3676, "lon": 4.9041},
            {"city": "Rotterdam", "region": "Zuid-Holland", "population": 651446, "postal_codes": ["3000", "3011", "3012"], "lat": 51.9225, "lon": 4.47917},
            {"city": "Utrecht", "region": "Utrecht", "population": 357694, "postal_codes": ["3500", "3511", "3512"], "lat": 52.0907, "lon": 5.1214},
            {"city": "Eindhoven", "region": "Noord-Brabant", "population": 234235, "postal_codes": ["5600", "5611", "5612"], "lat": 51.4416, "lon": 5.4697},
            {"city": "Groningen", "region": "Groningen", "population": 233218, "postal_codes": ["9700", "9711", "9712"], "lat": 53.2194, "lon": 6.5665},
            {"city": "Tilburg", "region": "Noord-Brabant", "population": 219800, "postal_codes": ["5000", "5011", "5012"], "lat": 51.5555, "lon": 5.0913},
            {"city": "Almere", "region": "Flevoland", "population": 214715, "postal_codes": ["1300", "1315", "1321"], "lat": 52.3508, "lon": 5.2647}
        ]
        
        # Belgium 🇧🇪
        belgium_cities = [
            {"city": "Brussels", "region": "Brussels-Capital", "population": 1209000, "postal_codes": ["1000", "1020", "1050"], "lat": 50.8505, "lon": 4.3488},
            {"city": "Antwerp", "region": "Vlaanderen", "population": 530504, "postal_codes": ["2000", "2018", "2020"], "lat": 51.2194, "lon": 4.4025},
            {"city": "Ghent", "region": "Vlaanderen", "population": 262219, "postal_codes": ["9000", "9030", "9040"], "lat": 51.0543, "lon": 3.7174},
            {"city": "Charleroi", "region": "Wallonia", "population": 201816, "postal_codes": ["6000", "6010", "6020"], "lat": 50.4108, "lon": 4.4446},
            {"city": "Liège", "region": "Wallonia", "population": 197013, "postal_codes": ["4000", "4020", "4030"], "lat": 50.6326, "lon": 5.5797}
        ]
        
        # Germany 🇩🇪
        germany_cities = [
            {"city": "Berlin", "region": "Berlin", "population": 3677472, "postal_codes": ["10115", "10117", "10119"], "lat": 52.5200, "lon": 13.4050},
            {"city": "Hamburg", "region": "Hamburg", "population": 1904915, "postal_codes": ["20095", "20097", "20099"], "lat": 53.5511, "lon": 9.9937},
            {"city": "Munich", "region": "Bayern", "population": 1488202, "postal_codes": ["80331", "80333", "80335"], "lat": 48.1351, "lon": 11.5820},
            {"city": "Cologne", "region": "Nordrhein-Westfalen", "population": 1087863, "postal_codes": ["50667", "50668", "50670"], "lat": 50.9375, "lon": 6.9603},
            {"city": "Frankfurt", "region": "Hessen", "population": 753056, "postal_codes": ["60311", "60313", "60316"], "lat": 50.1109, "lon": 8.6821},
            {"city": "Stuttgart", "region": "Baden-Württemberg", "population": 626275, "postal_codes": ["70173", "70174", "70176"], "lat": 48.7758, "lon": 9.1829},
            {"city": "Düsseldorf", "region": "Nordrhein-Westfalen", "population": 619294, "postal_codes": ["40210", "40211", "40212"], "lat": 51.2277, "lon": 6.7735}
        ]
        
        # France 🇫🇷
        france_cities = [
            {"city": "Paris", "region": "Île-de-France", "population": 2161000, "postal_codes": ["75001", "75002", "75003"], "lat": 48.8566, "lon": 2.3522},
            {"city": "Lyon", "region": "Auvergne-Rhône-Alpes", "population": 518635, "postal_codes": ["69001", "69002", "69003"], "lat": 45.7640, "lon": 4.8357},
            {"city": "Marseille", "region": "Provence-Alpes-Côte d'Azur", "population": 868277, "postal_codes": ["13001", "13002", "13003"], "lat": 43.2965, "lon": 5.3698},
            {"city": "Toulouse", "region": "Occitanie", "population": 479553, "postal_codes": ["31000", "31100", "31200"], "lat": 43.6047, "lon": 1.4442},
            {"city": "Nice", "region": "Provence-Alpes-Côte d'Azur", "population": 342669, "postal_codes": ["06000", "06100", "06200"], "lat": 43.7102, "lon": 7.2620}
        ]
        
        # Luxembourg 🇱🇺
        luxembourg_cities = [
            {"city": "Luxembourg City", "region": "Luxembourg", "population": 125133, "postal_codes": ["1009", "1011", "1014"], "lat": 49.6116, "lon": 6.1319},
            {"city": "Esch-sur-Alzette", "region": "Luxembourg", "population": 35382, "postal_codes": ["4001", "4002", "4005"], "lat": 49.4958, "lon": 5.9806}
        ]
        
        # Generate geo records
        countries = [
            {"code": "NL", "name": "Netherlands", "cities": netherlands_cities, "timezone": "Europe/Amsterdam", "vat": 21.0},
            {"code": "BE", "name": "Belgium", "cities": belgium_cities, "timezone": "Europe/Brussels", "vat": 21.0},
            {"code": "DE", "name": "Germany", "cities": germany_cities, "timezone": "Europe/Berlin", "vat": 19.0},
            {"code": "FR", "name": "France", "cities": france_cities, "timezone": "Europe/Paris", "vat": 20.0},
            {"code": "LU", "name": "Luxembourg", "cities": luxembourg_cities, "timezone": "Europe/Luxembourg", "vat": 17.0}
        ]
        
        import random
        from datetime import datetime
        
        geo_id = 1
        for country in countries:
            for city_info in country["cities"]:
                for postal_code in city_info["postal_codes"]:
                    # Calculate economic metrics based on city size and country
                    base_income = {"NL": 45000, "BE": 42000, "DE": 48000, "FR": 41000, "LU": 65000}[country["code"]]
                    city_multiplier = min(1.3, city_info["population"] / 500000)  # Larger cities = higher income
                    avg_income = base_income * city_multiplier
                    
                    # Fashion market size based on population and income
                    fashion_market = (city_info["population"] * avg_income * 0.02) / 1000000  # 2% of income on fashion
                    
                    # Competition density based on city size
                    if city_info["population"] > 1000000:
                        competition = "high"
                    elif city_info["population"] > 500000:
                        competition = "medium"
                    else:
                        competition = "low"
                    
                    geo_record = {
                        "geo_id": f"GEO_{geo_id:06d}",
                        "country_code": country["code"],
                        "country_name": country["name"],
                        "region": city_info["region"],
                        "city": city_info["city"],
                        "postal_code": postal_code,
                        "latitude": city_info["lat"] + random.uniform(-0.01, 0.01),  # Small variation
                        "longitude": city_info["lon"] + random.uniform(-0.01, 0.01),
                        "population": int(city_info["population"] * random.uniform(0.95, 1.05)),  # Small variation
                        "economic_index": round(city_multiplier, 2),
                        "timezone": country["timezone"],
                        "fashion_market_size_eur": round(fashion_market, 2),
                        "competition_density": competition,
                        "avg_income_eur": round(avg_income, 2),
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                    
                    geo_data.append(geo_record)
                    geo_id += 1
        
        # Insert data in batches
        success = self.process_in_batches("european_geography", iter(geo_data), len(geo_data))
        
        if success:
            self.logger.info(f"✅ Generated {len(geo_data)} European geography records")
            return True
        else:
            self.logger.error("❌ Failed to generate European geography data")
            return False
    
    def generate_fashion_calendar(self) -> bool:
        """Generate fashion calendar reference data."""
        self.logger.info("📅 Generating fashion calendar data...")
        
        from datetime import datetime, date, timedelta
        import random
        
        # Get time range from config
        time_config = self.config.get('time_range', {})
        start_date = datetime.strptime(time_config.get('fashion_calendar_start', '2020-01-01'), '%Y-%m-%d').date()
        end_date = datetime.strptime(time_config.get('fashion_calendar_end', '2026-12-31'), '%Y-%m-%d').date()
        
        calendar_data = []
        
        # Define events by country and type
        annual_events = {
            # Fashion Industry Events (All Countries)
            "global": [
                {"name": "New Year's Day", "date": "01-01", "type": "shopping-holiday", "impact": "medium", "lift": 15.0, "season": "Fall/Winter 2024", "phase": "clearance"},
                {"name": "Valentine's Day", "date": "02-14", "type": "shopping-holiday", "impact": "medium", "lift": 25.0, "season": "Spring/Summer 2024", "phase": "launch"},
                {"name": "International Women's Day", "date": "03-08", "type": "cultural-holiday", "impact": "low", "lift": 10.0, "season": "Spring/Summer 2024", "phase": "launch"},
                {"name": "Spring Collection Launch", "date": "03-15", "type": "fashion-event", "impact": "high", "lift": 40.0, "season": "Spring/Summer 2024", "phase": "launch"},
                {"name": "Mother's Day", "date": "05-12", "type": "shopping-holiday", "impact": "medium", "lift": 20.0, "season": "Spring/Summer 2024", "phase": "peak"},
                {"name": "Summer Sale Start", "date": "07-01", "type": "shopping-holiday", "impact": "high", "lift": 35.0, "season": "Spring/Summer 2024", "phase": "markdown"},
                {"name": "Back to School", "date": "08-15", "type": "shopping-holiday", "impact": "medium", "lift": 30.0, "season": "Fall/Winter 2024", "phase": "launch"},
                {"name": "Fall Collection Launch", "date": "09-01", "type": "fashion-event", "impact": "high", "lift": 45.0, "season": "Fall/Winter 2024", "phase": "launch"},
                {"name": "Black Friday", "date": "11-24", "type": "shopping-holiday", "impact": "high", "lift": 60.0, "season": "Fall/Winter 2024", "phase": "peak"},
                {"name": "Cyber Monday", "date": "11-27", "type": "shopping-holiday", "impact": "high", "lift": 50.0, "season": "Fall/Winter 2024", "phase": "peak"},
                {"name": "Christmas Shopping Peak", "date": "12-15", "type": "shopping-holiday", "impact": "high", "lift": 55.0, "season": "Fall/Winter 2024", "phase": "peak"},
                {"name": "Boxing Day Sales", "date": "12-26", "type": "shopping-holiday", "impact": "high", "lift": 45.0, "season": "Fall/Winter 2024", "phase": "clearance"},
            ],
            
            # Netherlands specific
            "NL": [
                {"name": "King's Day", "date": "04-27", "type": "cultural-holiday", "impact": "medium", "lift": 20.0, "season": "Spring/Summer 2024", "phase": "peak"},
                {"name": "Sinterklaas", "date": "12-05", "type": "cultural-holiday", "impact": "medium", "lift": 25.0, "season": "Fall/Winter 2024", "phase": "peak"},
            ],
            
            # Belgium specific
            "BE": [
                {"name": "Belgian National Day", "date": "07-21", "type": "cultural-holiday", "impact": "low", "lift": 10.0, "season": "Spring/Summer 2024", "phase": "markdown"},
                {"name": "Saint Nicholas", "date": "12-06", "type": "cultural-holiday", "impact": "medium", "lift": 20.0, "season": "Fall/Winter 2024", "phase": "peak"},
            ],
            
            # Germany specific
            "DE": [
                {"name": "Easter Monday", "date": "04-01", "type": "cultural-holiday", "impact": "medium", "lift": 15.0, "season": "Spring/Summer 2024", "phase": "launch"},
                {"name": "German Unity Day", "date": "10-03", "type": "cultural-holiday", "impact": "low", "lift": 8.0, "season": "Fall/Winter 2024", "phase": "launch"},
                {"name": "Oktoberfest Fashion", "date": "09-20", "type": "fashion-event", "impact": "medium", "lift": 30.0, "season": "Fall/Winter 2024", "phase": "launch"},
            ],
            
            # France specific
            "FR": [
                {"name": "Bastille Day", "date": "07-14", "type": "cultural-holiday", "impact": "low", "lift": 12.0, "season": "Spring/Summer 2024", "phase": "markdown"},
                {"name": "Fashion Week Paris SS", "date": "03-01", "type": "fashion-event", "impact": "high", "lift": 35.0, "season": "Spring/Summer 2024", "phase": "launch"},
                {"name": "Fashion Week Paris FW", "date": "09-25", "type": "fashion-event", "impact": "high", "lift": 40.0, "season": "Fall/Winter 2024", "phase": "launch"},
            ],
            
            # Luxembourg specific
            "LU": [
                {"name": "National Day Luxembourg", "date": "06-23", "type": "cultural-holiday", "impact": "low", "lift": 10.0, "season": "Spring/Summer 2024", "phase": "peak"},
            ]
        }
        
        # Generate calendar entries for each year
        current_date = start_date
        while current_date <= end_date:
            year = current_date.year
            
            # Add global events
            for event in annual_events["global"]:
                event_date = datetime.strptime(f"{year}-{event['date']}", '%Y-%m-%d').date()
                if start_date <= event_date <= end_date:
                    for country in ["NL", "BE", "DE", "FR", "LU"]:
                        calendar_data.append({
                            "date": event_date,
                            "country_code": country,
                            "event_name": event["name"],
                            "event_type": event["type"],
                            "impact_level": event["impact"],
                            "expected_sales_lift": event["lift"],
                            "fashion_season": event["season"].replace("2024", str(year)),
                            "collection_phase": event["phase"],
                            "campaign_opportunity": event["type"] in ["fashion-event", "shopping-holiday"],
                            "inventory_planning": event["impact"] == "high",
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        })
            
            # Add country-specific events
            for country_code in ["NL", "BE", "DE", "FR", "LU"]:
                if country_code in annual_events:
                    for event in annual_events[country_code]:
                        event_date = datetime.strptime(f"{year}-{event['date']}", '%Y-%m-%d').date()
                        if start_date <= event_date <= end_date:
                            calendar_data.append({
                                "date": event_date,
                                "country_code": country_code,
                                "event_name": event["name"],
                                "event_type": event["type"],
                                "impact_level": event["impact"],
                                "expected_sales_lift": event["lift"],
                                "fashion_season": event["season"].replace("2024", str(year)),
                                "collection_phase": event["phase"],
                                "campaign_opportunity": event["type"] in ["fashion-event", "shopping-holiday"],
                                "inventory_planning": event["impact"] == "high",
                                "created_at": datetime.now(),
                                "updated_at": datetime.now()
                            })
            
            # Move to next year
            current_date = date(year + 1, 1, 1)
        
        # Insert data in batches
        success = self.process_in_batches("fashion_calendar", iter(calendar_data), len(calendar_data))
        
        if success:
            self.logger.info(f"✅ Generated {len(calendar_data)} fashion calendar events")
            return True
        else:
            self.logger.error("❌ Failed to generate fashion calendar data")
            return False
    
    def generate_table_data(self, table_name: str) -> bool:
        """Generate data for a specific reference table."""
        if hasattr(self, f"generate_{table_name}"):
            return getattr(self, f"generate_{table_name}")()
        else:
            self.logger.error(f"❌ Unknown reference table: {table_name}")
            return False