from components.applications.defs._application_def import ApplicationDef

############################
class Seattle(ApplicationDef):
    
    def get_name(self):
        return'seattle'
    
    def get_subdomains(self):
        return ['','seattle']
    
    def get_neighborhoods(self):
        return (
                ('Ballard', 47.683997, -122.381086),
                ('Beacon Hill', 47.588626,-122.309246),
                ('Belltown', 47.624562, -122.345552),
                ('Capitol Hill', 47.632429, -122.312078),
                ('Central District', 47.607668, -122.306328),
                ('Downtown', 47.618777, -122.33139),
                ('Fremont', 47.665792, -122.351303),
                ('Georgetown', 47.559847, -122.324181),
                ('Green Lake', 47.698325, -122.324696),
                ('Greenwood', 47.70491, -122.35199),
                ('International District', 47.606742, -122.319803),
                ('Lake City', 47.725411, -122.278776),
                ('Leschi', 47.608362, -122.288647),
                ('Madison Park', 47.642781, -122.284098),
                ('Madrona', 47.616058, -122.289419),
                ('Magnolia', 47.656658, -122.393961),
                ('Maple Leaf', 47.705603, -122.314825),
                ('Northgate', 47.720214, -122.315083),
                ('Phinney Ridge', 47.670868, -122.351618),
                ('Queen Anne', 47.635321, -122.365036),
                ('Rainier Valley', 47.567261, -122.27972),
                ('Ravenna', 47.683823, -122.296371),
                ('Sand Point', 47.678692, -122.257048),
                ('Lake Union', None, None),
                ('South Park', 47.534472, -122.310705),
                ('University District', 47.657698, -122.306368),
                ('Wallingford', 47.655526, -122.326796),
                ('Wedgwood', 47.686669, -122.294891),
                ('West Seattle', 47.576526, -122.391901),
                ('Delridge', None, None),
                ('Rainier Beach', None, None),
                ('Shoreline', None, None),
                ('Edmonds', None, None),
                ('Lynnwood', None, None),
                ('Bothell', None, None),
                ('Kirkland', None, None),
                ('Redmond', None, None),
                ('Bellevue', None, None),
                ('Mercer Island', None, None),
                ('Tukwila', None, None),
                ('Burien', None, None),
                ('White Center', None, None),
                ('Bainbridge Island', None, None)
                )

############################ 
class LosAngeles(ApplicationDef):
    
    def get_name(self):
        return 'los-angeles'
    
    def get_subdomains(self):
        return ['la', 'los-angeles']
    
    def get_neighborhoods(self):
        return (
                ('Sierra Madre', None, None),
                ('Arcadia', None, None),
                ('Altadena', None, None),
                ('Pasadena', None, None),
                ('La Canada Flintridge', None, None),
                ('Tujunga', None, None),
                ('Sunland', None, None),
                ('Downtown Los Angeles', None, None),
                ('Eastside', None, None),
                ('San Gabriel Valley', None, None),
                ('Pomona Valley', None, None),
                ('Westside', None, None),
                ('Beach Cities', None, None),
                ('South Bay', None, None),
                ('Palos Verdes Peninsula', None, None),
                ('South Los Angeles', None, None),
                ('Gateway Cities', None, None),
                ('San Fernando Valley', None, None),
                ('Antelope Valley', None, None),
                ('Santa Clarita Valley', None, None),
                ('Mid-Wilshire', None, None))

############################  
class PierceCounty(ApplicationDef):
   
    def get_name(self):
        return 'pierce-county'
    
    def get_subdomains(self):
        return ['pierce-county', 'tacoma']
    
    def get_neighborhoods(self):
        return (
                ('Auburn', None, None),
                ('Bonney Lake', None, None),
                ('Buckley', None, None),
                ('DuPont', None, None),
                ('Eatonville', None, None),  
                ('Edgewood', None, None),  
                ('Fife', None, None),
                ('Fircrest', None, None),  
                ('Gig Harbor', None, None),  
                ('Graham', None, None),
                ('Lakewood', None, None),  
                ('Milton', None, None),
                ('North Tacoma', None, None),
                ('Orting', None, None),
                ('Puyallup', None, None),
                ('Spanaway/Parkland', None, None),
                ('Steilacoom',  None, None),
                ('Sumner',  None, None),
                ('Tacoma', None, None),
                ('Tillicum', None, None),
                ('University Place',None, None))