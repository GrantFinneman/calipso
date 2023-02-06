# File containing the definition of coordinate class so put both lat and longitude in the axis coordinate
# for the tensor

class Coordinate:
    '''
    Class that holds both the latitude and longitude data
    for the tensor axis. It will allow the soring and referencing
    of both lat and lon in one object without needing to
    abuse the attribute fields in xarray
    
    Sorts based on latitude since the latitude and longitude
    are directly correlated, when you bound one you bound the other.
    '''
    
    def __init__(self, latitude, longitude):
        self.lat = latitude
        self.lon = longitude
        self.cantor = self.cantor()
        return
    
    
    def cantor(self):
        a, b = self.lat + 90, (self.lon + 180)/361
        return a + b
    
    def __repr__(self):
        return f'Cordinate pair at ({self.lat}, {self.lon}) cantor = {self.cantor}'
    
    def __eq__(self, other):
        if isinstance(other, Coordinate):
            return self.lat == other.lat and self.lon == other.lon
        
    def __lt__(self, other):
        if isinstance(other, Coordinate):
            return self.cantor < other.cantor
            
    def __le__(self, other):
        if isinstance(other, Coordinate):
            return self < other or self == other