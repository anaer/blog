---
title: Java修改mp3的tag信息
date: "2023-05-18T13:45:56.000Z"
description: Java修改mp3的tag信息
tags:
  - java
  - music
last_updated: "2023-05-18T13:45:56.000Z"
---

```toc
# This code block gets replaced with the TOC
```

### 添加pom.xml依赖

```xml
<dependency>
    <groupId>org</groupId>
    <artifactId>jaudiotagger</artifactId>
    <version>2.0.3</version>
</dependency>
```

### 修改tag信息

```java
    /**
     * 修改mp3 tag信息
     * @param file mp3文件
     * @param title 标题
     * @param artist 作者
     * @param album 专辑
     */
    public static void setTagInfo(File file, String title, String artist, String album) {
        if (Objects.isNull(file)) {
            return;
        }
        try {
            MP3File mp3File = (MP3File) AudioFileIO.read(file);
            AbstractID3v2Tag tag = mp3File.getID3v2TagAsv24();
            if (Objects.nonNull(tag)) {
                tag.setField(FieldKey.TITLE, title);
                tag.setField(FieldKey.ARTIST, artist);
                tag.setField(FieldKey.ALBUM, album);
            }

            mp3File.setID3v2Tag(tag);
            mp3File.save();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
```