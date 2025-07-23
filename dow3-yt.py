#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Video Downloader Script
يتيح هذا السكريبت تحليل رابط فيديو YouTube وعرض خيارات التحميل المتاحة
"""

import requests
import json
import re
import os
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import time

class YouTubeDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://ss-youtube.online"
        
        # Headers لمحاكاة متصفح حقيقي
        self.headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://ss-youtube.online',
            'priority': 'u=1, i',
            'referer': 'https://ss-youtube.online/fr-b2/',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

    def extract_video_id(self, url):
        """استخراج معرف الفيديو من رابط YouTube"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:v\/|vi\/|be\/)([0-9A-Za-z_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def analyze_video(self, video_url):
        """تحليل الفيديو واستخراج روابط التحميل"""
        print(f"🔍 جاري تحليل الفيديو: {video_url}")
        
        video_id = self.extract_video_id(video_url)
        if not video_id:
            print("❌ رابط فيديو غير صالح")
            return None
            
        print(f"📹 معرف الفيديو: {video_id}")
        
        # معاملات الطلب
        params = {
            'retry': 'undefined',
            'platform': 'youtube',
        }
        
        data = {
            'url': video_url,
            'ajax': '1',
            'lang': 'fr',
        }
        
        try:
            # إرسال طلب التحليل
            response = self.session.post(
                f'{self.base_url}/mates/en/analyze/ajax',
                params=params,
                headers=self.headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    return self.parse_download_options(result.get('result', ''))
                else:
                    print("❌ فشل في تحليل الفيديو")
                    return None
            else:
                print(f"❌ خطأ في الخادم: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ خطأ في الاتصال: {str(e)}")
            return None
        except json.JSONDecodeError:
            print("❌ خطأ في تحليل البيانات المستلمة")
            return None

    def parse_download_options(self, html_content):
        """تحليل HTML واستخراج خيارات التحميل"""
        soup = BeautifulSoup(html_content, 'html.parser')
        options = {
            'audio': [],
            'video': []
        }
        
        # البحث عن خيارات الصوت
        audio_rows = soup.find_all('tr')
        for row in audio_rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                # التحقق من وجود أيقونة الصوت
                if row.find('svg') and 'audio' in str(row).lower():
                    format_text = cells[0].get_text().strip()
                    size_text = cells[1].get_text().strip()
                    
                    # البحث عن رابط التحميل
                    button = cells[2].find('button')
                    if button and button.get('data-url'):
                        options['audio'].append({
                            'format': format_text,
                            'size': size_text,
                            'url': button.get('data-url'),
                            'type': 'audio'
                        })
        
        # البحث عن خيارات الفيديو
        video_rows = soup.find_all('tr')
        for row in video_rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                # التحقق من وجود دقة الفيديو
                quality_text = cells[0].get_text().strip()
                if any(q in quality_text.lower() for q in ['720p', '1080p', '360p', '480p']):
                    size_text = cells[1].get_text().strip()
                    
                    # البحث عن رابط التحميل
                    link = cells[2].find('a') or cells[2].find('button')
                    if link:
                        download_url = link.get('href') or link.get('data-url')
                        if download_url:
                            options['video'].append({
                                'quality': quality_text,
                                'size': size_text,
                                'url': download_url,
                                'type': 'video'
                            })
        
        return options

    def display_options(self, options):
        """عرض خيارات التحميل للمستخدم"""
        if not options or (not options['audio'] and not options['video']):
            print("❌ لم يتم العثور على خيارات تحميل")
            return None
        
        print("\n" + "="*50)
        print("📋 خيارات التحميل المتاحة:")
        print("="*50)
        
        all_options = []
        counter = 1
        
        # عرض خيارات الصوت
        if options['audio']:
            print("\n🎵 ملفات الصوت:")
            for audio in options['audio']:
                print(f"{counter}. {audio['format']} - {audio['size']}")
                all_options.append(audio)
                counter += 1
        
        # عرض خيارات الفيديو
        if options['video']:
            print("\n🎬 ملفات الفيديو:")
            for video in options['video']:
                print(f"{counter}. {video['quality']} - {video['size']}")
                all_options.append(video)
                counter += 1
        
        return all_options

    def download_file(self, url, filename):
        """تحميل الملف"""
        try:
            print(f"⬇️ جاري التحميل: {filename}")
            
            # Headers للتحميل
            download_headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'Referer': 'https://ss-youtube.online/',
            }
            
            response = self.session.get(url, headers=download_headers, stream=True)
            
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # عرض تقدم التحميل
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                print(f"\r📊 التقدم: {progress:.1f}%", end='', flush=True)
                
                print(f"\n✅ تم التحميل بنجاح: {filename}")
                return True
            else:
                print(f"❌ فشل التحميل: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في التحميل: {str(e)}")
            return False

    def get_safe_filename(self, url, format_info, video_id):
        """إنشاء اسم ملف آمن"""
        # استخراج امتداد الملف من النوع
        if 'mp3' in format_info.lower() or format_info.get('type') == 'audio':
            ext = '.mp3'
        elif 'mp4' in format_info.lower() or format_info.get('type') == 'video':
            ext = '.mp4'
        else:
            ext = '.mp4'  # افتراضي
        
        # إنشاء اسم الملف
        if isinstance(format_info, dict):
            if 'quality' in format_info:
                quality = format_info['quality'].replace(' ', '_')
            else:
                quality = format_info['format'].replace(' ', '_')
        else:
            quality = str(format_info).replace(' ', '_')
        
        filename = f"{video_id}_{quality}{ext}"
        
        # إزالة الأحرف غير المسموحة
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        return filename

