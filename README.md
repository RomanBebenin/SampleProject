# Project: Scraping Weather Data

In this project the module scraper is for downloading and parsing weather observation data
from the BoM. The module 'scraper.py' contains stations' dictionary (only 4 stations now), 
the function scraper, the function testing scraper function and a set of custom exceptions 
for the scraper function. The scraper function is invoked with three parameters: location_name,
timeout, attempt_num. You may read more in the corresponding function's documentation. 

The *production quality* of the code is ensured by existence of the following:
 - custom exceptions specific to the module,
 - thorough arguments' check,
 - the mechanism for retrying assessing URL for a number of times defined by 
the corresponding functional argument,
 - testing function with boolean return True for Success and False for Fail
 - extensive documentation.

File WeatherProject.ipynb contains some examples of using scraper function.