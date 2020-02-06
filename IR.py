from googleapiclient.discovery import build

service = build("customsearch", "v1", developerKey="AIzaSyBKlE390a0krI3_Oe-zk-_Pdf7J0J7Oo1I")
    
res = service.cse().list(q='lectures', cx='000568897140034501999:kyspcqzrszq',).execute()

for i in range(len(res['items'])):
    print('Title: ', res['items'][i]['title'], '\n')
    print('URL: ', res['items'][i]['link'], '\n')
    print('Description: ', res['items'][0]['snippet'], '\n')
    print('\n\n')
