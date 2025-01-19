# -*-coding: utf-8 -*-
import os,sys,time,platform
def CleanMSG():
    if "Windows" in platform.platform():
            _ = os.system("cls")
    else:
        _ = os.system("clear")
CleanMSG()
os.system("go run zul.go zul")
