Android  TextView中部分文字高亮显示

```java
/**
* 关键字高亮显示
*
* @param context 上下文
* @param text 需要显示的文字
* @param target 需要高亮的关键字
* @param color 高亮颜色
* @param start 头部增加高亮文字个数
* @param end 尾部增加高亮文字个数
* @return 处理完后的结果
*/

public static SpannableString highlight(Context context, String text, String target, String color, int start, int end) {

    SpannableString spannableString = new SpannableString(text);
    Pattern pattern = Pattern.compile(target);
    Matcher matcher = pattern.matcher(text);
    while (matcher.find()) {
        ForegroundColorSpan span = new ForegroundColorSpan(Color.parseColor(color));
        spannableString.setSpan(span, matcher.start() - start, matcher.end() + end,
        Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
    }
    return spannableString;
}
```

start与end参数默认情况下传0，当需要高亮的关键字前后有符号时(比如[高亮])，start与end参数可传1。

调用方法

```java
SpannableString highlightText = StringUtils.highlight(this, "关键字高亮", "高亮", "#EA2D2D", 0, 0);

textView.setText(highlightText);
```