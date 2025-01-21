## 我的电脑删除3D对象等

```reg
Windows Registry Editor Version 5.00
; 删除导航窗格对应文件夹，-表示删除注册表项，不写-表示增加注册表项

; 删除3D对象
[-HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{0DB7E03F-FC29-4DC6-9020-FF41B59E513A}]

; 删除视频
[-HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{f86fa3ab-70d2-4fc7-9c99-fcbf05467f3a}]

; 删除图片
[-HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{24ad3ad4-a569-4530-98e1-ab02f9417aa8}]

; 删除文档
[-HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{d3162b92-9365-467a-956b-92703aca08af}]

; 删除下载
[-HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{088e3905-0323-4b02-9826-5d99428e115f}]

; 删除音乐
[-HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{3dfdf296-dbec-4fb4-81d1-6a3438bcf4de}]

; 删除桌面
[-HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}]
```

## 新增右键菜单openWithNotepad2

```reg
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\*\shell\Open with Notepad2]
"Icon"="D:\\totalcmd\\Tools\\Notepad2.exe,0"

[HKEY_CLASSES_ROOT\*\shell\Open with Notepad2\command]
@="\"D:\\totalcmd\\Tools\\Notepad2.exe\" \"%1\""
```

## 替换系统默认的notepad

```reg
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\notepad.exe]
"Debugger"="\"D:\\totalcmd\\Tools\\Notepad2.exe\" \"%1\""
```

## 禁用Win10&11系统更新

```reg
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings]
"FlightSettingsMaxPauseDays"=dword:00001b58
"PauseFeatureUpdatesStartTime"="2023-07-07T10:00:52Z"
"PauseFeatureUpdatesEndTime"="2042-09-05T09:59:52Z"
"PauseQualityUpdatesStartTime"="2023-07-07T10:00:52Z"
"PauseQualityUpdatesEndTime"="2042-09-05T09:59:52Z"
"PauseUpdatesStartTime"="2023-07-07T09:59:52Z"
"PauseUpdatesExpiryTime"="2042-09-05T09:59:52Z"
```

## 设置默认浏览器

```reg
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\http\shell\open\command]
@="\"D:\\floorp\\floorp.exe\" -- \"%1\""

[HKEY_CLASSES_ROOT\https\shell\open\command]
@="\"D:\\floorp\\floorp.exe\" -- \"%1\""

```