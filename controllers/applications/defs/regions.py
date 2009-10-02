from controllers.applications.defs._application_def import ApplicationDef

############################
class Seattle(ApplicationDef):
    
    def get_name(self):
        return 'seattle'
    
    def get_subdomains(self):
        return ['','seattle']
    
    def get_neighborhoods(self):
        return (
                'Ballard','Beacon Hill','Belltown','Capitol Hill','Central District',
                'Downtown','Fremont','Georgetown','Green Lake',
                'Greenwood','International District', 'Bitter Lake','Lake City',
                'Leschi','Madison Park','Madrona','Magnolia','Maple Leaf',
                'Northgate','Phinney Ridge','Queen Anne','Rainier Valley',
                'Ravenna','Sand Point',
                'Lake Union','South Park','University District','Wallingford',
                'Wedgwood','West Seattle','Delridge','Rainier Beach', 
                'Shoreline', 'Edmonds', 'Lynnwood', 'Bothell', 'Kirkland',
                'Redmond', 'Bellevue', 'Mercer Island', 'Tukwila', 'Burien',
                'White Center', 'Bainbridge Island',)

############################ 
class LosAngeles(ApplicationDef):
    
    def get_name(self):
        return 'los-angeles'
    
    def get_subdomains(self):
        return ['la', 'los-angeles']
    
    def get_neighborhoods(self):
        return ()

############################  
class PierceCounty(ApplicationDef):
   
    def get_name(self):
        return 'pierce-county'
    
    def get_subdomains(self):
        return ['pierce-county', 'tacoma']
    
    def get_neighborhoods(self):
        return ('Auburn',
'Bonney Lake',
'Buckley',
'DuPont',
'Eatonville',  
'Edgewood',  
'Fife',
'Fircrest',  
'Gig Harbor',  
'Graham',
'Lakewood',  
'Milton',
'North Tacoma',
'Orting',
'Puyallup',
'Spanaway/Parkland',
'Steilacoom',  
'Sumner',  
'Tacoma',
'Tillicum',
'University Place',)