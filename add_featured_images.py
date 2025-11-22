#!/usr/bin/env python3
"""
各ブログ記事の先頭画像を取得して記事の先頭に配置
ブログ一覧ページに画像とタイトルを表示
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import os
from urllib.parse import urljoin, urlparse
from pathlib import Path
import hashlib
from datetime import datetime

def download_image(img_url, save_dir):
    """画像をダウンロード"""
    try:
        if img_url.startswith('data:') or 'note_empty_ogp' in img_url or 'empty' in img_url.lower() or 'icon' in img_url.lower():
            return None
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(img_url, headers=headers, timeout=15, stream=True)
        response.raise_for_status()
        
        parsed = urlparse(img_url)
        filename = os.path.basename(parsed.path)
        
        if not filename or '.' not in filename:
            url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
            content_type = response.headers.get('Content-Type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            elif 'webp' in content_type:
                ext = '.webp'
            else:
                ext = '.jpg'
            filename = f"note_{url_hash}{ext}"
        
        filename = re.sub(r'[^\w\.-]', '_', filename)
        save_path = os.path.join(save_dir, filename)
        
        if os.path.exists(save_path):
            return f"../img/blog/{filename}"
        
        os.makedirs(save_dir, exist_ok=True)
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return f"../img/blog/{filename}"
    except Exception as e:
        print(f"  ✗ Error downloading {img_url}: {e}")
        return None

def get_first_image_from_article(article_url, img_dir):
    """記事から最初の画像を取得"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(article_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 記事本文を取得
        content_div = soup.find('div', class_=re.compile(r'note-body|note-content|article-body', re.I))
        if not content_div:
            content_div = soup.find('article')
        if not content_div:
            content_div = soup.find('main')
        
        if not content_div:
            return None
        
        # 最初の画像を取得
        images = content_div.find_all('img')
        for img in images:
            src = img.get('src') or img.get('data-src') or img.get('data-original')
            if src and not src.startswith('data:') and 'note_empty_ogp' not in src and 'empty' not in src.lower() and 'icon' not in src.lower():
                full_url = urljoin(article_url, src)
                local_path = download_image(full_url, img_dir)
                if local_path:
                    return local_path
        
        # 背景画像もチェック
        for tag in content_div.find_all(True):
            style = tag.get('style', '')
            if 'background-image' in style:
                urls = re.findall(r'url\(["\']?([^"\'()]+)["\']?\)', style)
                for url in urls:
                    if url.startswith('http') and 'icon' not in url.lower():
                        local_path = download_image(url, img_dir)
                        if local_path:
                            return local_path
        
        return None
    except Exception as e:
        print(f"  Error getting first image: {e}")
        return None

