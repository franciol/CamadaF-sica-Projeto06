
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Fisica da Computacao
# Carareto
# 17/02/2018
# Aplicacao SERVIDOR
# Aveiro & Otofuji
# 13 de setembro de 2018
####################################################

from enlace import *
import time
from PIL import Image,ImageDraw
import io,os


####################################################
# CHECK DE PORTAS:
# python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta
####################################################

#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
serialName = "/dev/cu.usbmodem1421" # Mac    (variacao de)
#serialName = "COM4"                  # Windows(variacao de)

####################################################

def fromByteToInt(bytes):
    result=0

    for b in bytes:
        result=result*256+int(b)

    return result

def sistemaRecebimento(com):
    com.enable()
    

    ouvindoMensagem1 = True
    ouvindoMensagem3 = True
    ouvindoMensagem4 = True
    pacoteAtual = 0
    esperandoPacotes = 0
    InsperTor = 0 
    comecou = False
    erro4 = 0
    arquivo = bytes()

    while ouvindoMensagem1:
        
        print("\n\n\n\n * OUVINDO MENSAGEM 1\n\n\n\n\n\n")
        bytesSeremLidos = com.rx.getBufferLen(False)

        payload, lenPayload, messageType, ack, numeroPacote, totalPacote = com.getData(bytesSeremLidos)
        
        
        if messageType == 1:
            print("\n\n\n\n\n\n * RECEBEU MENSAGEM 1 \n")
            ouvindoMensagem1 = False
            
        
        else:
            continue


        while ouvindoMensagem3:
            
            
            com.sendData(facadeEnlace.encapsulate(None, 2))
            print(" * MANDOU MENSAGEM 2 \n")
            print(" * OUVINDO MENSAGEM 3")
        
            bytesSeremLidos = com.rx.getBufferLen(True)
            if bytesSeremLidos == 0:
                print("ERRO TIPO II: NÃO RECEBEU MENSAGEM 3")
            payload, lenPayload, messageType, ack, numeroPacote, totalPacote = com.getData(bytesSeremLidos)

            if messageType == 3:
                print("\n * RECEBEU MENSAGEM 3 \n")
                ouvindoMensagem3 = False
                print(" * OUVINDO MENSAGEM 4: esperando pacote 1 \n")    
                
            
            else:
                continue



        while ouvindoMensagem4:
            
            #com.sendData(facadeEnlace.encapsulate(None, 3))
            #print("MANDOU MENSAGEM 3")
        
            bytesSeremLidos = com.rx.getBufferLen(False)
            payload, lenPayload, messageType, ack, numeroPacote, totalPacote = com.getData(bytesSeremLidos)

            if numeroPacote == 1:
                pacoteAtual = numeroPacote
                esperandoPacotes = totalPacote
                comecou = True
                InsperTor += 1 


            else:
                if esperandoPacotes == totalPacote:
                    if comecou == True:
                        if InsperTor != numeroPacote:
                        
                            print("-------------------------")
                            print("ERRO TIPO 4: PACOTE INESPERADO")
                            print("ERRO NA TRANSMISSÃO – MANDE DE NOVO")
                            print("ENVIANDO MENSAGEM TIPO 6: NACKNOWLEDGE")
                            print("-------------------------")
                            com.sendData(facadeEnlace.encapsulate(None, 6))
                            ouvindoMensagem4 = False
                            InsperTor = 1
                            pacoteAtual = 0
                            esperandoPacotes = 0
                            comecou = False
                                

                else:
                    ouvindoMensagem4 = False
                    InsperTor = 1
                    pacoteAtual = 0
                    esperandoPacotes = 0
                    comecou = False

                    com.sendData(facadeEnlace.encapsulate(None, 7))
                    print("-------------------------")
                    print("MANDOU MENSAGEM TIPO 7")
                    time.sleep(4)
                    com.disable()
                    print("-------------------------")
                    print("ERRO FATAL DESCONHECIDO – RECOMECE TRANSMISSÃO")
                    print("-------------------------")

                pacoteAtual = numeroPacote

            if ack == True:
                print("Mensagem tipo 5 – acknowledge da transmissão")
                print("-------------------------")
                arquivo += payload
                print("Pacote ", pacoteAtual, " de ", esperandoPacotes, "recebido, contendo payload de ", len(payload), " bytes \n")
                print("--------------------------------------------------")
                InsperTor += 1
                com.sendData(facadeEnlace.encapsulate(None, 5))
                
                
            
            
            else:
                print("-------------------------")
                print("-------------------------")
                print("ERRO NA TRANSMISSÃO – MANDE DE NOVO")
                print("-------------------------")
                print("ENVIANDO MENSAGEM TIPO 6: NACKNOWLEDGE")
                print("-------------------------")
                print("-------------------------")
                com.sendData(facadeEnlace.encapsulate(None, 6))
                
                continue


            time.sleep(5)

            if pacoteAtual == esperandoPacotes:
                comecou == False
                print("-------------------------")
                print("Tamanho total do payload do arquivo recebido: ", len(arquivo))
                print("-------------------------")
                time.sleep(5)
                com.sendData(facadeEnlace.encapsulate(None, 7))
                print(" * MANDOU MENSAGEM TIPO 7")
                time.sleep(5)
                com.disable()
                print("-------------------------")
                print("Comunicacao encerrada")
                print("-------------------------")
                rxBuff = io.BytesIO(arquivo)
                img = Image.open(rxBuff)
                draw = ImageDraw.Draw(img)
                img.show()
                break

            else:
                print("--------------------------------------------------")
                print("\n\nOuvindo pacote", InsperTor)
                

def main():

    com = enlace(serialName)
    sistemaRecebimento(com)
    
if __name__ == "__main__":
    main()