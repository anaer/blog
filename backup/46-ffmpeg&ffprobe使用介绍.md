
## 下载一帧图片

```sh
ffmpeg -i http://117.148.179.136/PLTV/88888888/224/3221231567/index.m3u8 -ss 1 -frames:v 1 aaaa.jpg
```

## 获取直播流分辨率

```sh
# 查询流信息, 指定输出字段
ffprobe -v quiet -of json -show_entries stream=width,height http://play-live.ifeng.com/live/06OLEGEGM4G.m3u8

# 查询流信息并输出json格式
ffprobe -v quiet -of json -show_streams -rw_timeout 3000 -stimeout 3000 http://play-live.ifeng.com/live/06OLEGEGM4G.m3u8
```

## 参数说明

```
-rw_timeout 读写超时时间, 单位微秒, 1秒=1000000微秒
-stimeout socket读写超时时间, 单位微秒, 1秒=1000000微秒
```

```log
usage: ffprobe [OPTIONS] [INPUT_FILE]

Main options:
-L                  show license
-h topic            show help
-? topic            show help
-help topic         show help
--help topic        show help
-version            show version
-buildconf          show build configuration
-formats            show available formats
-muxers             show available muxers
-demuxers           show available demuxers
-devices            show available devices
-codecs             show available codecs
-decoders           show available decoders
-encoders           show available encoders
-bsfs               show available bit stream filters
-protocols          show available protocols
-filters            show available filters
-pix_fmts           show available pixel formats
-layouts            show standard channel layouts
-sample_fmts        show available audio sample formats
-colors             show available color names
-loglevel loglevel  set logging level
-v loglevel         set logging level
-report             generate a report
-max_alloc bytes    set maximum size of a single allocated block
-cpuflags flags     force specific cpu flags
-hide_banner hide_banner  do not show program banner
-sources device     list sources of the input device
-sinks device       list sinks of the output device
-f format           force format
-unit               show unit of the displayed values
-prefix             use SI prefixes for the displayed values
-byte_binary_prefix  use binary prefixes for byte units
-sexagesimal        use sexagesimal format HOURS:MM:SS.MICROSECONDS for time units
-pretty             prettify the format of displayed values, make it more human readable
-print_format format  set the output printing format (available formats are: default, compact, csv, flat, ini, json, xml)
-of format          alias for -print_format
-select_streams stream_specifier  select the specified streams
-sections           print sections structure and section information, and exit
-show_data          show packets data
-show_data_hash     show packets data hash
-show_error         show probing error
-show_format        show format/container info
-show_frames        show frames info
-show_format_entry entry  show a particular entry from the format/container info
-show_entries entry_list  show a set of specified entries
-show_log           show log
-show_packets       show packets info
-show_programs      show programs info
-show_streams       show streams info
-show_chapters      show chapters info
-count_frames       count the number of frames per stream
-count_packets      count the number of packets per stream
-show_program_version  show ffprobe version
-show_library_versions  show library versions
-show_versions      show program and library versions
-show_pixel_formats  show pixel format descriptions
-show_private_data  show private data
-private            same as show_private_data
-bitexact           force bitexact output
-read_intervals read_intervals  set read intervals
-default            generic catch all option
-i input_file       read specified file
-find_stream_info   read and decode the streams to fill missing information with heuristics
```
