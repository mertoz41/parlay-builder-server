# NBA Parlay Builder Server

Backend of the NBA parlay builder app that returns searched player's season stats, last 5 games, and last 5 games against next opponent to help users build their parlays.
Django app scrapes basketball-reference.com and statmuse.com using Beautiful Soup and returns necessary data in dataframes with Pandas. 
## Installation
Install requirements and run server locally.
```bash 
pip install -r requirements.txt 

python manage.py runserver
```

## Contributing

Pull requests are welcome.
