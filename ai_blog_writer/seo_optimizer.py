def enhance_with_seo(blog: str, keywords: list) -> str:
    for keyword in keywords:
        if keyword.lower() not in blog.lower():
            blog += f"\n\nSEO Keyword: {keyword}"
    return blog