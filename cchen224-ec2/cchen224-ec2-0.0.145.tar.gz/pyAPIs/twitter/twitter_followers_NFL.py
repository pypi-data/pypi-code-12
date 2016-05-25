from twitter_accounts import accounts
from twitter_followers import get_followers_ids

NFL0 = ['BuffaloBills', 'MiamiDolphins', 'RealPatriots', 'NYJets',
        '1WinningDrive', 'Bengals', 'OfficialBrowns', 'Steelers',
        'HoustonTexans', 'NFLColts', 'JaguarsInsider']
NFL1 = ['TennesseeTitans',
        'Denver_Broncos', 'KCChiefs', 'Raiders', 'Chargers',
        'DallasCowboys', 'Giants', 'Eagles', 'Redskins']
NFL2 = ['ChicagoBearscom', 'DetroitLionsNFL', 'Packers', 'VikingsFootball',
        'Atlanta_Falcons', 'Panthers', 'Official_Saints', 'TBBuccaneers',
        'AZCardinals', 'STLouisRams', '49ers', 'Seahawks']

for team in NFL1:
        get_followers_ids(team, accounts[2])


