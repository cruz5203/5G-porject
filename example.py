import pandas as pd
import numpy as np
import math
import cv2
import folium
class Function :
    
    #將時間分割並判斷
    def Judgment_time(i,start_time = None,end_time = None) :  
        if start_time == None or end_time == None :
            return True
        hour , minute , second  = i // 10000 , math.floor(i / 10000 % 1*100) ,i % 100
        if start_time <= hour and end_time >= hour:
            return True
        else :
            return False
        
    #判斷要運算的地圖範圍 (最東)(最北)(最西)(最南)
    def Find_the_boundary(df):
        max_lon = 0
        max_lat = 0
        min_lon = float("inf")
        min_lat = float("inf")

        for lon, lat in zip(df["GPS經度"], df["GPS緯度"]):
            if max_lon < lon:
                max_lon = lon
            if max_lat < lat:
                max_lat = lat
            if min_lon > lon:
                min_lon = lon
            if min_lat > lat:
                min_lat = lat
        boundary = [max_lon , max_lat , min_lon ,min_lat]
        return  boundary

    #將經緯度轉換成建立矩陣大小的整數並建立矩陣每個矩陣為地圖上100m*100m的範圍空間
    def Create_map_matrix(boundary) :
        boundarys = list(boundary)
        boundarys[0] = math.ceil(boundarys[0] * 1000) / 1000 
        boundarys[1] = math.ceil(boundarys[1] * 1000) / 1000 
        boundarys[2] = math.floor(boundarys[2] * 1000) / 1000 
        boundarys[3] = math.floor(boundarys[3] * 1000) / 1000 
        Long  = math.floor((boundarys[1] - boundarys[3])*1000)
        wight = math.floor((boundarys[0] - boundarys[2])*1000)
        matrix = np.zeros((wight+1, Long+1), dtype=int)
        return matrix
    
    #將符合時間範圍內的資料填入建立好的矩陣(位於矩陣範圍內的點每有一點矩陣內的值即1)
    def punctuation(df,matrix,boundary,start_time = None,end_time = None):
        boundarys = list(boundary)
        min_wight =math.floor(boundarys[2] * 1000) / 1000
        min_long =math.floor(boundarys[3] * 1000) / 1000
    
        for lon, lat , time in zip(df['GPS經度'], df['GPS緯度'],df['發生時間']): 
            if Function.Judgment_time(time,start_time,end_time ) :
                long = round(lon - min_wight,3)*1000
                wight = round(lat - min_long,3)*1000
                matrix[int(long)][int(wight)] += 1
                
    #矩陣可視化            
    def create_spectrogram(hazard_distribution_array,Size):
        size = np.shape(hazard_distribution_array)
        img = np.zeros((size[0], size[1], 3), np.uint8)
        color = [
            [255,255,255],
            [176, 211, 93],
            [190, 215, 72],
            [209, 223, 66],
            [242, 235, 56],
            [254, 242, 2],
            [255, 217, 0],
            [252, 177, 24],
            [250, 157, 28],
            [247, 139, 31],
            [243, 121, 31],
            [243, 112, 43],
            [243, 101, 48],
            [242, 90, 49],
            [240, 65, 48],
            [238, 26, 47],
            [197, 37, 65],
            [187, 3, 75],
            [198, 49, 107],
            [179, 44, 120],
            [165, 63, 151],
            [122, 60, 145],
        ]
        for x in range(size[0]):
            for y in range(size[1]):
                if hazard_distribution_array[x][y]/Size<20:
                    n = hazard_distribution_array[x][y]//Size
                else:
                    n = 20
                img[x][y][0] = color[n][2]
                img[x][y][1] = color[n][1]
                img[x][y][2] = color[n][0]
        #img=cv2.resize(img,(size[1]*2, size[0]*2))
        #cv2.imshow("2",cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE))
        print(img.shape)
        cv2.imshow("spectrogram", img)
        #cv2.imshow("2", img[0:535,511:1022])
        cv2.waitKey(0)  
            
    #建立時間範圍內的地圖矩陣
    def Create_a_map_matrix_within_a_time_range(df,boundary,start_time=None,end_time=None) :
        matrix = Feature_value_judgment.Create_map_matrix(boundary)
        Feature_value_judgment.punctuation(df,matrix,boundary,start_time,end_time)
        print(matrix)
        Feature_value_judgment.create_spectrogram(matrix,1)
        return matrix
    
