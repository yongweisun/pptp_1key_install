import socket
import os
def getIp():
    hostname=socket.gethostname()
    addrs=socket.getaddrinfo(hostname,None)
    #if(addrs.count==1):
    #    return addrs[0][4]
    inetaddrs=[]
    for addr in addrs:
        if(addr[0]==2):
            inetaddrs.append(addr[4][0])
            #print(addr)
    return inetaddrs

def writeFileLines(openedFile,lines):
        for line in lines:
            openedFile.write(line)
            openedFile.write("\n")
def writeFile(filename,lines):
    file=open(filename,"w")
    writeFileLines(file,lines)
    file.close
def appendFile(filename,lines):
    file=open(filename,"a")
    writeFileLines(file,lines)
    file.close


def addNewUser(username,password,create):
    lines=["%s\t*\t%s\t*"%(username,password)]
    filename="/etc/ppp/chap-secrets";
    if(create):
        writeFile(filename,lines)
    else:
        appendFile(filename,lines)


def settingUpPptpdConf(ip):
    lines=["option /etc/ppp/pptpd-options",
        "logwtmp" ,
        "localip %s"%(ip) ,
        "remoteip 10.1.0.1-100" ,]
    writeFile("/etc/pptpd.conf",lines)

def setupPptpdOptions():
    lines=["name pptpd",
    "refuse-pap",
    "refuse-chap",
    "refuse-mschap",
    "require-mschap-v2",
    "require-mppe-128",
    "ms-dns 8.8.8.8",
    "ms-dns 8.8.4.4",
    "proxyarp",
    "nodefaultroute",
    "lock",
    "nobsdcomp"]
    writeFile("/etc/ppp/pptpd-options",lines)

def setupPptp(ip,username,password):
    print()
    print("######################################################")
    print( "Downloading and Installing PoPToP")
    print( "######################################################")
    os.system("apt-get -y install pptpd")
    
   
    setupPptpdOptions()
    ## setting up pptpd.conf
    settingUpPptpdConf(ip)
    ## adding new user
    addNewUser(username,password,True)
    print()
    print("######################################################")
    print("Forwarding IPv4 and Enabling it on boot")
    print("######################################################")
    appendFile("/etc/sysctl.conf",["net.ipv4.ip_forward=1"])
    os.system("sysctl -p")

    print()
    print("######################################################")
    print("Updating IPtables Routing and Enabling it on boot")
    print("######################################################")
    os.system("iptables -t nat -A POSTROUTING -j SNAT --to %s"%(ip))
    # saves iptables routing rules and enables them on-boot
    os.system("iptables-save > /etc/iptables.conf")

    writeFile("/etc/network/if-pre-up.d/iptables",["#!/bin/sh","iptables-restore < /etc/iptables.conf"]);

    os.system("chmod +x /etc/network/if-pre-up.d/iptables")
    
    appendFile("/etc/ppp/ip-up",["ifconfig ppp0 mtu 1400"])

    print()
    print("######################################################")
    print("Restarting PoPToP")
    print("######################################################")
    os.system("sleep 5")
    os.system("/etc/init.d/pptpd restart")

    print()
    print("######################################################")
    print("Server setup complete!")
    print("Connect to your VPS at %s with these credentials:"%(ip))
    print("Username:%s ##### Password: %s"%(username,password))
    print("######################################################")



def addUser():
    a=1
def selectIP():
    #addrs=getIp()    
    #index=0
    #for addr in addrs:
    #    print(index,addr)
    #    index+=1
    #if(addrs.count==1):
    #    return addrs[0]
    #selectIndex=int(input("please select a ip:"))
    #return addrs[selectIndex]
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip
def printInfo():
    print("######################################################")
    print("Interactive PoPToP Install Script for utuntu or debian servers")
    print("")
    print("Make sure to contact your provider and have them enable")
    print("IPtables and ppp modules prior to setting up PoPToP.")
    print("PPP can also be enabled from SolusVM.")
    print("")
    print("You need to set up the server before creating more users.")
    print("A separate user is required per connection or machine.")
    print("######################################################")
    print("")
    print("")
    print("######################################################")
    print("your ip is: ",ip)
    print("Select on option:")
    print("1) Set up new PoPToP server AND create one user")
    print("2) Create additional users")
    print("######################################################")


ip=selectIP()
print("your redirect ip is",ip)
printInfo()
x=int(input(""))
username=input("username:\n")
password=input("password:\n")
if(x==1):
    setupPptp(ip,username,password)
if(x==2):
    addNewUser(username,password,False)
    os.system("/etc/init.d/pptpd restart")


