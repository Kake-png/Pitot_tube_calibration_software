import tkinter as tk  #gui
from tkinter import filedialog   #ファイルを読み込んでくる関数、コード簡素化のために別でimport
import pandas as pd   #数値処理ライブラリ
import chardet  #文字コード確認用
import numpy as np
import matplotlib.pyplot as plt

glaph = None
wind_select = None
wind = None

filenames = []
absolute_pathes = []
windspeeds = []
file_winddict = {}

#windのボタン関数------------------
def go_ahead():
    global file_winddict
    global windspeeds
    print("this is go_ahead.")
    for key, value in file_winddict.items():
        file_winddict[key] = float(value.get())
        pass
    windspeeds = []
    for value in file_winddict.values():
        windspeeds.append(value)
    wind.destroy()
    return

#2個目のwindows(wind)-------------
def windspeed_selector():
    global filenames
    global absolute_pathes
    global file_winddict
    global wind
    file_winddict = {}
    wind = tk.Toplevel(graph)
    wind.title("風速設定")
    wind.geometry("500x500")

    for i in range(len(filenames)):
        newtext = tk.Label(wind, text=filenames[i])
        newtext.grid(row = i, column = 0)
        newlabel = tk.Entry(wind)
        newlabel.grid(row=i,column = 1)
        file_winddict[absolute_pathes[i]] = newlabel
        pass

    aheadbtn = tk.Button(wind,text="設定", command=lambda:go_ahead())
    aheadbtn.grid(row=0,column=2)
    wind.wait_window()
    return

#ファイル名表示変更関数--------------------
def filenamedisplay_changer(filenames_display):
    global filenames
    global windspeeds
    global graph
    newtext = ""
    for x in filenames:
        newtext = newtext + x + "\n"
    filenames_display["text"] = newtext

#計算関数--------------
def plot_with_least_squares(x, y, xlabel, ylabel, title):
    # 最小二乗法による回帰直線の係数を計算
    coefficients = np.polyfit(x, y, 1)  # 1次関数でフィッティング
    slope, intercept = coefficients

    # 回帰直線の式
    regression_line = slope * x + intercept
    # 散布図のプロット
    plt.scatter(x, y, label="data", color="blue")
    # 最小二乗法の直線をプロット
    plt.plot(x, regression_line, label=f"y = {slope:.6f}x + {intercept:.6f}", color="red")
    # グラフの装飾
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid()
    # 最小二乗法の式を出力
    #print(f"{title}: y = {slope:.6f}x + {intercept:.6f}")

    return

# ボタンの関数--------------------
def allfile(): # 後回し
    print("This is allfile")
    pass
def onefile(filenames_display):
    global absolute_pathes
    print("This is onefile")
    file_path = filedialog.askopenfilename(filetypes=[("all files", "*.csv")])
    for file in absolute_pathes:
        if file == file_path:
            tk.messagebox.showinfo('メッセージ', "すでに選択されています")
            return
    absolute_pathes.append(file_path)
    file = file_path.split("/")
    filenames.append(file[-1])
    filenamedisplay_changer(filenames_display)
    pass
def de_selector(filenames_display):
    global filenames
    global absolute_pathes
    filenames = []
    absolute_pathes = []
    filenamedisplay_changer(filenames_display)

def start_calc():
    print("This is start_calc")
    windspeed_selector()
    # 新しいウィンドウを生成して対気速度を設定
    print("wind was selected.")

    datas = []
    for i in range(len(absolute_pathes)):
        x = absolute_pathes[i]
        myfile = rf"{x}"
        with open(myfile, 'rb') as f:  #文字コードを確認するために一行だけ取り出す
            c = f.read()
            result = chardet.detect(c) #文字コード判定
        with open(myfile, encoding=result["encoding"])as file:
            contents = file.readlines()
            newcontents = []
            for line in contents:
                newcontents.append(line.replace(" ","").replace("\n","").replace("¥n","").replace(":",","))
            contents = newcontents
        header = contents.pop(0).split(",")
        value = []
        for line in contents: #移植したままだからこの形だけど実際現状@以外は必要なし
            if line == "\n" or line == "error": # 空白、捨てる値
                pass
            elif line != "" and (line[0] == "%" or line[0] == "@"): #とばし文字
                pass
            else:
                value.append(line.split(","))
        df = pd.DataFrame(value,columns=header)

        #はずれ値除去
        for name in ["差圧(Pa)", "ピトー管係数"]:
            df[name] = pd.to_numeric(df[name], errors='coerce')
            col = df[name].copy()
            # 四分位数
            q1 = col.describe()['25%']
            q3 = col.describe()['75%']
            iqr = q3 - q1 #四分位範囲
            # 外れ値の基準点
            outlier_min = q1 - (iqr) * 1.5
            outlier_max = q3 + (iqr) * 1.5
            # 範囲から外れている値を除く
            col.loc[col < outlier_min] = None
            col.loc[col > outlier_max] = None
            df[name] = col
            absolute_pathes[i] = df

        presure_gap = round(df["差圧(Pa)"].mean(),6)
        pitoi_num = round(df["ピトー管係数"].mean(),6)
        datas.append([presure_gap, pitoi_num, windspeeds[i]]) #差圧の平均, ピトー管係数の平均, 指定された風速
    #print(datas)

    calc_df = pd.DataFrame(datas,columns=["差圧_平均","ピトー管係数平均","風速"])
    #calc_df.plot.scatter(x="差圧_平均",y="ピトー管係数平均")
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plot_with_least_squares(calc_df["差圧_平均"], calc_df["ピトー管係数平均"], "press_ave", "pitot_ave", "press_ave vs pitot_ave")

    plt.subplot(1, 2, 2)
    plot_with_least_squares(calc_df["風速"], calc_df["ピトー管係数平均"], "wind_speed", "pitot_ave", "wind_speed vs pitot_ave")

    plt.tight_layout()
    wind.destroy()
    graph.destroy()
    plt.show()

#一個づつ選択
#フォルダごと選択

# ---------------------
def Linear_approximation():
    global graph
    global filenames
    #新規window生成
    graph = tk.Tk()
    graph.title("係数比較")
    graph.geometry("500x200")

    filename_Label = tk.Label(graph, text = "インポートファイル名")
    filename_Label.grid(row = 0,column = 2)

    filename_Label = tk.Label(graph, text = "(絶対パスの表示は省略)")
    filename_Label.grid(row = 1,column = 2)

    filenames = []

    filenames_display = tk.Label(graph, text = "ファイル未選択")
    filenames_display.grid(row = 2, column = 2)

    select_allfile = tk.Button(graph,text = "フォルダ選択", command= lambda:allfile())
    select_allfile.grid(row = 0, column = 0)

    select_onefile = tk.Button(graph,text = "ファイル選択", command= lambda:onefile(filenames_display))
    select_onefile.grid(row = 1, column = 0)

    deSelect = tk.Button(graph,text = "選択解除", command= lambda:de_selector(filenames_display))
    deSelect.grid(row = 0, column = 1)

    do = tk.Button(graph,text = "実行", command= lambda:start_calc())
    do.grid(row = 0, column = 4)

    #ファイル複数選択
    #ピトー管の列だけ抽出してデータフレームにする
    #それぞれの列の平均を出す
    #プロット、線形近似
    graph.mainloop()

Linear_approximation()

"""
HoPE 25G K.K
"""