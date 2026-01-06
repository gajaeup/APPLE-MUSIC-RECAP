import pandas as pd
from datetime import datetime
from collections import defaultdict

# 설정 및 데이터 로드
required_cols = [
    'Song Name', 
    'Event Received Timestamp', 
    'Auto Play', 
    'Repeat Play', 
    'Container Type',
    'Album Name'
]

song = pd.read_csv("", encoding='utf-8') #애플 뮤직 CSV 파일
song = song[required_cols]

song = song.dropna(how='all', axis=1)
song = song[song['Container Type'].str.upper() == 'PLAYLIST']

song['Event Received Timestamp'] = pd.to_datetime(song['Event Received Timestamp'], format='mixed').dt.tz_localize(None)
past_songs = set(song[song['Event Received Timestamp'].dt.year < 2025]['Song Name'])

# 2025년에 들은 노래들
current_songs = set(song[song['Event Received Timestamp'].dt.year == 2025]['Song Name'])
real_new_songs = current_songs - past_songs
new_song_cnt = len(real_new_songs)

# 2025년 데이터만 필터링
song = song[song['Event Received Timestamp'].dt.year == 2025]


song_counts = song['Song Name'].value_counts()
song['Play Count'] = song['Song Name'].map(song_counts)

mean_manual = song[song['Auto Play'] == 'AUTO_OFF']['Play Count'].mean()
mean_auto = song[song['Auto Play'] != 'AUTO_OFF']['Play Count'].mean()

if mean_auto > 0:
    calculated_selection_weight = mean_manual / mean_auto
else:
    calculated_selection_weight = 1.5 


# 점수 계산 로직
song_dates = defaultdict(lambda: {'dates': [], 'score': 0.0})
top_songs_list = song['Song Name'].value_counts().nlargest(15).index 
desired_date = datetime(2025, 12, 17) 

for i, row in song.iterrows():
    song_name = row['Song Name']


    diff_days = (desired_date - row['Event Received Timestamp']).days
    days_passed = max(0, diff_days)
    
    # 시간 점수 계산
    time_score = 1.0 * (0.98 ** days_passed) 
    score = time_score
    
    # 가중치 적용
    if row['Auto Play'] == 'AUTO_OFF':
        score *= calculated_selection_weight
        
    if row['Repeat Play'] == 'REPEAT_ONE':
        score *= 1.6
        
    if song_name in top_songs_list:
        score *= 1.8
        
    # 데이터 저장
    song_dates[song_name]['dates'].append(row['Event Received Timestamp'])
    song_dates[song_name]['score'] += score 


top_songs = sorted(song_dates.items(), key=lambda x: x[1]['score'], reverse=True)[:15]

print(f"\n======== 2025 recap ========")
print(f"새로 발견한 노래: {new_song_cnt}곡") 
print(f"===========================\n")

print(f"\n--- {desired_date.year}년 나만의 음악 랭킹 Top 15 ---\n")
for rank, (song_name, data_info) in enumerate(top_songs, start=1):
    print(f"Ranking: {rank}")
    print(f"Song: {song_name}")
    print(f"Total Score: {data_info['score']:.2f}") 
    print(f"Play Count: {len(data_info['dates'])}")
    print("-" * 30)