#特徵值判斷演算法
class Feature_value_judgment(Function):
    
    #建立陣列
    def __init__(self,file,start_time = None,end_time = None):  
        #搜尋文件     
        df = pd.read_csv(file, encoding="utf-8") 
        #地圖的(最東)(最北)(最西)(最南)
        self.boundary = Function.Find_the_boundary(df)
        #print(boundary)
        self.matrix = Function.Create_a_map_matrix_within_a_time_range(df,self.boundary,start_time,end_time)
        
    #計算特徵值    
    def feature_matrix_point(matrix,x,y):
        num=0
        size=np.shape(matrix)
        if(x-10<0):
            x_1=0
        else:
            x_1=x-10
        if(x+10>size[0]):
            x_2=size[0]
        else:
            x_2=x+10
        if(y-10<0):
            y_1=0
        else:
            y_1=y-10
        if(y+10>size[1]):
            y_2=size[1]
        else:
            y_2=y+10

        for i in range(x_1,x_2):
            for j in range(y_1,y_2):
                num+=matrix[i][j]
        return num
    
    #將特徵值注入矩陣    
    def creat_featrue_matrix(matrix,feature_matrix):
        size=np.shape(matrix)
        for x in range(size[0]):
            for y in range(size[1]):
                feature_matrix[x][y]=Feature_value_judgment.feature_matrix_point(matrix,x,y)    
        
    #搜尋特徵值矩陣最大的點
    def search_max_point(matrix):
        max=[0,0,0]
        size=np.shape(matrix)
        for x in range(size[0]):
            for y in range(size[1]):
                if(matrix[x][y]>max[2]):
                    max[0]=x
                    max[1]=y
                    max[2]=matrix[x][y]
        return max
    
    #特徵值過濾函式
    def matrix_area_zero(matrix,x,y):
        size=np.shape(matrix)
        if(x-10<0):
            x_1=0
        else:
            x_1=x-10
        if(x+10>size[0]):
            x_2=size[0]
        else:
            x_2=x+10
        if(y-10<0):
            y_1=0
        else:
            y_1=y-10
        if(y+10>size[1]):
            y_2=size[1]
        else:
            y_2=y+10

        for i in range(x_1,x_2):
            for j in range(y_1,y_2):
                matrix[i][j]=0
        
    def featrue_matrix_area_refresh(matrix,featrue_matrix,x,y):
        size=np.shape(matrix)
        if(x-20<0):
            x_1=0
        else:
            x_1=x-20
        if(x+20>size[0]):
            x_2=size[0]
        else:
            x_2=x+20
        if(y-20<0):
            y_1=0
        else:
            y_1=y-20
        if(y+20>size[1]):
            y_2=size[1]
        else:
            y_2=y+20

        for i in range(x_1,x_2):
            for j in range(y_1,y_2):
                featrue_matrix[i][j]=Feature_value_judgment.feature_matrix_point(matrix,i,j)
            
    #部屬點計算
    def Point(matrix,feature_matrix):
        quantity=input("請輸入無人機數量:")
        drone_location=[]
        for i in range(int(quantity)):
            max_point = Feature_value_judgment.search_max_point(feature_matrix)  
            if max_point[2] < 60 :
                break
            drone_location.append(max_point)
            Feature_value_judgment.matrix_area_zero(matrix,drone_location[i][0],drone_location[i][1])
            Feature_value_judgment.featrue_matrix_area_refresh(matrix,feature_matrix,drone_location[i][0],drone_location[i][1])
            Function.create_spectrogram(feature_matrix,10)
        return drone_location
    
    #找尋部屬點
    def Deployment_point(self):
        #特徵值矩陣
        feature_matrix=Function.Create_map_matrix(self.boundary)
        Feature_value_judgment.creat_featrue_matrix(self.matrix,feature_matrix)
        Function.create_spectrogram(feature_matrix,10)
        print(Feature_value_judgment.Point(self.matrix,feature_matrix))
    
def main():
    test = Feature_value_judgment((
        r"C:\Users\MicLab_LAPTOP\Downloads\20a0110c-525e-4138-ae1a-d352c09beca5.csv"
    ),0,23)
    test.Deployment_point()
    
if __name__==main():
    main()