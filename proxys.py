__author__ = 'jmpews'
import socket
from redisq import RedisQueue
import errno
import select
import time
import utils

# 采用非阻塞的connect,每个IP测试4个端口,手动做好每个socket的connect的超时处理
# 几个注意点:
# 1.IP的区段 http://ips.chacuo.net/
# 2.非阻塞connect的返回码'EINPROGRESS',表示正在连接
# 3.http代理的验证方式,send一段http报文,验证返回.


# rq=RedisQueue('socks5')
# rq=RedisQueue('https')

# 爬取IP段
# ipfile=open('ip_zhejiang.txt','r',encoding='utf-8')
# iplist=[]
# for line in ipfile:
#     tmp=line.split('\t')
#     iplist.append((tmp[0],tmp[1]))
# ipfile.close()

# # 从米扑上购买代理
# ipfile=open('httph.txt','r',encoding='utf-8')
# # ipfile=open('socks5.txt','r',encoding='utf-8')
# iplist=[]
# for line in ipfile:
#     tmp=line.split(':')
#     iplist.append((tmp[0],int(tmp[1])))
# ipfile.close()

# ips=utils.genips(iplist)
# ips=utils.genips([('180.161.130.11','180.161.130.12')])


#test
# outputimeouts+=utils.addips('118.144.108.254')
def checkproxy(ips,proxytype='http'):
    inputs=[]
    outputs=[]
    outputimeouts=[]
    inputimeouts=[]
    result=[]
    flag=0
    while outputimeouts or inputs or not flag:
        # 清理超时socket和补充数据
        outputimeouts,outputs,inputimeouts,inputs,flag=utils.updatelist(outputimeouts,inputimeouts,ips)
        readable,writeable,exceptional=select.select(inputs,outputs,[],2)
        for x in readable:
            try:
                errwrite=x.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                detial=x.getpeername()
                # print(detial)
                data=x.recv(1024)
                # print(data)
            except Exception as e:
                inputimeouts=list(filter(lambda tm:tm[0].fileno()!=x.fileno(),inputimeouts))
                print('Read-Error:',errwrite)
                x.close()
                continue
            if proxytype=='http':
                if utils.checkhttp(data):
                    # print('HTTP: ',detial)
                    result.append(','.join([detial[0],str(detial[1]),proxytype]))
                    # rq.put('http:'+detial[0]+':'+str(detial[1]))
            else:
                if utils.checksocks(data):
                    # print('SOCK5: ',detial)
                    result.append(','.join([detial[0],str(detial[1]),proxytype]))
                    # rq.put('http:'+detial[0]+':'+str(detial[1]))
            inputimeouts=list(filter(lambda tm:tm[0].fileno()!=x.fileno(),inputimeouts))
            # inputs.remove(x)
            x.close()

        for x in writeable:
            erro=x.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            # connect拒绝
            if erro==errno.ECONNREFUSED:
                # print('conn refuse.')
                outputimeouts=list(filter(lambda tm:tm[1]!=x.fileno(),outputimeouts))
                # outputs.remove(x)
                x.close()
                continue

            # 超时
            elif erro==errno.ETIMEDOUT:
                # print('conn timeout.')
                outputimeouts=list(filter(lambda tm:tm[1]!=x.fileno(),outputimeouts))
                # outputs.remove(x)
                x.close()
                continue

            # 不可到达
            elif erro==errno.EHOSTUNREACH:
                # print('host unreach.')
                outputimeouts=list(filter(lambda tm:tm[1]!=x.fileno(),outputimeouts))
                # outputs.remove(x)
                x.close()
                continue

            # 正常connect
            # 发送http代理验证数据
            elif erro==0:
                # print('connect success')
                if proxytype=='http':
                    utils.sendhttp(x)
                else:
                    utils.sendsocks(x)
                outputimeouts=list(filter(lambda tm:tm[1]!=x.fileno(),outputimeouts))
                # outputs.remove(x)
                inputimeouts.append([x,time.time()])
                # inputs.append(x)


        for x in exceptional:
            print('====EXCEP====')

        # print(outputimeouts,inputs,flag)
        # ip=ips.__next__()
        # print(ip)
        # print('loop...')
    return result
# checkproxy(ips)