def main():
    print("🎬 مرحباً بك في أداة تحميل مقاطع YouTube")
    print("="*50)
    
    downloader = YouTubeDownloader()
    
    while True:
        try:
            # طلب رابط الفيديو من المستخدم
            video_url = input("\n📎 أدخل رابط فيديو YouTube (أو 'exit' للخروج): ").strip()
            
            if video_url.lower() in ['exit', 'quit', 'خروج']:
                print("👋 وداعاً!")
                break
            
            if not video_url:
                print("❌ يرجى إدخال رابط صالح")
                continue
            
            # تحليل الفيديو
            options = downloader.analyze_video(video_url)
            
            if not options:
                continue
            
            # عرض الخيارات
            all_options = downloader.display_options(options)
            
            if not all_options:
                continue
            
            # طلب اختيار المستخدم
            while True:
                try:
                    choice = input(f"\n🔢 اختر رقم الملف للتحميل (1-{len(all_options)} أو 'back' للعودة): ").strip()
                    
                    if choice.lower() in ['back', 'عودة']:
                        break
                    
                    choice_num = int(choice)
                    
                    if 1 <= choice_num <= len(all_options):
                        selected_option = all_options[choice_num - 1]
                        video_id = downloader.extract_video_id(video_url)
                        
                        # إنشاء اسم الملف
                        filename = downloader.get_safe_filename(
                            selected_option['url'], 
                            selected_option, 
                            video_id
                        )
                        
                        # التحميل
                        success = downloader.download_file(selected_option['url'], filename)
                        
                        if success:
                            print(f"📁 الملف محفوظ في: {os.path.abspath(filename)}")
                        
                        break
                    else:
                        print(f"❌ يرجى اختيار رقم بين 1 و {len(all_options)}")
                        
                except ValueError:
                    print("❌ يرجى إدخال رقم صالح")
                except KeyboardInterrupt:
                    print("\n\n👋 تم إلغاء العملية")
                    return
                    
        except KeyboardInterrupt:
            print("\n\n👋 تم إلغاء العملية")
            break
        except Exception as e:
            print(f"❌ خطأ غير متوقع: {str(e)}")

if __name__ == "__main__":
    main()
