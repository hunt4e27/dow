import requests

def extract_download_links(data):
    links = []

    formats = data.get('formats', [])
    for fmt in formats:
        fmt_id = fmt.get('id')
        quality = fmt.get('quality')
        mime = fmt.get('mime')
        if fmt_id:
            download_url = f"https://px29.genyoutube.online/mates/en/download?url={fmt_id}"
            links.append({
                'quality': quality,
                'mime': mime,
                'url': download_url
            })
    
    return links


def display_links(links):
    print("\n✅ روابط التحميل المتوفرة:\n")
    for idx, link in enumerate(links, 1):
        print(f"{idx}. الجودة: {link['quality']} | النوع: {link['mime']}")
        print(f"   🔗 {link['url']}\n")


def main():
    # هنا تدخل رابط فيديو YouTube
    youtube_url = "https://www.youtube.com/watch?v=gtWxG1NislE"
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://genyoutube.online',
        'referer': 'https://genyoutube.online/en1/',
        'user-agent': 'Mozilla/5.0',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'url': youtube_url,
        'ajax': '1',
        'lang': 'en',
    }

    print("🔍 جاري تحليل الرابط...")
    response = requests.post(
        'https://genyoutube.online/mates/en/analyze/ajax?retry=undefined&platform=youtube',
        headers=headers,
        data=data
    )

    if response.status_code == 200:
        try:
            json_data = response.json()
            download_links = extract_download_links(json_data)

            if download_links:
                display_links(download_links)
            else:
                print("❌ لم يتم العثور على روابط تحميل.")
        except Exception as e:
            print("❌ فشل في تحليل الرد:", e)
            print(response.text[:500])
    else:
        print("❌ فشل الاتصال بالخادم.")


if __name__ == "__main__":
    main()

