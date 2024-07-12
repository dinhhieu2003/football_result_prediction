import csv
import chardet
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from PIL import ImageTk, Image, ImageFilter
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

matches = pd.read_csv("matches_clean.csv", index_col=0)

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        result = chardet.detect(file.read())
    return result['encoding']
csv_encoding = detect_encoding('matches_clean.csv')

def load_teams_from_csv(file_path, encoding=csv_encoding):
    teams = []
    with open(file_path, 'r', encoding=encoding) as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            team_entry = {
                'team': row['team'],
                'team_code': row['team_code'],
            }

            # Kiểm tra xem 'opp_code' có trong dòng dữ liệu không
            if 'opp_code' in row:
                team_entry['opp_code'] = row['opp_code']

            teams.append(team_entry)

    return teams

def load_opponents_from_csv(file_path, encoding=csv_encoding):
    opponents = []
    with open(file_path, 'r', encoding=encoding) as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            opp_entry = {
                'opponent': row.get('opponent', ''),
                'opp_code': row.get('opp_code', ''),
            }
            opponents.append(opp_entry)
    return opponents

def calculate_mean(data, attribute):
    values = [float(entry[attribute]) for entry in data]
    return np.mean(values)

def get_home_name(file_path, team_code, encoding=csv_encoding):
    teams = []
    with open(file_path, 'r', encoding=encoding) as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if team_code == row['team_code']:
                return row['team']
    return ''

def get_data_home_team(file_path, team_code, encoding=csv_encoding):
    teams = []
    with open(file_path, 'r', encoding=encoding) as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            team_entry = {
                'team_code': row['team_code'],
                'xg': row['xg'],
                'xga': row['xga'],
                'poss': row['poss'],
                'sca': row['sca'],
                'gca': row['gca'],
                'cmp%': row['cmp%'],
                'g/sh': row['g/sh']
            }
            if team_entry['team_code'] == team_code:
                teams.append(team_entry)
    mean_xg = calculate_mean(teams, 'xg')
    mean_xga = calculate_mean(teams, 'xga')
    mean_poss = calculate_mean(teams, 'poss')
    mean_sca = calculate_mean(teams, 'sca')
    mean_gca = calculate_mean(teams, 'gca')
    mean_cmp_percent = calculate_mean(teams, 'cmp%')
    mean_g_sh = calculate_mean(teams, 'g/sh')
    return mean_xg, mean_xga, mean_poss, mean_sca, mean_gca, mean_cmp_percent, mean_g_sh

def get_result(team_code, venue_code, opp_code):
    mean_xg, mean_xga, mean_poss, mean_sca, mean_gca, mean_cmp_percent, mean_g_sh = \
        get_data_home_team('matches_clean.csv', team_code, encoding=csv_encoding)
    rf = RandomForestClassifier(n_estimators=50, min_samples_split=10, random_state=1)
    train = matches[matches["date"] < '2022-01-01']
    test = matches[matches["date"] > '2022-01-01']
    predictors = ["team_code","venue_code", "opp_code", "xg", "xga","poss", "sca" ,"gca", "cmp%", "g/sh"]
    rf.fit(train[predictors], train["target"])

    new_data = {
        "team_code": team_code,
        "venue_code": venue_code,
        "opp_code": opp_code,
        "xg": mean_xg,
        "xga": mean_xga,
        "poss": mean_poss,
        "sca": mean_sca,
        "gca": mean_gca,
        "cmp%": mean_cmp_percent,
        "g/sh": mean_g_sh
    }
    new_data_df = pd.DataFrame([new_data])
    preds = rf.predict(new_data_df)
    return preds

teams_data = load_teams_from_csv('matches_clean.csv', encoding=csv_encoding)
opps_data = load_opponents_from_csv('matches_clean.csv', encoding=csv_encoding)
team_code = 0
opp_code = 0

