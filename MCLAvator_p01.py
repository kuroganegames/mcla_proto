# coding:utf-8

import pygame, os, sys, time, pyaudio, configparser
import numpy as np
from pygame.locals import *
from random import random


class MCLA:    
    def __init__(self):
        self.main()
       
    def load_setting_dict(self):
        config_ini = configparser.ConfigParser()
        config_ini.read(self.dir_ini, encoding="utf-8")
        dict_ini = {}
        for ini_section in config_ini.sections():
            dict_ini[ini_section] = dict(config_ini.items(ini_section))
        return dict_ini
        
    def set_rec_device(self):
        chunk = 1024        
        a_FORMAT = pyaudio.paInt16
        CHANNELS = 1

        audio = pyaudio.PyAudio()
        info_device = audio.get_device_info_by_index(self.index_device_mic)
        RATE = int(info_device["defaultSampleRate"])

        # 音の取込開始
        p = pyaudio.PyAudio()
        stream = p.open(format = a_FORMAT,
            channels = CHANNELS,
            rate = RATE,
            input_device_index = self.index_device_mic,
            input = True,
            frames_per_buffer = chunk
        )
        return stream, chunk, CHANNELS, RATE, audio.get_sample_size(a_FORMAT)      
        
    def main(self):
        # 設定の読み込み
        dir_data = os.getcwd()
        self.dir_ini = os.path.join(dir_data,"p_setting.ini")
        dict_ini                = self.load_setting_dict()
        # print(dict_ini)
        self.index_device_mic        = int(dict_ini["volume"]["index_decive"])
        aud_vol_min             = float(dict_ini["volume"]["aud_vol_min"])
        aud_vol_max             = float(dict_ini["volume"]["aud_vol_max"])
        aud_threshold_close     = float(dict_ini["volume"]["aud_threshold_close"])
        aud_threshold_mid       = float(dict_ini["volume"]["aud_threshold_mid"])
        aud_threshold_max       = float(dict_ini["volume"]["aud_threshold_max"])

        aud_vol_width           = aud_vol_max - aud_vol_min
        aud_vol_mouth_close     = aud_vol_min + aud_vol_width * aud_threshold_close
        aud_vol_mouth_open_mid  = aud_vol_min + aud_vol_width * aud_threshold_mid
        aud_vol_mouth_open_max  = aud_vol_min + aud_vol_width * aud_threshold_max
        
        back_color_16           = dict_ini["view"]["back_color"]
        back_color              = (int(back_color_16[1:3],16), int(back_color_16[3:5],16), int(back_color_16[5:],16),)
        # print(back_color)
        view_width              = int(dict_ini["view"]["width"])
        view_height             = int(dict_ini["view"]["height"])
        view_mouth_x            = int(dict_ini["view"]["mouth_x"])
        view_mouth_y            = int(dict_ini["view"]["mouth_y"])
        
        window_name             = dict_ini["view"]["name"]
        # print(window_name)
        # print(len(window_name))
        # print(type(window_name))
        # input()
        
        dir_image               = os.path.join(dir_data, "imgs")


        # pygameの初期設定
        pygame.init()          
        if window_name=="":
            pygame.display.set_caption("MCLiveAvator")    
        else:
            pygame.display.set_caption("MCLiveAvator_{}".format(window_name)) 
        dir_icon = os.path.join(dir_data, "icon.png")
        pygame.display.set_icon(pygame.image.load(dir_icon))

        # 画像ディレクトリの取得
        dir_img_base    = os.path.join(dir_image, "base.png")
        dir_blink       = os.path.join(dir_image, "blink.png")
        
        keis_mouth      = ["mouth_close", "mouth_mid1", "mouth_mid2", "mouth_max"]
        dirs_mouth      = [os.path.join(dir_image, "{}.png".format(key_mouth)) for key_mouth in keis_mouth]
        
        # print(dir_blink)
        if os.path.exists(dir_blink):
            flug_blink      = True
            # print("aaaa")
        else:
            dir_blink       = os.path.join(dir_image, "backup", "blink.png")
            flug_blink      = False
            
            
        # 画像の読み込みとリサイズ
        loaded_img_base        = pygame.image.load(dir_img_base)
        img_width, img_height   = loaded_img_base.get_width(), loaded_img_base.get_height()
        
        if view_width==0 or view_height==0:
            screen = pygame.display.set_mode((img_width, img_height))         
            resize_scale_xy         = ((int(img_width), int(img_height)))
        else:
            screen = pygame.display.set_mode((view_width, view_height)) 
            resize_scale            = max(view_width/img_width , view_height/img_height)
            resize_scale_xy         = ((int(img_width*resize_scale), int(img_height*resize_scale)))

        loaded_img_base        = pygame.transform.scale(pygame.image.load(dir_img_base), resize_scale_xy)
        list_loaded_mouths      = [pygame.transform.scale(pygame.image.load(dir_mouth), resize_scale_xy) for dir_mouth in dirs_mouth]
        img_blink               = pygame.transform.scale(pygame.image.load(dir_blink), resize_scale_xy)

        dict_mouth = {}
        for i, key_mouth in enumerate(keis_mouth):
            dict_mouth[key_mouth] = list_loaded_mouths[i]
        # print(dict_mouth)
        
        
        # 文字描画系
        set_font = pygame.font.SysFont(None, 24)
        show_result    = int(dict_ini["view"]["show_result"])

        # デバイスの設定
        aud_stream, chunk, CHANNELS, RATE, aud_sample_size = self.set_rec_device()
        
        # 認識などの設定。休止無しなら約40fps前後のハズ。
        sec_per_frame = chunk/RATE
        time_loop_sleeped               = float(dict_ini["recognition"]["time_loop_sleeped"])
        time_aud_averaged_frames        = float(dict_ini["recognition"]["time_aud_averaged_frames"])
        
        num_aud_averaged_frames         = time_aud_averaged_frames/sec_per_frame
        blink_probability               = float(dict_ini["blink"]["probability"])

        
        # 初期設定
        aud_average_window = []

        # 描画系ループ
        
        while True: 
            screen.fill(back_color)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()             
                    sys.exit

            # 画像描画。blink or baseを描写
            if random() < blink_probability and flug_blink:
                screen.blit(img_blink, (0,0)) 
                if show_result:
                    screen.blit(set_font.render("blinked", True, (100,100,100)), (0,0))
                    print("blinked")
            else:
                screen.blit(loaded_img_base, (0,0))  

            
            # 音声データ取得
            data = aud_stream.read(chunk)
            x = np.frombuffer(data, dtype="int16") / 32768.0
            aud_volume = x.max()
            aud_average_window.append(aud_volume)
            if len(aud_average_window) > num_aud_averaged_frames:
                del aud_average_window[0]
            aud_volume_averaged = sum(aud_average_window) / len(aud_average_window)

            # 口パク描画。
            if aud_volume_averaged < aud_vol_mouth_close:
                # print(aud_volume,"close")
                mouth_text = "mouth_close"
            elif aud_vol_mouth_close < aud_volume_averaged < aud_vol_mouth_open_mid:
                mouth_text = "mouth_mid1"
            elif aud_vol_mouth_open_mid < aud_volume_averaged < aud_vol_mouth_open_max:
                mouth_text = "mouth_mid2"
            elif aud_vol_mouth_open_max < aud_volume_averaged:
                mouth_text = "mouth_max"
            screen.blit(dict_mouth[mouth_text], (view_mouth_x,view_mouth_y))
            
            # 画面更新
            pygame.display.update()

            # 休止設定
            time.sleep(time_loop_sleeped)
        

if __name__ == "__main__":
    gk = MCLA()