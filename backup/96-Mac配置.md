
1. 设置程序坞显示与隐藏时间, 设置为 0 无延迟显示隐藏。
defaults write com.apple.Dock autohide-delay -float 0 && killall Dock

2. 防止 macOS 的 Finder 在网络设备或者 USB 设备上生成 .DS_Store 文件
defaults write com.apple.desktopservices DSDontWriteNetworkStores true
defaults write com.apple.desktopservices DSDontWriteUSBStores -bool true

3. 不需要拖动标题栏，只要按住 Ctrl + Command 之后，在窗口任意位置就可以拖动窗口：
defaults write -g NSWindowShouldDragOnGesture -bool true

4. 访达显示文件扩展名
defaults write NSGlobalDomain "AppleShowAllExtensions" -bool "true" && killall Finder

5. 访达显示隐藏文件
defaults write com.apple.finder "AppleShowAllFiles" -bool "true" && killall Finder

6. 访达显示路径栏
defaults write com.apple.finder "ShowPathbar" -bool "true" && killall Finder

7. 访达将文件夹放于最前方显示
defaults write com.apple.finder "_FXSortFoldersFirst" -bool "true" && killall Finder

8. dmg安装提示文件损坏
xattr -cr /Applications/demo.app

### 相关链接
1. [macOS defaults list](https://macos-defaults.com/)