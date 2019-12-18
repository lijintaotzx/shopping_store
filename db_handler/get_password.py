# # coding=utf-8
#
# import sys, tty, termios
#
#
# # for python 3.x
# def getch():
#     fd = sys.stdin.fileno()
#     old_settings = termios.tcgetattr(fd)
#     try:
#         tty.setraw(sys.stdin.fileno())
#         ch = sys.stdin.read(1)
#     finally:
#         termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
#     return ch
#
#
# def getpass(maskchar="*"):
#     password = ""
#     while True:
#         ch = getch()
#         if ch == "\r" or ch == "\n":
#             print
#             return password
#         elif ch == "\b" or ord(ch) == 127:
#             if len(password) > 0:
#                 sys.stdout.write("\b \b")
#                 password = password[:-1]
#         else:
#             if maskchar != None:
#                 sys.stdout.write(maskchar)
#             password += ch
#
#
# if __name__ == "__main__":
#     print("Enter your password:", )
#     password = getpass("*")
#     print("your password is %s" % password)

import msvcrt, sys, os
print('password: ', end='', flush=True)

li = []

while 1:
    ch = msvcrt.getch()
    #回车
    if ch == b'\r':
        msvcrt.putch(b'\n')
        print('输入的密码是：%s' % b''.join(li).decode())
        break
    #退格
    elif ch == b'\x08':
        if li:
            li.pop()
            msvcrt.putch(b'\b')
            msvcrt.putch(b' ')
            msvcrt.putch(b'\b')
    #Esc
    elif ch == b'\x1b':
        break
    else:
        li.append(ch)
        msvcrt.putch(b'*')

os.system('pause')
