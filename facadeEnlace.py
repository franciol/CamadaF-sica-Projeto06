from PIL import Image,ImageDraw
import io,os
from PyCRC.CRC16 import CRC16 as crc16

EOP = b'/00'
stuffingByte = b'/7a/'
crc_combinado = None

#Função para criar CRC
def crc_creator(payload):
    #payload transformado em bits
    payloadBits = bin(int.from_bytes(payload, byteorder="big")).strip('0b')
    #payloadBits = '0000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    crcBitsPayload = crc16().calculate(payloadBits)
    return crcBitsPayload

#Função para verificar o crc
def crc_check(crc, payload):
    isRight = False
    payloadBits = bin(int.from_bytes(payload, byteorder="big")).strip('0b')
    crcBitsPayload = crc16().calculate(payloadBits)
    if crcBitsPayload == crc:
        isRight = True
    return isRight





def int_to_byte(values, length):
    result = []
    for i in range(0,length):
        result.append(values >> (i*8)& 0xff)

    result.reverse()

    return bytes(result)

def fromByteToInt(bytes):
    result=0

    for b in bytes:
        result=result*256+int(b)

    return result


def encapsulate(payload, messageType):
    #Variavel do tamanho do pacote do payload
    pckSize = 106

    if payload != None:
        txLen = len(payload)
    else:
        txLen = len(int_to_byte(0,1))

    '''
        Head = 17 bytes:
            tipo de msg: 1 byte
            pacote atual: 2 bytes
            numero de pacotes: 2 bytes
            payloadLen = 5 bytes
            crc = 2 bytes
            EOP = 3 bytes
            stuffing = 4 bytes


            package = 128
            head = 17
            EOP = 3
            payload = 108
    '''
    payloadfinal = bytes()
    if payload != None:
        for i in range(0, len(payload)):
            if EOP == payload[i:i+13]:
                payloadfinal+=stuffingByte
                payloadfinal+=payload[i:i+1]
            else:
                payloadfinal+=payload[i:i+1]
    else:
        payloadfinal = int_to_byte(0,1)

    payloadLen = int_to_byte(txLen,5)

    if messageType == 1:
        head = int_to_byte(1,1)+int_to_byte(0,2)+int_to_byte(0,2)+payloadLen+int_to_byte(0,2)+EOP+stuffingByte
        #Cliente manda pedido de comunicação para servidor
        all = bytes()
        all += head
        all += payloadfinal
        all += EOP

        return all
    elif messageType == 2:
        head = int_to_byte(2,1)+int_to_byte(0,2)+int_to_byte(0,2)+payloadLen+int_to_byte(0,2)+EOP+stuffingByte
        #Servidor responde cliente dizendo que recebeu mensagem tipo 1
        all = bytes()
        all += head
        all += payloadfinal
        all += EOP

        return all
    elif messageType == 3:
        head = int_to_byte(3,1)+int_to_byte(0,2)+int_to_byte(0,2)+payloadLen+int_to_byte(0,2)+EOP+stuffingByte
        #Cliente responde servidor dizendo que recebeu mensagem tipo 2
        #e servidor sabe que a próxima mensagem é tipo 4
        all = bytes()
        all += head
        all += payloadfinal
        all += EOP

        return all
    elif messageType == 4:
        #Cliente faz efetivamente transmissão para servidor
        sad = 0
        listOfPackages = []
        if (len(payload)%pckSize)==0 :
            packTotal =int(len(payload)/pckSize)
        else:
            packTotal =int(1+(len(payload)//pckSize))
        a = 0
        for i in range(0,packTotal):
            payloadfinal = payload[i*pckSize:(i*pckSize)+pckSize]
            crc = crc_creator(payloadfinal)

            payloadLen = int_to_byte(len(payloadfinal),5)

            head = int_to_byte(4,1)+int_to_byte(i,2)+int_to_byte(packTotal,2)+payloadLen+int_to_byte(crc,2)+EOP+stuffingByte
            all = bytes()
            all += head
            all += payloadfinal
            all += EOP
            listOfPackages.insert(a,all)
            print('\n',all)
            a+=1

        return listOfPackages

    elif messageType == 5:
        head = int_to_byte(5,1)+int_to_byte(0,2)+int_to_byte(0,2)+payloadLen+int_to_byte(0,2)+EOP+stuffingByte
        #acknowledge do servidor para cliente confirmando recebimento
        #correto do payload
        all = bytes()
        all += head
        all += payloadfinal
        all += EOP

        return all
    elif messageType == 6:
        head = int_to_byte(6,1)+int_to_byte(0,2)+int_to_byte(0,2)+payloadLen+int_to_byte(0,2)+EOP+stuffingByte
        #nacknowledge do servidor para cliente pedindo reenvio do pacote por
        #erro de transmissão
        all = bytes()
        all += head
        all += payloadfinal
        all += EOP

        return all
    elif messageType == 7:
        head = int_to_byte(7,1)+int_to_byte(0,2)+int_to_byte(0,2)+payloadLen+int_to_byte(0,2)+EOP+stuffingByte
        #Pedido de encerramento da mensagem
        all = bytes()
        all += head
        all += payloadfinal
        all += EOP

        return all
    elif messageType == 8:
        head = int_to_byte(8,1)+int_to_byte(0,2)+int_to_byte(0,2)+payloadLen+int_to_byte(0,2)+EOP+stuffingByte
        #Erro tipo  1: cliente não recebeu mensagem tipo 2
        all = bytes()
        all += head
        all += payloadfinal
        all += EOP

        return all
    elif messageType == 9:
        head = int_to_byte(9,1)+int_to_byte(0,2)+int_to_byte(0,2)+payloadLen+int_to_byte(0,2)+EOP+stuffingByte
        #Erro tipo 2: servidor não recebeu mensagem tipo 3
        all = bytes()
        all += head
        all += payloadfinal
        all += EOP

        return all
    elif messageType == 0:
        head = int_to_byte(0,1)+int_to_byte(0,2)+int_to_byte(0,2)+payloadLen+int_to_byte(0,2)+EOP+stuffingByte
        #Erro tipo 3: não recebeu ack ou nack em 5 segundos
        all = bytes()
        all += head
        all += payloadfinal
        all += EOP

        return all
    else:
        head = None
        print("erro NOS")
        #messageType fora do protocolo e portanto byte não deve ser formado com HEAD
        all = bytes()
        all += head
        all += payloadfinal
        all += EOP

        return all





def readHeadNAll(receivedAll):
    #print(receivedAll)

    head = receivedAll[0:19]
    messageType = fromByteToInt(head[0:1])
    actualPackage = fromByteToInt(head[1:3])+1
    totalPackage = fromByteToInt(head[3:5])
    txLen = fromByteToInt(head[5:10])
    crc1 = fromByteToInt(head[10:12])
    eopSystem = head[12:15]
    stuffByte = head[15:19]


    #Leitura do messaType do pacote recebido

    #print("Pacote ",actualPackage," de um total de ",totalPackage)

    sanityCheck = bytearray()
    stuffByteCount = 0
    ack = False

    for i in range(19, len(receivedAll)):
        if receivedAll[i:i+1] == stuffByte:
            sanityCheck += receivedAll[i+1:i+14]
            i +=14
        elif eopSystem == receivedAll[i:i+13]:
            #print('EOP: ',receivedAll[i:i+13])
            break

        else:
            sanityCheck += receivedAll[i:i+1]
            #print("\n yep")
            #print(sanityCheck)
            #print("VERIFICANDO PACOTE RECEBIDO")

    #print('SanityCheck ', sanityCheck)
    crcChecked = crc_check(crc1, sanityCheck)
    if len(sanityCheck) == txLen

        #print ("sanityCheck = okay")
        ack = True

        return sanityCheck, txLen, messageType, ack, actualPackage, totalPackage, crcChecked

    else:

        #print("Ue")

        return None, None, messageType, ack ,None, None, None



def teste():
    img = Image.open('circuit.jpg', mode='r')
    imgByteArr = io.BytesIO()
    img.save(imgByteArr, format='JPEG')
    imgByteArr = imgByteArr.getvalue()
    testeSubject = encapsulate(imgByteArr,4)
    sanityCheck, txLen, messageType, ack, actualPackage, totalPackage= readHeadNAll(testeSubject[0])
    print(ack)
    #print(txLen)
teste()
