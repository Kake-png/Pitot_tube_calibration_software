# ライブラリのインポート
import tkinter as tk
from tkinter import filedialog
import os
import pandas as pd
import chardet
from decimal import Decimal

df = None

#ボタンのコマンド達
def file_select(filepathbox):
    file_path = filedialog.askopenfilename(filetypes=[("all files", "*.txt")])
    filepathbox.delete(0, tk.END)
    filepathbox.insert(tk.END, file_path)

def read_txt(filepathbox,time_orig,time_new, range_start, range_finish,time_max,time_min):
    time_orig.delete( 0, tk.END )
    time_orig.insert(0,"Nan")
    time_new.delete( 0, tk.END )
    time_new.insert(0,"")
    
    file_path = filepathbox.get()
    editing = file_path.split("/")
    filename = editing[-1]
    directiry_path = file_path.replace(filename,"")
    print(directiry_path)
    os.chdir(directiry_path)

    with open(filename, 'rb') as f:
        c = f.read()
        result = chardet.detect(c)
        #print(result)

    with open(filename, encoding=result["encoding"]) as file:
        contents = file.readlines()
        line_num = 0
        deletelen = []
        for line in contents:
            line.replace(" ","").replace("\n","").replace("¥n","").replace(":",",")
            if len(line) == 0:
                deletelen.insert(line_num)
            line_num += 1
        for line in deletelen:
            del contents[line]

    with open("temporary.csv",mode="w")as file:
        for line in contents:
            if line == "\n":
                pass
            else:
                file.write(line)

    #これ以降pandasに入れてデータ表にして処理
    global df
    df = pd.read_csv("temporary.csv")
    os.remove("temporary.csv")

    #print(df.columns.values)
    for column in df.columns.values:   #すでにtimeの項目があった場合Entryに代入
        if column == "time":
            time_range = float(df.at[1,"time"]) - float(df.at[0,"time"])
            #print(time_range)
            time_orig.delete( 0, tk.END )
            time_orig.insert(0,time_range)

            time_start = float(df.at[0,"time"])
            time_end   = float(df.at[len(df.index)-1,"time"])
            #print(f"{time_start} , {time_end}")
            range_start.delete( 0, tk.END )
            range_start.insert(0,time_start)
            range_finish.delete( 0, tk.END )
            range_finish.insert(0,time_end)
            time_min = tk.Label(root,text=f"min:{time_start}")
            time_min.grid(row=4,column=1)
            time_max = tk.Label(root,text=f"max:{time_end}")
            time_max.grid(row=4,column=3)


def time_refresh(time_orig,time_new,range_start,range_finish,time_max,time_min):  #時間の更新ボタンが押されたとき  Nanと数字以外だった場合のtry_except書かないと
    global df
    if time_orig.get() != "Nan" and time_new.get() != "Nan":  #すでにtimeが指定存在した場合
        tk.messagebox.showinfo('メッセージ', "処理中です1")
        #df.drop('time', axis=1)
        del df["time"]
        newtime_list = []
        insert_time = 0
        for i in range(0,len(df.index)):
            newtime_list.append(insert_time)
            insert_time += Decimal(time_new.get())#そのままfloatとかを足すと桁溢れする
        newtimedf = pd.DataFrame(data=newtime_list, columns=["time"])
        df = pd.concat([newtimedf,df], axis=1)
        print(df.columns.values)
        time_orig.delete( 0, tk.END )
        time_orig.insert(0,time_new.get())
        time_new.delete( 0, tk.END )
        time_new.insert(0,"Nan")

        time_start = float(df.at[0,"time"])
        time_end   = float(df.at[len(df.index)-1,"time"])
        #print(f"{time_start} , {time_end}")
        range_start.delete( 0, tk.END )
        range_start.insert(0,time_start)
        range_finish.delete( 0, tk.END )
        range_finish.insert(0,time_end)
        time_min = tk.Label(root,text=f"min:{time_start}")
        time_min.grid(row=4,column=1)
        time_max = tk.Label(root,text=f"max:{time_end}")
        time_max.grid(row=4,column=3)
        tk.messagebox.showinfo('メッセージ', "値を更新しました1")

    elif time_orig.get() == "Nan" and time_new.get() != "Nan":  #timeが存在しなかった場合
        tk.messagebox.showinfo('メッセージ', "処理中です2")
        newtime_list = []
        insert_time = 0
        #print(len(df.index))
        for i in range(0,len(df.index)):
            newtime_list.append(insert_time)
            insert_time += Decimal(time_new.get())#そのままfloatとかを足すと桁溢れする
        newtimedf = pd.DataFrame(data=newtime_list, columns=["time"])
        df = pd.concat([newtimedf,df],axis=1)
        print(df.columns.values)
        time_orig.delete( 0, tk.END )
        time_orig.insert(0,time_new.get())
        time_new.delete( 0, tk.END )
        time_new.insert(0,"Nan")
        time_start = float(df.at[0,"time"])
        time_end   = float(df.at[len(df.index)-1,"time"])
        #print(f"{time_start} , {time_end}")
        range_start.delete( 0, tk.END )
        range_start.insert(0,time_start)
        range_finish.delete( 0, tk.END )
        range_finish.insert(0,time_end)
        time_min = tk.Label(root,text=f"min:{time_start}")
        time_min.grid(row=4,column=1)
        time_max = tk.Label(root,text=f"max:{time_end}")
        time_max.grid(row=4,column=3)
        tk.messagebox.showinfo('メッセージ', "値を更新しました2")

    else:
        tk.messagebox.showinfo('メッセージ', "正しい値を入力してください")

    print(df["time"])
    df.to_csv("new.csv")

