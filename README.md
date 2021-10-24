# CunyZero

## To install dependencies: 

        $ pip install -r requirements.txt

## To check dependencies installed: 

        $ pip freeze
        
To update **requirements.txt**:

        $ pip freeze > requirements.txt 

## To build the most up-to-date Database:

#### Disclaimer: Doing this will wipe the entire older instance of your local database meaning all users, profiles will be lost!
In the event of any error upon the launching the application, try deleting your local sqlite DB instance.  
To create a new database that adheres to all modifications made in "models.py" type:
        
        $ python clean_up.py

## To run the application:

        $ python run.py 