def on_combobox_select(event):
    global team_code
    global opp_code
    selected_team = combo_home.get()
    selected_opp = combo_away.get()
    if selected_team and selected_opp:
        selected_team_code = team_code_mapping.get(selected_team, '')
        team_code = selected_team_code
        selected_opp_code = opp_code_mapping.get(selected_opp, '')
        opp_code = selected_opp_code


window = Tk()
window.title('Dự đoán')
window.geometry('900x600')

# Tạo một Label làm background cho frame
background_label = Label(window)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Tạo một frame để nhóm các nhãn Đội nhà và Đội khách
team_frame = Frame(window, width=700, height=500)
team_frame.pack(anchor='center')
#team_frame.place(relx=0.5, rely=0.2, anchor='center')


name = Label(team_frame, text='DỰ ĐOÁN KẾT QUẢ', foreground='blue', font=("Times New Roman", 30))
name.pack()

home_team = Label(team_frame, text='Đội nhà:', font=("Times New Roman", 13))
home_team.pack(side=LEFT)  # Chỉnh các nhãn về phía trái

unique_team_names = set([team['team'] for team in teams_data])

combo_home = Combobox(team_frame, font=("Times New Roman", 13), values = list(unique_team_names), width=30)
combo_home.pack(side=LEFT, padx=10)

selected_team_code = StringVar()

# Tạo một ánh xạ từ tên đội đến mã đội
team_code_mapping = {team['team']: team['team_code'] for team in teams_data}
# Liên kết hàm on_combobox_select với sự kiện chọn Combobox
combo_home.bind("<<ComboboxSelected>>", on_combobox_select)
print(team_code_mapping)

#######################################

vs_label = Label(team_frame, text='VS', font=("Times New Roman", 25), foreground='red')
vs_label.pack(side=LEFT, padx=10) 

away_team = Label(team_frame, text='Đội khách:', font=("Times New Roman", 13))
away_team.pack(side=LEFT)
unique_opp_names = set([opp['opponent'] for opp in opps_data])

combo_away = Combobox(team_frame, font=("Times New Roman", 13), values = list(unique_opp_names), width=30)
combo_away.pack(side=LEFT, padx=10)  # Căn giữa và thêm khoảng cách

selected_opp_code = StringVar()
opp_code_mapping = {opp['opponent']: opp['opp_code'] for opp in opps_data}

# Liên kết hàm on_combobox_select với sự kiện chọn Combobox
combo_away.bind("<<ComboboxSelected>>", on_combobox_select)
print(type(opp_code_mapping))

######################################
######################################

infor_frame = Frame(window, width=700, height=500)
infor_frame.pack(anchor='center')
#infor_frame.place(relx=0.5, rely=0.5, anchor='center')

result_label = Label(infor_frame, text=f'Kết quả trận đấu', font=("Times New Roman", 13))
result_label.pack()

predict_label = Label(infor_frame, text='Đang chờ', font=("Comic Sans MS", 15))

def predict():
    global predict_label
    predict_label.destroy()
    pred = get_result(team_code, 1, opp_code)
    name = get_home_name('matches_clean.csv', team_code, encoding=csv_encoding)
    result = ''
    if pred == 2:
        result = 'Đội thắng là:'
    elif pred == 1:
        result = 'Đội thua là:'
    else:
        result = 'Hòa'
    
    if result == 'Hòa':
        predict_label = Label(infor_frame, text=f'{result}', font=("Comic Sans MS", 15))
    else:
        predict_label = Label(infor_frame, text=f'{result} {name}', font=("Comic Sans MS", 15))
    predict_label.pack()

predict_button = tk.Button(infor_frame, text="Dự đoán", command=predict, font=("Comic Sans MS", 15),
                                bg="#badc58")
predict_button.pack()


predict_label.pack()

#######################################

#IMPORT HÌNH ẢNH

img_import = (Image.open("assets/back_ground.png"))
resize = img_import.resize((900, 600), Image.LANCZOS)
background_image = ImageTk.PhotoImage(resize)

background_label.configure(image=background_image)
background_label.image = background_image

window.mainloop()