def start_calc(range_start,range_finish,average_index,str_index,var_index):
    for column in df.columns.values:   #すでにtimeの項目があった場合Entryに代入
        if column == "time":
             #start = df.index[df['time'] == float(range_start.get())].tolist()[0]
            start = df.index[(df["time"]-Decimal(range_start.get())).abs().argsort()][0].tolist()
            #finish = df.index[df['time'] == float(range_finish.get())].tolist()[0]
            finish = df.index[(df["time"]-Decimal(range_finish.get())).abs().argsort()][0].tolist()
            df_for_calc = df[start:finish]
            #print(df_for_calc.columns.values)
            #valueindex = tk.Label(root,df_for_calc.columns.values)
            
            mean = df_for_calc["ピトー管係数"].mean()
            #print(f"平均 : {mean}")
            str_ = df_for_calc["ピトー管係数"].std(ddof=0)
            #print(f"標準偏差 : {std}")
            var = df_for_calc["ピトー管係数"].var()
            #print(f"分散 : {var}")
            average_index = tk.Label(root, text=f"平均:{mean}")
            average_index.grid(row=5,column=1)

            str_index = tk.Label(root, text=f"標準偏差:{str_}")
            str_index.grid(row=6,column=1)

            var_index = tk.Label(root, text=f"分散:{var}")
            var_index.grid(row=7,column=1)
            return None
    tk.messagebox.showinfo('メッセージ', "データにtimeを設定してください")



# tkオブジェクトの作成
root = tk.Tk()
root.title("ピトー管校正")
root.geometry("800x200")

# ウィジェットの配置
filepathbox = tk.Entry(root, text="絶対パスを入力するかボタンから選択")
filepathbox.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E)

filesetbutton = tk.Button(root, text="ファイル選択", command=lambda:file_select(filepathbox))
filesetbutton.grid(row=0, column=2)

import_btn = tk.Button(root, text="読み込み", command = lambda:read_txt(filepathbox,time_orig,time_new,range_start,range_finish,time_max,time_min))
import_btn.grid(row=1,column=0)

timeindex = tk.Label(root, text="測定間隔 : ")
timeindex.grid(row=2,column=0)

time_orig = tk.Entry(root)
time_orig.grid(row=2,column=1)

timeshift = tk.Label(root, text=" -> ")
timeshift.grid(row=2,column=2)

time_new = tk.Entry(root)
time_new.grid(row=2,column=3)

time_override = tk.Button(root, text="更新", command = lambda:time_refresh(time_orig,time_new,range_start,range_finish,time_max,time_min))
time_override.grid(row=2,column=4)

rangeindex = tk.Label(root, text="範囲 : ")
rangeindex.grid(row=3,column=0)

range_start = tk.Entry(root)
range_start.grid(row=3,column=1)

rangeshift = tk.Label(root, text=" ~ ")
rangeshift.grid(row=3,column=2)

range_finish = tk.Entry(root)
range_finish.grid(row=3,column=3)

start = tk.Button(root, text="演算、書き出し", command = lambda:start_calc(range_start,range_finish,average_index,str_index,var_index))
start.grid(row=3,column=4)

time_min = tk.Label(root, text=" ~ ")
time_min.grid(row=4,column=1)

time_max = tk.Label(root, text=" ~ ")
time_max.grid(row=4,column=3)

valueindex = tk.Label(root, text="値")
valueindex.grid(row=5,column=0)

average_index = tk.Label(root, text="平均:")
average_index.grid(row=5,column=1)

str_index = tk.Label(root, text="標準偏差:")
str_index.grid(row=6,column=1)

var_index = tk.Label(root, text="分散:")
var_index.grid(row=7,column=1)

# メインループの実行
root.mainloop()
