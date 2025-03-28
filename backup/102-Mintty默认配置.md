在SmartPutty中使用Mintty时, 在个人目录~下添加以下配置: 

## .minttyrc

```rc
ThemeFile=dracula
Locale=zh_CN
Charset=UTF-8
Font=JetBrains Maple Mono Regular
FontHeight=12

Rows=30
Columns=100
Scrollbar=none
ScrollbackLines=10000
ForegroundColour=131,148,150
BackgroundColour=0,43,54
CursorColour=220,50,47
Transparency=low
OpaqueWhenFocused=no
Term=xterm-256color
Charset=UTF-8
Clipboard=RightClick,ShiftIns
MouseTracking=yes
BellSound=
BellTaskbar=no
```

## .bashrc

```
alias c:='cd /cygdrive/c'
alias d:='cd /cygdrive/d'
alias ll='ls -al'

PS1='\w\$ '
```