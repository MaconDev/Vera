from urllib.request import urlretrieve
import os
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd

# Raw Data: https://data.detroitmi.gov/Public-Safety/DPD-911-Calls-for-Service-September-20-2016-Presen/wgv9-drfc

BASE_NAME = 'Detroit'

DATA_URLS = {
    'all': "https://data.detroitmi.gov/api/views/wgv9-drfc/rows.csv?accessType=DOWNLOAD"
}

DATE_FORMAT = '%m/%d/%Y %H:%M:%S %p'

COLUMN_TRANSFORMS = {
    'Call Time' : 'date_time'
}

COLUMN_TYPES = {

}

COLUMN_RENAMES = {
       
}

def create_dir():
    project_dir = Path(__file__).resolve().parents[2]
    city_dir = project_dir / 'data' / 'raw' / BASE_NAME     
    
    city_dir.mkdir(parents=True, exist_ok=True)
    return city_dir

def file_path(year, output_filepath):
    return output_filepath / 'calls_{}.csv'.format(year)

def download_calls(output_filepath):
    """ Download the call data from the New Orleans open data portal
    """
    logger = logging.getLogger(__name__)
    for year, url in DATA_URLS.items():
        logger.info('Downloading New Orleans calls data for year {} from {} '.format(year,url))
        download_path = file_path(year,output_filepath)
        if(download_path.exists()):
            print("Already downloaded, skipping {}".format(download_path))
        else:
            print('Downloading {} calls data for year {} from {} '.format(BASE_NAME, year,url))

            urlretrieve(url, str(download_path))
    logger.info('Done')
       
def download_geoms(output_filepath):
    """ Download the geometry files for LA
    """
    logger = logging.getLogger(__name__)
    logger.info('No specific geoms for LA just now')
    #urlretrieve(seattle_data_url,output_filepath)
    logger.info('Done')

def download_all():
    """ Download all the files for New Orleans
    """
    project_dir = Path(__file__).resolve().parents[2]
    city_dir = project_dir / 'data' / 'raw' / BASE_NAME     
    
    city_dir.mkdir(parents=True, exist_ok=True)
                                     
    download_calls(city_dir)
    download_geoms(city_dir)
    
def load_and_fix_types(file):
    data = pd.read_csv(file, dtype=COLUMN_TYPES)
    data = data.rename(columns = COLUMN_RENAMES)
    for column, transform in COLUMN_TRANSFORMS.items():
        if(transform =='date_time'):
            if type(DATE_FORMAT) == str or column not in DATE_FORMAT.keys():
                column_date_format = DATE_FORMAT
            else :
                column_date_format = DATE_FORMAT[column]
            data[column] = pd.to_datetime(data[column], format=column_date_format)
    return data

def consolidate_all():
    print('loading data and assigning column types')
    city_dir = create_dir()
    all_data = []
    for year, url in DATA_URLS.items():
        file = file_path(year,city_dir)
        all_data.append( load_and_fix_types(str(file)))
    data = pd.concat(all_data)    
    data.reset_index().to_feather(city_dir / 'calls.feather')
                                    

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    
    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())
    
    # Download all data
    download_all()
    consolidate_all()