def add_featured_image_to_article(article_file, featured_image):
    """記事の先頭に画像を追加"""
    if not featured_image:
        return False
    
    with open(article_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # 記事ヘッダーを探す
    header = soup.find('header', class_='mb-8')
    if not header:
        return False
    
    # 既に画像があるかチェック
    existing_img = header.find('img')
    if existing_img:
        # 既存の画像を更新
        existing_img['src'] = featured_image
        existing_img['class'] = 'w-full h-64 md:h-96 object-cover rounded-lg mb-6 shadow-lg'
        existing_img['alt'] = soup.find('h1').get_text() if soup.find('h1') else '記事画像'
        existing_img['loading'] = 'lazy'
    else:
        # 新しい画像を追加
        new_img = soup.new_tag('img')
        new_img['src'] = featured_image
        new_img['class'] = 'w-full h-64 md:h-96 object-cover rounded-lg mb-6 shadow-lg'
        new_img['alt'] = soup.find('h1').get_text() if soup.find('h1') else '記事画像'
        new_img['loading'] = 'lazy'
        
        # 日付の後に挿入
        date_p = header.find('p', class_='text-gray-500')
        if date_p:
            date_p.insert_after(new_img)
        else:
            header.append(new_img)
    
    with open(article_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    return True

def generate_article_card_with_image(article, featured_image, delay_ms=0):
    """画像付きの記事カードを生成"""
    # タグを推測
    tags = []
    title_lower = article['title'].lower()
    if 'ai' in title_lower or '生成ai' in title_lower:
        tags.append('AI')
    if 'llm' in title_lower:
        tags.append('LLM')
    if '税理士' in article['title'] or '転記' in article['title']:
        tags.append('税理士')
        tags.append('業務効率化')
    if 'google' in title_lower or 'gemini' in title_lower:
        tags.append('Gemini CLI')
    if '情報漏洩' in article['title'] or 'セキュリティ' in article['title']:
        tags.append('情報漏洩対策')
        tags.append('セキュリティ')
    if '旅行' in article['title'] or 'うどん' in article['title']:
        tags.append('業務効率化')
        tags.append('Googleマップ')
    if '読書' in article['title'] or '本' in article['title']:
        tags.append('AI活用')
    if 'パスポート' in article['title']:
        tags.append('AI活用')
        tags.append('教育')
    if 'データ' in article['title'] or '予測' in article['title']:
        tags.append('AI活用')
        tags.append('データ分析')
    
    # タグのHTMLを生成
    tags_html = ''
    tag_colors = {
        "AI": "bg-purple-100 text-purple-700",
        "LLM": "bg-indigo-100 text-indigo-700",
        "業務効率化": "bg-green-100 text-green-700",
        "税理士": "bg-blue-100 text-blue-700",
        "情報漏洩対策": "bg-red-100 text-red-700",
        "セキュリティ": "bg-red-100 text-red-700",
        "Gemini CLI": "bg-yellow-100 text-yellow-700",
        "Googleマップ": "bg-orange-100 text-orange-700",
        "AI活用": "bg-purple-100 text-purple-700",
        "データ分析": "bg-indigo-100 text-indigo-700",
        "教育": "bg-pink-100 text-pink-700",
    }
    
    for i, tag in enumerate(tags[:3]):
        color_class = tag_colors.get(tag, "bg-gray-100 text-gray-700")
        tags_html += f'<span class="px-3 py-1 {color_class} text-xs font-semibold rounded-full">{tag}</span>\n                            '
    
    # 画像のHTML
    image_html = ''
    if featured_image:
        image_html = f'<img src="{featured_image}" alt="{article["title"]}" class="w-full h-48 object-cover">'
    else:
        # デフォルト画像
        image_html = '<div class="w-full h-48 bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center"><span class="text-white text-2xl font-bold">📝</span></div>'
    
    # 記事のパス
    article_href = f"blog/{article['slug']}.html"
    
    return f"""
                <article class="blog-card bg-white rounded-2xl border border-gray-200 shadow-lg overflow-hidden fade-in" {"style=\"transition-delay: " + str(delay_ms) + "ms;\"" if delay_ms > 0 else ""}>
                    <a href="{article_href}" class="block">
                        {image_html}
                        <div class="p-6">
                            <div class="flex flex-wrap gap-2 mb-3">
                                {tags_html}
                            </div>
                            <h2 class="text-xl font-bold text-gray-900 mb-3 hover:text-indigo-600 transition-colors">
                                {article['title']}
                            </h2>
                            <p class="text-sm text-gray-500 mb-4">{article['date']}</p>
                            <p class="text-gray-600 leading-relaxed">
                                {article['excerpt']}
                            </p>
                            <span class="inline-block mt-4 text-indigo-600 font-semibold hover:underline">続きを読む →</span>
                        </div>
                    </a>
                </article>
        """

def update_blog_listing(articles_data, featured_images, file_path):
    """ブログ一覧ページを更新"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    articles_html = ""
    # 日付でソート（新しい順）
    sorted_articles = sorted(articles_data, key=lambda x: datetime.fromisoformat(x['date_obj']), reverse=True)
    
    for i, article in enumerate(sorted_articles):
        slug = article['slug']
        featured_image = featured_images.get(slug)
        articles_html += generate_article_card_with_image(article, featured_image, delay_ms=i*100)
    
    # プレースホルダーを置き換え
    updated_content = content.replace(
        '<!-- ブログ記事一覧 -->\n            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">\n                <!-- Articles will be inserted here -->\n            </div>',
        f'<!-- ブログ記事一覧 -->\n            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">\n{articles_html}            </div>'
    )
    
    # 既に記事がある場合の置き換え
    pattern = r'<!-- ブログ記事一覧.*?<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">.*?</div>'
    if re.search(pattern, updated_content, re.DOTALL):
        updated_content = re.sub(
            pattern,
            f'<!-- ブログ記事一覧 -->\n            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">\n{articles_html}            </div>',
            updated_content,
            flags=re.DOTALL
        )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Updated {file_path}")

if __name__ == '__main__':
    # JSONファイルを読み込む
    with open('note_articles.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    img_dir = 'img/blog'
    os.makedirs(img_dir, exist_ok=True)
    
    print("Getting featured images for all articles...\n")
    
    featured_images = {}
    
    # 各記事の先頭画像を取得
    for article in articles:
        print(f"Processing: {article['title']}")
        article_file = f"blog/{article['slug']}.html"
        
        if os.path.exists(article_file):
            featured_image = get_first_image_from_article(article['url'], img_dir)
            if featured_image:
                featured_images[article['slug']] = featured_image
                print(f"  ✓ Found featured image: {featured_image}")
                
                # 記事の先頭に画像を追加
                if add_featured_image_to_article(article_file, featured_image):
                    print(f"  ✓ Added to article: {article_file}")
            else:
                print(f"  - No featured image found")
        else:
            print(f"  ✗ File not found: {article_file}")
        print()
    
    # ブログ一覧ページを更新
    print("Updating blog listing pages...\n")
    update_blog_listing(articles, featured_images, 'blog.html')
    
    # index.htmlのブログセクションも更新
    with open('index.html', 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    # index.htmlのブログセクションを探す
    blog_section_pattern = r'(<section id="blog"[^>]*>.*?<!-- ブログ記事一覧.*?<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">).*?(</div>.*?</section>)'
    match = re.search(blog_section_pattern, index_content, re.DOTALL)
    
    if match:
        articles_html = ""
        sorted_articles = sorted(articles, key=lambda x: datetime.fromisoformat(x['date_obj']), reverse=True)
        
        for i, article in enumerate(sorted_articles):
            slug = article['slug']
            featured_image = featured_images.get(slug)
            articles_html += generate_article_card_with_image(article, featured_image, delay_ms=i*100)
        
        updated_index = re.sub(
            r'(<!-- ブログ記事一覧.*?<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">).*?(</div>)',
            f'\\1\n{articles_html}                \\2',
            index_content,
            flags=re.DOTALL
        )
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_index)
        
        print("Updated index.html blog section")
    
    print(f"\n✓ Completed! Featured images for {len(featured_images)} articles")


