import pandas as pd
import icalendar
from datetime import datetime
import pytz


# URL = 'http://kayit.etu.edu.tr/butunleme_gozetmenlikleri.php'
# URL = 'http://kayit.etu.edu.tr/ara_sinav_programi.php'
URL = 'http://kayit.etu.edu.tr/rapor/final_sinav_programi.php'
# URL = 'http://kayit.etu.edu.tr/rapor/final_sinav_programi.php'
gozetmen_name = 'MEHMET UĞUR GÜDELEK'
# gozetmen_name = 'MUHAMMED YILMAZ'
# gozetmen_name = 'ZEYNEP TÜFEKCİ'
# gozetmen_name = 'CANSIN BAYRAK'
# gozetmen_name = 'IŞIKSU EKŞİOĞLU'
# gozetmen_name = 'UĞUR ŞAHİN'

gozetmenlik_df = pd.read_html(URL, header=0, encoding='utf-8')[0]

gozetmenlik_df = gozetmenlik_df.loc[gozetmenlik_df['GOZETMEN'] == gozetmen_name].reset_index(drop=True)

gozetmenlik_df['HSTART'] = gozetmenlik_df['SAAT'].apply(lambda x:x.split('-')[0])
gozetmenlik_df['HEND'] = gozetmenlik_df['SAAT'].apply(lambda x:x.split('-')[1])
gozetmenlik_df['DTSTART'] = gozetmenlik_df.apply(lambda row: row['TARIH'] + '-' + row['HSTART'], axis=1)
gozetmenlik_df['DTEND'] = gozetmenlik_df.apply(lambda row: row['TARIH'] + '-' + row['HEND'], axis=1)

gozetmenlik_df['DTSTART'] = gozetmenlik_df['DTSTART'].apply(lambda x: pd.to_datetime(x, format='%d/%m/%Y-%H:%M'))
gozetmenlik_df['DTEND'] = gozetmenlik_df['DTEND'].apply(lambda x: pd.to_datetime(x, format='%d/%m/%Y-%H:%M'))
gozetmenlik_df['DTSTART'] = gozetmenlik_df.loc[:,'DTSTART'].dt.tz_localize(pytz.timezone('Europe/Istanbul'))
gozetmenlik_df['DTEND'] = gozetmenlik_df.loc[:,'DTEND'].dt.tz_localize(pytz.timezone('Europe/Istanbul'))
gozetmenlik_df = gozetmenlik_df.drop(['TARIH', 'GUN', 'SAAT', 'HSTART', 'HEND'], axis=1)


ical = icalendar.Calendar()

for idx,row in gozetmenlik_df.iterrows():

    event = icalendar.Event()
    event.add('summary', 'Gozetmenlik - {}'.format(row['DERS ADI']))
    event.add('dtstart', row['DTSTART'].to_pydatetime())
    event.add('dtend', row['DTEND'].to_pydatetime())
    event.add('location', row['DERSLIK'])
    ical.add_component(event)


f = open('gozetmenlik.ics', 'wb')
f.write(ical.to_ical())
f.close()
