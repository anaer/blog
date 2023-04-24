---
title: 代码格式化时如何保留部分代码的原始格式
date: "2023-04-24T15:13:28.000Z"
description: 代码格式化时如何保留部分代码的原始格式
tags:
  - java
  - formatter
last_updated: "2023-04-24T15:13:28.000Z"
---

在一些情况下，代码格式化可能会破坏代码的结构，或者导致代码难以阅读。
例如，当代码中存在大量的嵌套结构、长字符串或注释时，自动格式化可能会使代码难以阅读或理解。

使用 `@formatter:off` 注释标记可以让 IDE 或代码编辑器停止格式化代码，从而保留代码的原始格式。
在需要恢复自动格式化时，可以使用 `@formatter:on` 注释标记来重新开启自动格式化。

`@formatter:off` 注释标记的作用范围是从当前位置开始直到文件结尾或遇到 `@formatter:on` 注释标记为止。
因此，在使用 `@formatter:off` 和 `@formatter:on` 注释标记时，需要注意注释的作用范围，避免影响其他代码的格式化。

举个例子:

```java
	@Test
	public void logoutWhenNoSecurityContextRepositoryThenHttpSessionSecurityContextRepository() throws Exception {
		this.spring.register(InvalidateHttpSessionFalseConfig.class).autowire();
		MockHttpSession session = mock(MockHttpSession.class);
		// @formatter:off
		MockHttpServletRequestBuilder logoutRequest = post("/logout")
				.with(csrf())
				.with(user("user"))
				.session(session)
				.header(HttpHeaders.ACCEPT, MediaType.TEXT_HTML_VALUE);
		this.mvc.perform(logoutRequest)
				.andExpect(status().isFound())
				.andExpect(redirectedUrl("/login?logout"))
				.andReturn();
		// @formatter:on
		verify(session).removeAttribute(HttpSessionSecurityContextRepository.SPRING_SECURITY_CONTEXT_KEY);
	}
```

[code link](https://github.com/spring-projects/spring-security/commit/a4840445912b070f3a3deb154b245dccd1b9575f)
