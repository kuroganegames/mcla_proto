# coding:utf-8
import pyaudio

def main():
    audio = pyaudio.PyAudio()

    # 音声デバイス毎のインデックス番号を一覧表示
    print("入力デバイスの一覧を表示します。\n使用したいデバイス番号を「p_setting.ini」の[volume]の「index_decive」に設定してください。\n===========")
    for x in range(0, audio.get_device_count()):
        info_device = audio.get_device_info_by_index(x)
        # print(info_device)
        # print("input")
        if info_device["maxInputChannels"]>0:
            print(info_device["index"], "input", info_device["name"], info_device["maxInputChannels"])
        # print("output")
        # if info_device["maxOutputChannels"]>0:
            # print(info_device["index"], "output", info_device["name"], info_device["maxInputChannels"])
    input("終了するにはなんたらかんたら…")
if __name__ == '__main__':
    main()