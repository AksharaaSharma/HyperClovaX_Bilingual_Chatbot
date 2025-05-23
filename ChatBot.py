import streamlit as st
import requests
from streamlit_extras.colored_header import colored_header
import base64
from Frontend import add_custom_css
from pymongo.errors import DuplicateKeyError
import streamlit as st
import requests
import json
from datetime import datetime
from difflib import SequenceMatcher
from streamlit_extras.add_vertical_space import add_vertical_space
import requests
import os
from PIL import Image, ImageDraw, ImageFont
import io
import hashlib
import random

def extract_search_keywords_from_book(book_info, api_key):
    """Extract contextual search keywords from book information using AI without predefined categories"""
    if not api_key:
        # Fallback - use basic title analysis without predefined categories
        title = book_info.get('bookname') or book_info.get('bookName', '')
        authors = book_info.get('authors') or book_info.get('author', '')
        
        # Extract meaningful words from title and author
        import re
        words = re.findall(r'\b\w+\b', f"{title} {authors}".lower())
        # Filter out common words and return a meaningful word
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'ì˜', 'ì™€', 'ê³¼', 'ì—', 'ì„', 'ë¥¼', 'ì´', 'ê°€'}
        meaningful_words = [word for word in words if len(word) > 3 and word not in common_words]
        
        if meaningful_words:
            return meaningful_words[0]
        else:
            return "books"
    
    title = book_info.get('bookname') or book_info.get('bookName', 'ì•Œ ìˆ˜ ì—†ëŠ” ì œëª©')
    authors = book_info.get('authors') or book_info.get('author', 'ì•Œ ìˆ˜ ì—†ëŠ” ì €ìž')
    
    prompt = f"""
ì±… ì œëª©: "{title}"
ì €ìž: {authors}

ì´ ì±…ì˜ ì œëª©ê³¼ ì €ìž ì •ë³´ë¥¼ ë¶„ì„í•˜ì—¬, ì´ë¯¸ì§€ ê²€ìƒ‰ì— ê°€ìž¥ ì í•©í•œ ì˜ì–´ í‚¤ì›Œë“œë¥¼ ìƒì„±í•´ì£¼ì„¸ìš”.

ë‹¤ìŒ ì§€ì¹¨ì„ ë”°ë¼ì£¼ì„¸ìš”:
1. ì±…ì˜ ë‚´ìš©, ë¶„ìœ„ê¸°, ì£¼ì œë¥¼ ì¶”ì¸¡í•˜ì—¬ ê´€ë ¨ëœ ì‹œê°ì  ìš”ì†Œë¥¼ ìƒê°í•´ë³´ì„¸ìš”
2. ë¯¸ë¦¬ ì •ì˜ëœ ì¹´í…Œê³ ë¦¬ë¥¼ ì‚¬ìš©í•˜ì§€ ë§ê³ , ì±…ì˜ ê³ ìœ í•œ íŠ¹ì„±ì„ ë°˜ì˜í•˜ì„¸ìš”
3. êµ¬ì²´ì ì´ê³  ì‹œê°ì ì¸ ì˜ì–´ ë‹¨ì–´ í•˜ë‚˜ë§Œ ë°˜í™˜í•˜ì„¸ìš”
4. ì¶”ìƒì  ê°œë…ë³´ë‹¤ëŠ” êµ¬ì²´ì ì¸ ì´ë¯¸ì§€ë¥¼ ì—°ìƒì‹œí‚¤ëŠ” ë‹¨ì–´ë¥¼ ì„ íƒí•˜ì„¸ìš”

ì˜ˆì‹œ:
- ë¡œë§¨ìŠ¤ ì†Œì„¤ â†’ "romance", "couple", "sunset", "flowers"
- ì „ìŸ ì†Œì„¤ â†’ "battlefield", "soldier", "ruins", "memorial"
- ê³¼í•™ ë„ì„œ â†’ "laboratory", "research", "microscope", "discovery"
- ì—¬í–‰ ì—ì„¸ì´ â†’ "journey", "landscape", "adventure", "exploration"
- ìš”ë¦¬ ì±… â†’ "kitchen", "ingredients", "cooking", "chef"

ì±…ì˜ íŠ¹ì„±ì„ ê°€ìž¥ ìž˜ í‘œí˜„í•˜ëŠ” ì˜ì–´ í‚¤ì›Œë“œ í•˜ë‚˜ë§Œ ë°˜í™˜í•˜ì„¸ìš”.
"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "ë‹¹ì‹ ì€ ì±…ì˜ ë‚´ìš©ì„ ë¶„ì„í•˜ì—¬ ì‹œê°ì  ì´ë¯¸ì§€ ê²€ìƒ‰ì— ì í•©í•œ í‚¤ì›Œë“œë¥¼ ìƒì„±í•˜ëŠ” ì „ë¬¸ê°€ìž…ë‹ˆë‹¤. ë¯¸ë¦¬ ì •ì˜ëœ ì¹´í…Œê³ ë¦¬ë¥¼ ì‚¬ìš©í•˜ì§€ ì•Šê³ , ê° ì±…ì˜ ê³ ìœ í•œ íŠ¹ì„±ì„ ë°˜ì˜í•œ êµ¬ì²´ì ì¸ í‚¤ì›Œë“œë¥¼ ìƒì„±í•©ë‹ˆë‹¤."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "maxTokens": 20,
        "temperature": 0.7,
        "topP": 0.8,
    }
    
    try:
        response = requests.post(
            "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            keyword = result['result']['message']['content'].strip().lower()
            keyword = keyword.replace('"', '').replace("'", '').strip()
            
            # Clean up the keyword - extract only the main word
            import re
            clean_keyword = re.findall(r'\b[a-zA-Z]+\b', keyword)
            if clean_keyword:
                return clean_keyword[0]
            else:
                return keyword if keyword else "literature"
        else:
            return "literature"
    except Exception as e:
        st.error(f"í‚¤ì›Œë“œ ì¶”ì¶œ ì¤‘ ì˜¤ë¥˜: {e}")
        return "literature"

def fetch_unsplash_image(book_info, unsplash_access_key, api_key):
    """Fetch a contextually appropriate image from Unsplash based on AI-generated keywords"""
    if not unsplash_access_key:
        return None
    
    # Extract contextual keywords using AI (no predefined categories)
    primary_keyword = extract_search_keywords_from_book(book_info, api_key)
    
    # Create unique seed for this book to ensure different images
    title = book_info.get('bookname') or book_info.get('bookName', '')
    authors = book_info.get('authors') or book_info.get('author', '')
    isbn = book_info.get('isbn13') or book_info.get('isbn', '')
    
    # Create a unique seed based on book details
    book_seed = hashlib.md5(f"{title}{authors}{isbn}".encode()).hexdigest()[:8]
    
    # Generate additional contextual terms using AI
    additional_terms = []
    if api_key:
        try:
            context_prompt = f"""
ì£¼ìš” í‚¤ì›Œë“œ: "{primary_keyword}"
ì±… ì œëª©: "{title}"

ì£¼ìš” í‚¤ì›Œë“œì™€ ê´€ë ¨ëœ ì‹œê°ì  ìˆ˜ì‹ì–´ë¥¼ 2-3ê°œ ìƒì„±í•´ì£¼ì„¸ìš”.
ì˜ˆì‹œ:
- "ocean" â†’ "serene", "vast", "blue"
- "forest" â†’ "mysterious", "green", "peaceful"
- "city" â†’ "modern", "bustling", "urban"

ì˜ì–´ ë‹¨ì–´ë§Œ ì‰¼í‘œë¡œ êµ¬ë¶„í•˜ì—¬ ë°˜í™˜í•˜ì„¸ìš”.
"""
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "ì‹œê°ì  ìˆ˜ì‹ì–´ë¥¼ ìƒì„±í•˜ëŠ” ì „ë¬¸ê°€ìž…ë‹ˆë‹¤."
                    },
                    {
                        "role": "user",
                        "content": context_prompt
                    }
                ],
                "maxTokens": 30,
                "temperature": 0.6,
                "topP": 0.7,
            }
            
            response = requests.post(
                "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003",
                headers=headers,
                json=payload,
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                terms_text = result['result']['message']['content'].strip()
                import re
                additional_terms = re.findall(r'\b[a-zA-Z]+\b', terms_text)
                additional_terms = [term for term in additional_terms if len(term) > 2][:3]
        except:
            pass
    
    # Fallback additional terms if AI fails
    if not additional_terms:
        aesthetic_terms = ["beautiful", "artistic", "elegant", "serene", "dramatic", "peaceful", "inspiring", "creative", "atmospheric", "stunning"]
        # Select terms based on book seed for consistency
        seed_int = int(book_seed[:4], 16)
        additional_terms = [aesthetic_terms[seed_int % len(aesthetic_terms)]]
    
    # Select additional term based on book seed
    variety_index = int(book_seed[4:6], 16) % len(additional_terms)
    variety_term = additional_terms[variety_index] if additional_terms else "beautiful"
    
    # Combine primary keyword with AI-generated variety term
    search_query = f"{primary_keyword} {variety_term}"
    
    # Use book seed to determine page number for variety
    page_num = (int(book_seed[:4], 16) % 10) + 1
    
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": search_query,
        "client_id": unsplash_access_key,
        "per_page": 5,
        "page": page_num,
        "orientation": "landscape",
        "content_filter": "high",
        "order_by": "relevant"
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                # Select image based on book seed for consistency
                image_index = int(book_seed[4:6], 16) % len(data['results'])
                image_url = data['results'][image_index]['urls']['regular']
                return image_url
        return None
    except Exception as e:
        st.error(f"ì´ë¯¸ì§€ ê²€ìƒ‰ ì¤‘ ì˜¤ë¥˜: {e}")
        return None

def generate_book_tagline(book_info, api_key):
    """Generate a Korean tagline for the book using HyperCLOVA"""
    if not api_key:
        return "ì±…ê³¼ í•¨ê»˜í•˜ëŠ” íŠ¹ë³„í•œ ì—¬í–‰"  # Default tagline
    
    title = book_info.get('bookname') or book_info.get('bookName', 'ì•Œ ìˆ˜ ì—†ëŠ” ì œëª©')
    authors = book_info.get('authors') or book_info.get('author', 'ì•Œ ìˆ˜ ì—†ëŠ” ì €ìž')
    
    prompt = f"""
ì±… ì œëª©: "{title}"
ì €ìž: {authors}

ì´ ì±…ì— ëŒ€í•œ ë§¤ë ¥ì ì´ê³  ê°„ê²°í•œ í•œêµ­ì–´ íƒœê·¸ë¼ì¸ì„ ë§Œë“¤ì–´ì£¼ì„¸ìš”.
íƒœê·¸ë¼ì¸ì€ 10-15ìž ì´ë‚´ë¡œ ìž‘ì„±í•˜ê³ , ì±…ì˜ ë¶„ìœ„ê¸°ë‚˜ ì£¼ì œë¥¼ ìž˜ í‘œí˜„í•´ì•¼ í•©ë‹ˆë‹¤.
ì˜ˆì‹œ: "ì‚¬ëž‘ì´ ì‹œìž‘ë˜ëŠ” ê³³", "ëª¨í—˜ì´ ê¸°ë‹¤ë¦¬ëŠ” ì„¸ìƒ", "ì§„ì‹¤ì„ ì°¾ëŠ” ì—¬í–‰"

íƒœê·¸ë¼ì¸ë§Œ ë°˜í™˜í•´ì£¼ì„¸ìš”.
"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "ë‹¹ì‹ ì€ ì±… ë§ˆì¼€íŒ… ì „ë¬¸ê°€ìž…ë‹ˆë‹¤. ê°„ê²°í•˜ê³  ë§¤ë ¥ì ì¸ í•œêµ­ì–´ íƒœê·¸ë¼ì¸ì„ ë§Œë“œëŠ” ê²ƒì´ ì „ë¬¸ìž…ë‹ˆë‹¤."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "maxTokens": 50,
        "temperature": 0.7,
        "topP": 0.8,
    }
    
    try:
        response = requests.post(
            "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            tagline = result['result']['message']['content'].strip()
            # Clean up the tagline
            tagline = tagline.replace('"', '').replace("'", '').strip()
            return tagline if len(tagline) <= 20 else "ì±…ê³¼ í•¨ê»˜í•˜ëŠ” íŠ¹ë³„í•œ ì—¬í–‰"
        else:
            return "ì±…ê³¼ í•¨ê»˜í•˜ëŠ” íŠ¹ë³„í•œ ì—¬í–‰"
    except Exception as e:
        st.error(f"íƒœê·¸ë¼ì¸ ìƒì„± ì¤‘ ì˜¤ë¥˜: {e}")
        return "ì±…ê³¼ í•¨ê»˜í•˜ëŠ” íŠ¹ë³„í•œ ì—¬í–‰"

def fetch_unsplash_image(book_info, unsplash_access_key, api_key):
    """Fetch a contextually appropriate image from Unsplash based on book information"""
    if not unsplash_access_key:
        return None
    
    # Extract contextual keywords using AI
    primary_keyword = extract_search_keywords_from_book(book_info, api_key)
    
    # Create unique seed for this book to ensure different images for same genre
    title = book_info.get('bookname') or book_info.get('bookName', '')
    authors = book_info.get('authors') or book_info.get('author', '')
    isbn = book_info.get('isbn13') or book_info.get('isbn', '')
    
    # Create a unique seed based on book details
    book_seed = hashlib.md5(f"{title}{authors}{isbn}".encode()).hexdigest()[:8]
    
    # Add variety to search terms based on book seed
    variety_terms = [
        "aesthetic", "artistic", "beautiful", "elegant", "serene", 
        "dramatic", "peaceful", "inspiring", "creative", "atmospheric"
    ]
    
    # Select variety term based on book seed
    variety_index = int(book_seed, 16) % len(variety_terms)
    variety_term = variety_terms[variety_index]
    
    # Combine primary keyword with variety term
    search_query = f"{primary_keyword} {variety_term}"
    
    # Use book seed to determine page number for variety
    page_num = (int(book_seed[:4], 16) % 10) + 1
    
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": search_query,
        "client_id": unsplash_access_key,
        "per_page": 5,
        "page": page_num,
        "orientation": "landscape",
        "content_filter": "high",
        "order_by": "relevant"
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                # Select image based on book seed for consistency
                image_index = int(book_seed[4:6], 16) % len(data['results'])
                image_url = data['results'][image_index]['urls']['regular']
                return image_url
        return None
    except Exception as e:
        st.error(f"ì´ë¯¸ì§€ ê²€ìƒ‰ ì¤‘ ì˜¤ë¥˜: {e}")
        return None

def create_book_image_with_tagline(image_url, tagline, book_title):
    """Create an image with Korean tagline overlay using proper fonts"""
    try:
        # Download the image
        response = requests.get(image_url, timeout=30)
        if response.status_code != 200:
            return None
        
        # Open image with PIL
        img = Image.open(io.BytesIO(response.content))
        
        # Resize image to standard size
        img = img.resize((1200, 800), Image.Resampling.LANCZOS)
        
        # Create a semi-transparent overlay
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Create gradient overlay for better text visibility
        for y in range(img.height):
            alpha = int(180 * (y / img.height))  # Gradient from transparent to semi-opaque
            for x in range(img.width):
                overlay.putpixel((x, y), (0, 0, 0, alpha))
        
        # Composite the overlay onto the image
        img_with_overlay = Image.alpha_composite(img.convert('RGBA'), overlay)
        draw = ImageDraw.Draw(img_with_overlay)
        
        # Try to load Korean fonts in order of preference
        font_title = None
        font_tagline = None
        
        korean_fonts = [
            "malgun.ttf",  # Windows
            "NanumGothic.ttf",  # Common Korean font
            "AppleGothic.ttf",  # macOS
            "NotoSansCJK-Regular.ttc",  # Google Noto
            "DejaVuSans.ttf",  # Fallback
        ]
        
        for font_name in korean_fonts:
            try:
                font_title = ImageFont.truetype(font_name, 60)
                font_tagline = ImageFont.truetype(font_name, 45)
                break
            except (OSError, IOError):
                continue
        
        # If no TrueType font found, use default but larger
        if font_title is None:
            try:
                font_title = ImageFont.load_default()
                font_tagline = ImageFont.load_default()
                # Try to create a larger default font
                font_title = ImageFont.load_default()
                font_tagline = ImageFont.load_default()
            except:
                # Last resort - create basic font
                font_title = ImageFont.load_default()
                font_tagline = ImageFont.load_default()
        
        # Add book title at the top
        title_bbox = draw.textbbox((0, 0), book_title, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
        title_height = title_bbox[3] - title_bbox[1]
        title_x = (img.width - title_width) // 2
        title_y = 80
        
        # Add text shadow for better visibility
        shadow_offset = 3
        draw.text((title_x + shadow_offset, title_y + shadow_offset), book_title, 
                 fill=(0, 0, 0, 200), font=font_title)
        draw.text((title_x, title_y), book_title, fill=(255, 255, 255, 255), font=font_title)
        
        # Add tagline at the bottom
        tagline_bbox = draw.textbbox((0, 0), tagline, font=font_tagline)
        tagline_width = tagline_bbox[2] - tagline_bbox[0]
        tagline_height = tagline_bbox[3] - tagline_bbox[1]
        tagline_x = (img.width - tagline_width) // 2
        tagline_y = img.height - tagline_height - 100
        
        # Add text shadow for tagline
        draw.text((tagline_x + shadow_offset, tagline_y + shadow_offset), tagline, 
                 fill=(0, 0, 0, 200), font=font_tagline)
        draw.text((tagline_x, tagline_y), tagline, fill=(255, 255, 255, 255), font=font_tagline)
        
        # Add decorative border
        border_width = 8
        draw.rectangle([border_width//2, border_width//2, 
                       img.width - border_width//2, img.height - border_width//2], 
                      outline=(255, 255, 255, 150), width=border_width)
        
        # Convert back to RGB
        final_img = img_with_overlay.convert('RGB')
        
        # Convert to base64 for display in Streamlit
        buffer = io.BytesIO()
        final_img.save(buffer, format='JPEG', quality=90)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str
    except Exception as e:
        st.error(f"ì´ë¯¸ì§€ ìƒì„± ì¤‘ ì˜¤ë¥˜: {e}")
        return None

def generate_and_display_book_image(book_info, unsplash_key, hyperclova_key):
    """Generate and display book image with tagline"""
    with st.spinner('ì±…ì˜ ë‚´ìš©ì„ ë¶„ì„í•˜ê³  ë§žì¶¤ ì´ë¯¸ì§€ë¥¼ ìƒì„±í•˜ê³  ìžˆìŠµë‹ˆë‹¤...'):
        # Generate tagline
        tagline = generate_book_tagline(book_info, hyperclova_key)
        
        # Fetch contextually appropriate image from Unsplash
        image_url = fetch_unsplash_image(book_info, unsplash_key, hyperclova_key)
        
        if image_url:
            # Create image with tagline
            book_title = book_info.get('bookname') or book_info.get('bookName', 'ì±…')
            img_base64 = create_book_image_with_tagline(image_url, tagline, book_title)
            
            if img_base64:
                st.markdown("### ðŸ“¸ ìƒì„±ëœ ì±… ì´ë¯¸ì§€")
                st.image(f"data:image/jpeg;base64,{img_base64}", caption=f"íƒœê·¸ë¼ì¸: {tagline}")
                
                # Show the search context used
                search_keyword = extract_search_keywords_from_book(book_info, hyperclova_key)
                st.info(f"ì´ë¯¸ì§€ ê²€ìƒ‰ í‚¤ì›Œë“œ: {search_keyword}")
                
                # Download button
                st.download_button(
                    label="ì´ë¯¸ì§€ ë‹¤ìš´ë¡œë“œ",
                    data=base64.b64decode(img_base64),
                    file_name=f"{book_title}_image.jpg",
                    mime="image/jpeg"
                )
            else:
                st.error("ì´ë¯¸ì§€ ìƒì„±ì— ì‹¤íŒ¨í–ˆìŠµë‹ˆë‹¤.")
        else:
            st.error("ì ì ˆí•œ ì´ë¯¸ì§€ë¥¼ ì°¾ì„ ìˆ˜ ì—†ìŠµë‹ˆë‹¤.")


add_custom_css()

def display_liked_book_card(book, index):
    """Display a liked book card with a remove (cross) button using MongoDB."""
    info = book if isinstance(book, dict) else book.get("doc", {})
    with st.container():
        st.markdown('<div class="book-card" style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px;">', unsafe_allow_html=True)
        cols = st.columns([1, 3])
        with cols[0]:
            image_url = info.get("bookImageURL", "")
            if image_url:
                st.image(image_url, width=120)
            else:
                st.markdown("""
                <div style="width: 100px; height: 150px; background: linear-gradient(135deg, #2c3040, #363c4e); 
                            display: flex; align-items: center; justify-content: center; border-radius: 5px;">
                    <span style="color: #b3b3cc;">No Image</span>
                </div>
                """, unsafe_allow_html=True)
        with cols[1]:
            title = info.get('bookname') or info.get('bookName', 'ì œëª© ì—†ìŒ')
            authors = info.get('authors') or info.get('author', 'ì €ìž ì—†ìŒ')
            publisher = info.get('publisher', 'ì¶œíŒì‚¬ ì—†ìŒ')
            year = info.get('publication_year') or info.get('publicationYear', 'ì—°ë„ ì—†ìŒ')
            loan_count = info.get('loan_count') or info.get('loanCount', 0)
            isbn13 = info.get('isbn13') or info.get('isbn', 'unknown')
            st.markdown(f"""
            <div style="padding-left: 10px;">
                <div style="font-size: 1.2em; font-weight: bold; color: #333; margin-bottom: 8px;">{title}</div>
                <div style="margin-bottom: 4px;"><strong>Author:</strong> {authors}</div>
                <div style="margin-bottom: 4px;"><strong>Publisher:</strong> {publisher}</div>
                <div style="margin-bottom: 4px;"><strong>Year:</strong> {year}</div>
                <div style="margin-bottom: 8px;"><strong>Loan Count:</strong> {loan_count}</div>
            </div>
            """, unsafe_allow_html=True)
            btn_col1, btn_col2 = st.columns([3, 1])
            with btn_col1:
                if st.button(f"Tell me more about this book", key=f"details_liked_{isbn13}_{index}"):
                    st.session_state.selected_book = info
                    st.session_state.app_stage = "discuss_book"
                    st.rerun()
            with btn_col2:
                # Remove (cross) button
                if st.button("âŒ", key=f"remove_{isbn13}_{index}", help="Remove from My Library"):
                    unlike_book_for_user(st.session_state.username, isbn13)
                    st.success("Removed from your library!")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# Add after MongoDB client initialization
def get_user_library_collection():
    client = st.session_state.db_client  # Already set in login.py
    db = client["Login_Credentials"]
    return db["user_libraries"]

def like_book_for_user(username, book_info):
    user_library = get_user_library_collection()
    isbn = book_info.get("isbn13")
    if not isbn:
        return False
    # First, try to add to existing document
    result = user_library.update_one(
        {"username": username},
        {"$addToSet": {"liked_books": book_info}}
    )
    # If no document was modified, create one with an empty array and add the book
    if result.matched_count == 0:
        user_library.update_one(
            {"username": username},
            {"$set": {"liked_books": [book_info], "username": username}},
            upsert=True
        )
    return True

def get_liked_books(username):
    user_library = get_user_library_collection()
    doc = user_library.find_one({"username": username})
    return doc.get("liked_books", []) if doc else []

def unlike_book_for_user(username, isbn):
    user_library = get_user_library_collection()
    user_library.update_one(
        {"username": username},
        {"$pull": {"liked_books": {"isbn13": isbn}}}
    )

def display_message(message):
    if message["role"] != "system":
        if message["role"] == "assistant":
            avatar = "AI"
            avatar_class = "assistant-avatar"
            message_class = "assistant-message"
            
            if "í•œêµ­ì–´ ë‹µë³€:" in message["content"]:
                parts = message["content"].split("í•œêµ­ì–´ ë‹µë³€:", 1)
                english_part = parts[0].strip()
                korean_part = parts[1].strip() if len(parts) > 1 else ""
                
                st.markdown(f"""
                <div class="message-with-avatar">
                    <div class="message-avatar {avatar_class}">{avatar}</div>
                    <div class="chat-message {message_class}">
                        {english_part}
                        <div class="korean-text">
                            <span class="korean-label">í•œêµ­ì–´ ë‹µë³€:</span><br>
                            {korean_part}
                        </div>
                        <div class="message-timestamp">Now</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message-with-avatar">
                    <div class="message-avatar {avatar_class}">{avatar}</div>
                    <div class="chat-message {message_class}">
                        {message["content"]}
                        <div class="message-timestamp">Now</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            avatar = "You"
            avatar_class = "user-avatar"
            message_class = "user-message"
            
            st.markdown(f"""
            <div class="message-with-avatar">
                <div class="message-avatar {avatar_class}">{avatar}</div>
                <div class="chat-message {message_class}">
                    {message["content"]}
                    <div class="message-timestamp">Now</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def call_hyperclova_api(messages, api_key):
    """Helper function to call HyperCLOVA API with correct headers"""
    try:
        endpoint = "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": messages,
            "maxTokens": 1024,
            "temperature": 0.7,
            "topP": 0.8,
        }
        
        response = requests.post(endpoint, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result['result']['message']['content']
        else:
            st.error(f"Error connecting to HyperCLOVA API: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to HyperCLOVA API: {e}")
        return None

def display_book_card(book, index):
    """Display a book card with like and image functionality, using MongoDB for liked books."""
    # Handle both old format (direct keys) and new format (nested in 'doc')
    if "doc" in book:
        info = book["doc"]
    else:
        info = book

    with st.container():
        st.markdown('<div class="book-card" style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px;">', unsafe_allow_html=True)
        cols = st.columns([1, 3])
        with cols[0]:
            image_url = info.get("bookImageURL", "")
            if image_url:
                st.image(image_url, width=120)
            else:
                st.markdown("""
                <div style="width: 100px; height: 150px; background: linear-gradient(135deg, #2c3040, #363c4e); 
                            display: flex; align-items: center; justify-content: center; border-radius: 5px;">
                    <span style="color: #b3b3cc;">No Image</span>
                </div>
                """, unsafe_allow_html=True)
        with cols[1]:
            title = info.get('bookname') or info.get('bookName', 'ì œëª© ì—†ìŒ')
            authors = info.get('authors') or info.get('author', 'ì €ìž ì—†ìŒ')
            publisher = info.get('publisher', 'ì¶œíŒì‚¬ ì—†ìŒ')
            year = info.get('publication_year') or info.get('publicationYear', 'ì—°ë„ ì—†ìŒ')
            loan_count = info.get('loan_count') or info.get('loanCount', 0)
            isbn13 = info.get('isbn13') or info.get('isbn', 'unknown')

            st.markdown(f"""
            <div style="padding-left: 10px;">
                <div style="font-size: 1.2em; font-weight: bold; color: #333; margin-bottom: 8px;">{title}</div>
                <div style="margin-bottom: 4px;"><strong>ì €ìž:</strong> {authors}</div>
                <div style="margin-bottom: 4px;"><strong>ì¶œíŒì‚¬:</strong> {publisher}</div>
                <div style="margin-bottom: 4px;"><strong>ì¶œê°„ë…„ë„:</strong> {year}</div>
                <div style="margin-bottom: 8px;"><strong>ëŒ€ì¶œ íšŸìˆ˜:</strong> {loan_count}</div>
            </div>
            """, unsafe_allow_html=True)

            btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 1])
            with btn_col1:
                if st.button(f"ì´ ì±…ì— ëŒ€í•´ ë” ì•Œì•„ë³´ê¸°", key=f"details_{isbn13}_{index}"):
                    st.session_state.selected_book = info
                    st.session_state.app_stage = "discuss_book"
                    st.rerun()
            with btn_col2:
                # Check if this book is already liked
                liked_books = get_liked_books(st.session_state.username)
                already_liked = any((b.get("isbn13") or b.get("isbn")) == isbn13 for b in liked_books)
                if already_liked:
                    st.button("â¤ï¸", key=f"liked_{isbn13}_{index}", help="ë‚´ ì„œìž¬ì— ì¶”ê°€ë¨", disabled=True)
                else:
                    if st.button("â¤ï¸", key=f"like_{isbn13}_{index}", help="ë‚´ ì„œìž¬ì— ì¶”ê°€"):
                        # Store the book in MongoDB with consistent ISBN field
                        book_data = info.copy()
                        book_data['isbn13'] = isbn13
                        like_book_for_user(st.session_state.username, book_data)
                        st.success("ì„œìž¬ì— ì¶”ê°€ë˜ì—ˆìŠµë‹ˆë‹¤!")
                        st.rerun()
            with btn_col3:
                # Image generation button
                if st.button("ðŸ–¼ï¸", key=f"image_{isbn13}_{index}", help="ë§žì¶¤ ì´ë¯¸ì§€ ìƒì„±"):
                    if st.session_state.get('unsplash_api_key') and st.session_state.api_key:
                        generate_and_display_book_image(info, st.session_state.unsplash_api_key, st.session_state.api_key)
                    else:
                        st.error("ì´ë¯¸ì§€ ìƒì„±ì„ ìœ„í•´ Unsplash API í‚¤ì™€ HyperCLOVA API í‚¤ê°€ í•„ìš”í•©ë‹ˆë‹¤.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- Load JSON files ---
@st.cache_resource
def load_dtl_kdc_json():
    """Load only the detailed KDC JSON file"""
    with open("dtl_kdc.json", encoding="utf-8") as f:
        dtl_kdc_dict = json.load(f)
    return dtl_kdc_dict

dtl_kdc_dict = load_dtl_kdc_json()

# --- Enhanced HyperCLOVA API Integration ---
def extract_keywords_with_hyperclova(user_input, api_key, dtl_kdc_dict):
    """Extract and match the most appropriate DTL KDC code using HyperCLOVA with two-step process"""
    if not api_key:
        return find_best_dtl_code_fallback(user_input, dtl_kdc_dict)
    
    # First attempt - exact keyword matching
    categories_list = []
    for code, label in dtl_kdc_dict.items():
        categories_list.append(f"- {code}: {label}")
    
    categories_text = "\n".join(categories_list)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # First prompt - look for exact keywords
    prompt_exact = f"""
ë‹¤ìŒì€ ì „ì²´ ë„ì„œ ë¶„ë¥˜ ì½”ë“œ ëª©ë¡ìž…ë‹ˆë‹¤:
{categories_text}

ì‚¬ìš©ìž ìž…ë ¥: "{user_input}"

ìœ„ì˜ ì „ì²´ ëª©ë¡ì—ì„œ ì‚¬ìš©ìž ìž…ë ¥ê³¼ ì •í™•ížˆ ì¼ì¹˜í•˜ëŠ” í‚¤ì›Œë“œë‚˜ ë¶„ë¥˜ëª…ì„ ì°¾ì•„ì£¼ì„¸ìš”.
ì˜ˆë¥¼ ë“¤ì–´:
- "ì˜ë¬¸í•™" â†’ ì˜ë¯¸ë¬¸í•™ ê´€ë ¨ ì½”ë“œ
- "ì—­ì‚¬" â†’ ì—­ì‚¬ ê´€ë ¨ ì½”ë“œ  
- "ì†Œì„¤" â†’ ì†Œì„¤ ê´€ë ¨ ì½”ë“œ
- "ì² í•™" â†’ ì² í•™ ê´€ë ¨ ì½”ë“œ

ì •í™•í•œ ì¼ì¹˜ê°€ ìžˆìœ¼ë©´ í•´ë‹¹ ì½”ë“œë²ˆí˜¸ë§Œ ë°˜í™˜í•˜ì„¸ìš”. ì •í™•í•œ ì¼ì¹˜ê°€ ì—†ìœ¼ë©´ "NO_EXACT_MATCH"ë¥¼ ë°˜í™˜í•˜ì„¸ìš”.
"""
    
    data_exact = {
        "messages": [
            {
                "role": "system",
                "content": "ë‹¹ì‹ ì€ ë„ì„œ ë¶„ë¥˜ ì „ë¬¸ê°€ìž…ë‹ˆë‹¤. ì „ì²´ ë¶„ë¥˜ ëª©ë¡ì—ì„œ ì •í™•í•œ í‚¤ì›Œë“œ ì¼ì¹˜ë¥¼ ì°¾ì•„ ì½”ë“œë²ˆí˜¸ë§Œ ë°˜í™˜í•©ë‹ˆë‹¤."
            },
            {
                "role": "user", 
                "content": prompt_exact
            }
        ],
        "maxTokens": 50,
        "temperature": 0.1,
        "topP": 0.5,
    }
    
    try:
        # First API call - exact matching
        response = requests.post(
            "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003",
            headers=headers,
            json=data_exact,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            extracted_code = result['result']['message']['content'].strip()
            extracted_code = extracted_code.replace('"', '').replace("'", '').strip()
            
            # If exact match found and exists in dictionary
            if extracted_code != "NO_EXACT_MATCH" and extracted_code in dtl_kdc_dict:
                return extracted_code, dtl_kdc_dict[extracted_code]
            
            # If no exact match, try second attempt with similarity
            prompt_similar = f"""
ì‚¬ìš©ìž ìž…ë ¥: "{user_input}"

ë‹¤ìŒì€ ì‚¬ìš©í•  ìˆ˜ ìžˆëŠ” ë„ì„œ ë¶„ë¥˜ ì½”ë“œë“¤ìž…ë‹ˆë‹¤:
{categories_text}

ì •í™•í•œ ì¼ì¹˜ê°€ ì—†ìœ¼ë¯€ë¡œ, ì‚¬ìš©ìž ìž…ë ¥ì˜ ì˜ë¯¸ì™€ ê°€ìž¥ ìœ ì‚¬í•œ ë¶„ë¥˜ ì½”ë“œë¥¼ ì°¾ì•„ì£¼ì„¸ìš”.
ì˜ë¯¸ìƒ ì—°ê´€ì„±ì„ ê³ ë ¤í•˜ì—¬ ê°€ìž¥ ì ì ˆí•œ ì½”ë“œë¥¼ ì„ íƒí•˜ì„¸ìš”.

ì˜ˆë¥¼ ë“¤ì–´:
- "ì±… ì¶”ì²œ" â†’ ì¼ë°˜ì ì¸ ë¬¸í•™ì´ë‚˜ ì´ë¥˜ ê´€ë ¨ ì½”ë“œ
- "ê²½ì œ ê´€ë ¨" â†’ ê²½ì œí•™ ê´€ë ¨ ì½”ë“œ
- "ê±´ê°•" â†’ ì˜í•™ì´ë‚˜ ê±´ê°• ê´€ë ¨ ì½”ë“œ
- "ìš”ë¦¬" â†’ ìš”ë¦¬, ìŒì‹ ê´€ë ¨ ì½”ë“œ

ê°€ìž¥ ìœ ì‚¬í•œ ì½”ë“œë²ˆí˜¸ë§Œ ë°˜í™˜í•˜ì„¸ìš”.
"""
            
            data_similar = {
                "messages": [
                    {
                        "role": "system",
                        "content": "ë‹¹ì‹ ì€ ë„ì„œ ë¶„ë¥˜ ì „ë¬¸ê°€ìž…ë‹ˆë‹¤. ì˜ë¯¸ì  ìœ ì‚¬ì„±ì„ ë°”íƒ•ìœ¼ë¡œ ê°€ìž¥ ì ì ˆí•œ ë¶„ë¥˜ ì½”ë“œë¥¼ ì°¾ì•„ ë°˜í™˜í•©ë‹ˆë‹¤."
                    },
                    {
                        "role": "user", 
                        "content": prompt_similar
                    }
                ],
                "maxTokens": 50,
                "temperature": 0.3,
                "topP": 0.7,
            }
            
            # Second API call - similarity matching
            response2 = requests.post(
                "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003",
                headers=headers,
                json=data_similar,
                timeout=30
            )
            
            if response2.status_code == 200:
                result2 = response2.json()
                similar_code = result2['result']['message']['content'].strip()
                similar_code = similar_code.replace('"', '').replace("'", '').strip()
                
                if similar_code in dtl_kdc_dict:
                    return similar_code, dtl_kdc_dict[similar_code]
                else:
                    # Try to find partial matches
                    return find_best_dtl_code_fallback(user_input, dtl_kdc_dict, similar_code)
            else:
                return find_best_dtl_code_fallback(user_input, dtl_kdc_dict)
        else:
            st.warning(f"HyperCLOVA API error: {response.status_code}")
            return find_best_dtl_code_fallback(user_input, dtl_kdc_dict)
            
    except Exception as e:
        st.warning(f"Keyword extraction failed: {e}")
        return find_best_dtl_code_fallback(user_input, dtl_kdc_dict)

def find_best_dtl_code_fallback(user_query, dtl_kdc_dict, ai_suggested_code=None):
    """Fallback method to find the best matching DTL KDC code"""
    best_score = 0
    best_code = None
    best_label = ""
    
    # If AI suggested a code but it wasn't exact, try to find similar codes
    if ai_suggested_code:
        for code, label in dtl_kdc_dict.items():
            if ai_suggested_code in code or code in ai_suggested_code:
                return code, label
    
    # Original similarity matching
    for code, label in dtl_kdc_dict.items():
        # Check similarity with the label
        score = SequenceMatcher(None, user_query.lower(), label.lower()).ratio()
        
        # Also check if any word from user query is in the label
        user_words = user_query.lower().split()
        for word in user_words:
            if len(word) > 1 and word in label.lower():
                score += 0.3  # Boost score for word matches
        
        if score > best_score:
            best_score = score
            best_code = code
            best_label = label
    
    return best_code, best_label if best_score > 0.2 else (None, None)

def get_dtl_kdc_code(user_query, api_key=None):
    """Get DTL KDC code using HyperCLOVA or fallback method"""
    if api_key:
        try:
            code, label = extract_keywords_with_hyperclova(user_query, api_key, dtl_kdc_dict)
            if code and label:
                st.info(f"Found category: {label} (Code: {code})")
                return code, label
        except Exception as e:
            st.warning(f"HyperCLOVA extraction failed, using fallback: {e}")
    
    # Fallback to similarity matching
    code, label = find_best_dtl_code_fallback(user_query, dtl_kdc_dict)
    if code and label:
        st.info(f"Found category: {label} (Code: {code})")
        return code, label
    
    return None, None

# --- Query library API for books by DTL KDC code ---
def get_books_by_dtl_kdc(dtl_kdc_code, auth_key, page_no=1, page_size=10):
    """Get books using DTL KDC code"""
    url = "http://data4library.kr/api/loanItemSrch"
    params = {
        "authKey": auth_key,
        "startDt": "2000-01-01",
        "endDt": datetime.now().strftime("%Y-%m-%d"),
        "format": "json",
        "pageNo": page_no,
        "pageSize": page_size,
        "dtl_kdc": dtl_kdc_code  # Use dtl_kdc parameter
    }
    
    try:
        r = requests.get(url, params=params)
        if r.status_code == 200:
            response_data = r.json()
            
            # Check if response has the expected structure
            if "response" in response_data:
                docs = response_data["response"].get("docs", [])
                
                # Handle case where docs might be a single dict instead of list
                if isinstance(docs, dict):
                    docs = [docs]
                elif not isinstance(docs, list):
                    return []
                
                # Extract and clean book data
                books = []
                for doc in docs:
                    # Handle nested 'doc' structure if it exists
                    if "doc" in doc:
                        book_data = doc["doc"]
                    else:
                        book_data = doc
                    
                    # Extract book information with fallback values
                    book_info = {
                        "bookname": book_data.get("bookname", book_data.get("bookName", "Unknown Title")),
                        "authors": book_data.get("authors", book_data.get("author", "Unknown Author")),
                        "publisher": book_data.get("publisher", "Unknown Publisher"),
                        "publication_year": book_data.get("publication_year", book_data.get("publicationYear", "Unknown Year")),
                        "isbn13": book_data.get("isbn13", book_data.get("isbn", "")),
                        "loan_count": int(book_data.get("loan_count", book_data.get("loanCount", 0))),
                        "bookImageURL": book_data.get("bookImageURL", "")
                    }
                    books.append(book_info)
                
                # Sort by loan count (descending)
                books = sorted(books, key=lambda x: x["loan_count"], reverse=True)
                return books
            else:
                st.error(f"Unexpected API response structure: {response_data}")
                return []
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return []
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse API response: {e}")
        return []
    except Exception as e:
        st.error(f"Error processing API response: {e}")
        return []
    
    return []

# --- Sidebar (as provided) ---
def setup_sidebar():
    with st.sidebar:
        if st.button("ì¢‹ì•„í•˜ëŠ” ì±…ë“¤"):
            st.session_state.app_stage = "show_liked_books"
            st.rerun()

        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3 style="background: linear-gradient(90deg, #3b2314, #221409);
                      -webkit-background-clip: text;
                      -webkit-text-fill-color: transparent;
                      font-weight: 700;">
                API ì„¤ì •
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # API Keys section
        with st.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            
            # HyperCLOVA API Key
            hyperclova_api_key = st.text_input("HyperCLOVA API í‚¤ë¥¼ ìž…ë ¥í•˜ì„¸ìš”", 
                                              type="password", 
                                              value=st.session_state.api_key)
            st.session_state.api_key = hyperclova_api_key
            
            # Library API Key
            library_api_key = st.text_input("ë„ì„œê´€ API í‚¤ë¥¼ ìž…ë ¥í•˜ì„¸ìš”", 
                                            type="password", 
                                            value=st.session_state.library_api_key)
            st.session_state.library_api_key = library_api_key
            
            # Unsplash API Key
            unsplash_api_key = st.text_input("Unsplash API í‚¤ë¥¼ ìž…ë ¥í•˜ì„¸ìš”", 
                                            type="password", 
                                            value=st.session_state.get('unsplash_api_key', ''))
            st.session_state.unsplash_api_key = unsplash_api_key
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Reset button
        if st.button("ë‹¤ì‹œ ì‹œìž‘í•˜ê¸° ðŸ’«"):
            st.session_state.messages = [
                {"role": "system", "content": "You are a helpful AI assistant specializing in book recommendations. For EVERY response, you must answer in BOTH English and Korean. First provide the complete answer in English, then provide 'í•œêµ­ì–´ ë‹µë³€:' followed by the complete Korean translation of your answer."}
            ]
            st.session_state.app_stage = "welcome"
            st.session_state.user_genre = ""
            st.session_state.user_age = ""
            st.session_state.selected_book = None
            st.session_state.showing_books = False
            st.rerun()
        
        st.markdown("""
        <div style="text-align: center; margin-top: 30px; padding: 10px;">
            <p style="color: #b3b3cc; font-size: 0.8rem;">
                HyperCLOVA X, í•œêµ­ ë„ì„œê´€ API & Unsplashë¡œ êµ¬ë™
            </p>
        </div>
        """, unsafe_allow_html=True)

# --- Process follow-up questions with HyperCLOVA ---
def process_followup_with_hyperclova(user_input, api_key):
    """Process follow-up questions using HyperCLOVA API"""
    if not api_key:
        return "Please provide your HyperCLOVA API key in the sidebar to get detailed responses.\n\ní•œêµ­ì–´ ë‹µë³€: ìžì„¸í•œ ë‹µë³€ì„ ë°›ìœ¼ë ¤ë©´ ì‚¬ì´ë“œë°”ì—ì„œ HyperCLOVA API í‚¤ë¥¼ ì œê³µí•´ ì£¼ì„¸ìš”."
    
    # Create context from previous messages
    conversation_context = ""
    recent_messages = st.session_state.messages[-5:]  # Get last 5 messages for context
    for msg in recent_messages:
        if msg["role"] != "system":
            conversation_context += f"{msg['role']}: {msg['content']}\n"
    
    prompt = f"""
ì´ì „ ëŒ€í™” ë‚´ìš©:
{conversation_context}

ì‚¬ìš©ìžì˜ ìƒˆë¡œìš´ ì§ˆë¬¸: "{user_input}"

ìœ„ì˜ ë§¥ë½ì„ ê³ ë ¤í•˜ì—¬ ì‚¬ìš©ìžì˜ ì§ˆë¬¸ì— ëŒ€í•´ ë„ì›€ì´ ë˜ëŠ” ë‹µë³€ì„ í•´ì£¼ì„¸ìš”. 
ë§Œì•½ ìƒˆë¡œìš´ ë„ì„œ ì¶”ì²œì„ ìš”ì²­í•˜ëŠ” ê²ƒ ê°™ë‹¤ë©´, êµ¬ì²´ì ì¸ ìž¥ë¥´ë‚˜ ì£¼ì œë¥¼ ì œì‹œí•´ì£¼ì„¸ìš”.

ë‹µë³€ì€ ì˜ì–´ì™€ í•œêµ­ì–´ ëª¨ë‘ë¡œ ì œê³µí•˜ë˜, ë¨¼ì € ì˜ì–´ë¡œ ì™„ì „í•œ ë‹µë³€ì„ í•˜ê³ , 
ê·¸ ë‹¤ìŒ "í•œêµ­ì–´ ë‹µë³€:" ì´í›„ì— í•œêµ­ì–´ ë²ˆì—­ì„ ì œê³µí•˜ì„¸ìš”.
"""
    
    messages = [
        {
            "role": "system",
            "content": "ë‹¹ì‹ ì€ ë„ì„œ ì¶”ì²œ ì „ë¬¸ê°€ìž…ë‹ˆë‹¤. ì‚¬ìš©ìžì™€ì˜ ëŒ€í™” ë§¥ë½ì„ ì´í•´í•˜ê³  ë„ì›€ì´ ë˜ëŠ” ë‹µë³€ì„ ì œê³µí•©ë‹ˆë‹¤. í•­ìƒ ì˜ì–´ì™€ í•œêµ­ì–´ë¡œ ë‹µë³€í•˜ì„¸ìš”."
        },
        {
            "role": "user", 
            "content": prompt
        }
    ]
    
    return call_hyperclova_api(messages, api_key)

def generate_book_introduction(book, api_key):
    """Generate an introduction about the book when first selected"""
    title = book.get('bookname') or book.get('bookName', 'Unknown Title')
    authors = book.get('authors') or book.get('author', 'Unknown Author')
    publisher = book.get('publisher', 'Unknown Publisher')
    year = book.get('publication_year') or book.get('publicationYear', 'Unknown Year')
    loan_count = book.get('loan_count') or book.get('loanCount', 0)
    
    if not api_key:
        return f"Let's discuss '{title}' by {authors}! This book was published by {publisher} in {year} and has been borrowed {loan_count} times, showing its popularity. What would you like to know about this book - its themes, plot, writing style, or would you like similar recommendations?\n\ní•œêµ­ì–´ ë‹µë³€: {authors}ì˜ '{title}'ì— ëŒ€í•´ ì´ì•¼ê¸°í•´ ë´…ì‹œë‹¤! ì´ ì±…ì€ {year}ë…„ì— {publisher}ì—ì„œ ì¶œê°„ë˜ì—ˆìœ¼ë©° {loan_count}ë²ˆ ëŒ€ì¶œë˜ì–´ ì¸ê¸°ë¥¼ ë³´ì—¬ì¤ë‹ˆë‹¤. ì´ ì±…ì— ëŒ€í•´ ë¬´ì—‡ì„ ì•Œê³  ì‹¶ìœ¼ì‹ ê°€ìš” - ì£¼ì œ, ì¤„ê±°ë¦¬, ë¬¸ì²´, ì•„ë‹ˆë©´ ë¹„ìŠ·í•œ ì¶”ì²œì„ ì›í•˜ì‹œë‚˜ìš”?"
    
    book_context = f"Book: {title} by {authors}, published by {publisher} in {year}, with {loan_count} loans"
    
    messages = [
        {
            "role": "system",
            "content": "You are a knowledgeable book expert. For EVERY response, answer in BOTH English and Korean. First provide complete English answer, then 'í•œêµ­ì–´ ë‹µë³€:' with Korean translation. Provide an engaging introduction about the book."
        },
        {
            "role": "user", 
            "content": f"Please provide an engaging introduction about this book: {book_context}. Talk about what makes this book interesting, its potential themes, and invite the user to ask questions about it. Keep it conversational and welcoming."
        }
    ]
    
    response = call_hyperclova_api(messages, api_key)
    if response:
        return response
    else:
        # Fallback if API fails
        return f"Let's explore '{title}' by {authors}! This book from {publisher} ({year}) has {loan_count} loans, indicating its appeal to readers. I'm here to discuss anything about this book - from plot details to thematic analysis. What aspect interests you most?\n\ní•œêµ­ì–´ ë‹µë³€: {authors}ì˜ '{title}'ì„ íƒí—˜í•´ ë´…ì‹œë‹¤! {publisher}({year})ì˜ ì´ ì±…ì€ {loan_count}ë²ˆì˜ ëŒ€ì¶œë¡œ ë…ìžë“¤ì—ê²Œ ì–´í•„í•˜ê³  ìžˆìŒì„ ë³´ì—¬ì¤ë‹ˆë‹¤. ì¤„ê±°ë¦¬ ì„¸ë¶€ì‚¬í•­ë¶€í„° ì£¼ì œ ë¶„ì„ê¹Œì§€ ì´ ì±…ì— ëŒ€í•œ ëª¨ë“  ê²ƒì„ ë…¼ì˜í•  ì¤€ë¹„ê°€ ë˜ì–´ ìžˆìŠµë‹ˆë‹¤. ì–´ë–¤ ì¸¡ë©´ì— ê°€ìž¥ ê´€ì‹¬ì´ ìžˆìœ¼ì‹ ê°€ìš”?"

def process_book_question(book, question, api_key, conversation_history):
    """Process specific questions about a book using HyperCLOVA with improved context handling"""
    if not api_key:
        return "Please provide your HyperCLOVA API key in the sidebar to get detailed responses about this book.\n\ní•œêµ­ì–´ ë‹µë³€: ì´ ì±…ì— ëŒ€í•œ ìžì„¸í•œ ë‹µë³€ì„ ë°›ìœ¼ë ¤ë©´ ì‚¬ì´ë“œë°”ì—ì„œ HyperCLOVA API í‚¤ë¥¼ ì œê³µí•´ ì£¼ì„¸ìš”."
    
    title = book.get('bookname') or book.get('bookName', 'Unknown Title')
    authors = book.get('authors') or book.get('author', 'Unknown Author')
    publisher = book.get('publisher', 'Unknown Publisher')
    year = book.get('publication_year') or book.get('publicationYear', 'Unknown Year')
    loan_count = book.get('loan_count') or book.get('loanCount', 0)
    
    # Build comprehensive conversation context
    context_string = ""
    if conversation_history:
        # Include more context - last 6 messages for better continuity
        recent_history = conversation_history[-6:] if len(conversation_history) >= 6 else conversation_history
        for msg in recent_history:
            role = "ì‚¬ìš©ìž" if msg["role"] == "user" else "AI"
            context_string += f"{role}: {msg['content']}\n\n"
    
    book_info = f"ì œëª©: '{title}', ì €ìž: {authors}, ì¶œíŒì‚¬: {publisher}, ì¶œê°„ë…„ë„: {year}, ì¸ê¸°ë„: {loan_count}íšŒ ëŒ€ì¶œ"
    
    # Enhanced prompt with better context integration
    enhanced_prompt = f"""
í˜„ìž¬ ë…¼ì˜ ì¤‘ì¸ ë„ì„œ ì •ë³´:
{book_info}

ì´ì „ ëŒ€í™” ë‚´ìš©:
{context_string}

ì‚¬ìš©ìžì˜ ìƒˆë¡œìš´ ì§ˆë¬¸: "{question}"

ìœ„ì˜ ë„ì„œì™€ ì´ì „ ëŒ€í™” ë§¥ë½ì„ ëª¨ë‘ ê³ ë ¤í•˜ì—¬ ì‚¬ìš©ìžì˜ ì§ˆë¬¸ì— ëŒ€í•´ ìƒì„¸í•˜ê³  ë„ì›€ì´ ë˜ëŠ” ë‹µë³€ì„ ì œê³µí•´ì£¼ì„¸ìš”.

ë‹µë³€ ì§€ì¹¨:
1. ì´ì „ ëŒ€í™”ì˜ ë§¥ë½ì„ ì°¸ê³ í•˜ì—¬ ì—°ì†ì„± ìžˆëŠ” ë‹µë³€ì„ ì œê³µí•˜ì„¸ìš”
2. ì±…ì˜ ë‚´ìš©, ì£¼ì œ, ë“±ìž¥ì¸ë¬¼, ë¬¸ì²´, ë¬¸í™”ì  ë°°ê²½ ë“±ì— ëŒ€í•´ êµ¬ì²´ì ìœ¼ë¡œ ì„¤ëª…í•˜ì„¸ìš”
3. í•„ìš”ì‹œ ìœ ì‚¬í•œ ì±… ì¶”ì²œë„ í¬í•¨í•˜ì„¸ìš”
4. ì˜ì–´ë¡œ ì™„ì „í•œ ë‹µë³€ì„ ë¨¼ì € ì œê³µí•˜ê³ , ê·¸ ë‹¤ìŒ "í•œêµ­ì–´ ë‹µë³€:" ì´í›„ì— í•œêµ­ì–´ ë²ˆì—­ì„ ì œê³µí•˜ì„¸ìš”

ë‹µë³€ì€ ìƒì„¸í•˜ê³  í†µì°°ë ¥ ìžˆê²Œ ìž‘ì„±í•´ì£¼ì„¸ìš”.
"""
    
    messages = [
        {
            "role": "system",
            "content": f"ë‹¹ì‹ ì€ '{title}' by {authors}ì— ëŒ€í•´ ë…¼ì˜í•˜ëŠ” ì§€ì‹ì´ í’ë¶€í•œ ë„ì„œ ì „ë¬¸ê°€ìž…ë‹ˆë‹¤. ì´ì „ ëŒ€í™”ì˜ ë§¥ë½ì„ ê¸°ì–µí•˜ê³  ì—°ì†ì„± ìžˆëŠ” ë‹µë³€ì„ ì œê³µí•©ë‹ˆë‹¤. ëª¨ë“  ë‹µë³€ì€ ì˜ì–´ì™€ í•œêµ­ì–´ ëª¨ë‘ë¡œ ì œê³µí•˜ë©°, ë¨¼ì € ì˜ì–´ë¡œ ì™„ì „í•œ ë‹µë³€ì„ í•˜ê³  ê·¸ ë‹¤ìŒ 'í•œêµ­ì–´ ë‹µë³€:'ìœ¼ë¡œ í•œêµ­ì–´ ë²ˆì—­ì„ ì œê³µí•©ë‹ˆë‹¤. ë„ì„œì˜ ì£¼ì œ, ì¤„ê±°ë¦¬ ìš”ì†Œ, ë“±ìž¥ì¸ë¬¼ ë¶„ì„, ë¬¸ì²´, ë¬¸í™”ì  ë§¥ë½, ìœ ì‚¬í•œ ë„ì„œ ì¶”ì²œ ë“±ì„ í¬í•¨í•œ ìƒì„¸í•˜ê³  í†µì°°ë ¥ ìžˆëŠ” ì •ë³´ë¥¼ ì œê³µí•©ë‹ˆë‹¤."
        },
        {
            "role": "user",
            "content": enhanced_prompt
        }
    ]
    
    try:
        response = call_hyperclova_api(messages, api_key)
        if response:
            return response
        else:
            return f"I'd be happy to continue our discussion about '{title}', but I'm having trouble connecting to the AI service right now. Could you try asking your question again?\n\ní•œêµ­ì–´ ë‹µë³€: '{title}'ì— ëŒ€í•œ ë…¼ì˜ë¥¼ ê³„ì†í•˜ê³  ì‹¶ì§€ë§Œ ì§€ê¸ˆ AI ì„œë¹„ìŠ¤ì— ì—°ê²°í•˜ëŠ” ë° ë¬¸ì œê°€ ìžˆìŠµë‹ˆë‹¤. ì§ˆë¬¸ì„ ë‹¤ì‹œ í•´ë³´ì‹œê² ì–´ìš”?"
    except Exception as e:
        st.error(f"Error processing question: {e}")
        return f"I encountered an error while processing your question about '{title}'. Please try rephrasing your question or check your API connection.\n\ní•œêµ­ì–´ ë‹µë³€: '{title}'ì— ëŒ€í•œ ì§ˆë¬¸ì„ ì²˜ë¦¬í•˜ëŠ” ì¤‘ ì˜¤ë¥˜ê°€ ë°œìƒí–ˆìŠµë‹ˆë‹¤. ì§ˆë¬¸ì„ ë‹¤ì‹œ í‘œí˜„í•˜ê±°ë‚˜ API ì—°ê²°ì„ í™•ì¸í•´ ì£¼ì„¸ìš”."

def main():
    # --- Initialize all session state variables before use ---
    if "unsplash_api_key" not in st.session_state:
        st.session_state.unsplash_api_key = ""
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    if "library_api_key" not in st.session_state:
        st.session_state.library_api_key = ""
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "system",
            "content": (
                "You are a friendly AI assistant specializing in book recommendations. "
                "Start by greeting and asking about favorite books/authors/genres/age. "
                "For EVERY response, answer in BOTH English and Korean. "
                "First provide complete English answer, then 'í•œêµ­ì–´ ë‹µë³€:' with Korean translation."
            )
        }]
    if "app_stage" not in st.session_state:
        st.session_state.app_stage = "welcome"
    if "books_data" not in st.session_state:
        st.session_state.books_data = []
    if "user_genre" not in st.session_state:
        st.session_state.user_genre = ""
    if "user_age" not in st.session_state:
        st.session_state.user_age = ""
    if "selected_book" not in st.session_state:
        st.session_state.selected_book = None
    if "showing_books" not in st.session_state:
        st.session_state.showing_books = False
    if "book_discussion_messages" not in st.session_state:
        st.session_state.book_discussion_messages = []
    if "book_intro_shown" not in st.session_state:
        st.session_state.book_intro_shown = False

    setup_sidebar()

    st.markdown("<h1 style='text-align:center;'>ðŸ“š Book Wanderer / ì±…ë°©ëž‘ìž</h1>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;'>Discover your next favorite read with AI assistance in English and Korean</div>", unsafe_allow_html=True)
    st.markdown("---")

    # --- Chat history (only show non-book-specific messages in main flow) ---
    for msg in st.session_state.messages:
        if msg["role"] != "system" and not msg.get("book_context"):
            display_message(msg)

    # --- App stages ---
    if st.session_state.app_stage == "welcome":
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! Tell me about your favourite books, author, genre, or age group. You can describe what you're looking for in natural language.\n\ní•œêµ­ì–´ ë‹µë³€: ì•ˆë…•í•˜ì„¸ìš”! ì¢‹ì•„í•˜ëŠ” ì±…, ìž‘ê°€, ìž¥ë¥´ ë˜ëŠ” ì—°ë ¹ëŒ€ì— ëŒ€í•´ ë§ì”€í•´ ì£¼ì„¸ìš”. ìžì—°ìŠ¤ëŸ¬ìš´ ì–¸ì–´ë¡œ ì›í•˜ëŠ” ê²ƒì„ ì„¤ëª…í•´ ì£¼ì‹œë©´ ë©ë‹ˆë‹¤."
        })
        st.session_state.app_stage = "awaiting_user_input"
        st.rerun()

    elif st.session_state.app_stage == "awaiting_user_input":
        user_input = st.text_input("Tell me about your favorite genre, author, or book (in Korean or English):", key="user_open_input")
        if st.button("Send", key="send_open_input"):
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.app_stage = "process_user_input"
                st.rerun()

    elif st.session_state.app_stage == "process_user_input":
        user_input = st.session_state.messages[-1]["content"]
        
        # Only use Library API for book fetching, HyperCLOVA only for category matching
        dtl_code, dtl_label = get_dtl_kdc_code(user_input, st.session_state.api_key)
        
        if dtl_code and st.session_state.library_api_key:
            # Fetch books using the DTL KDC code (Library API only)
            books = get_books_by_dtl_kdc(dtl_code, st.session_state.library_api_key, page_no=1, page_size=20)
            
            if books:
                st.session_state.books_data = books
                
                # Generate AI response about the recommendations using HyperCLOVA
                if st.session_state.api_key:
                    ai_response = call_hyperclova_api([
                        {"role": "system", "content": "You are a helpful book recommendation assistant. For EVERY response, answer in BOTH English and Korean. First provide complete English answer, then 'í•œêµ­ì–´ ë‹µë³€:' with Korean translation."},
                        {"role": "user", "content": f"I found {len(books)} books in the {dtl_label} category. Tell me about this category and encourage me to explore these recommendations."}
                    ], st.session_state.api_key)
                    
                    if ai_response:
                        st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    else:
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": f"Great! I found {len(books)} excellent books in the {dtl_label} category. These recommendations are based on popularity and should match your interests perfectly. Take a look at the books below!\n\ní•œêµ­ì–´ ë‹µë³€: ì¢‹ìŠµë‹ˆë‹¤! {dtl_label} ì¹´í…Œê³ ë¦¬ì—ì„œ {len(books)}ê¶Œì˜ í›Œë¥­í•œ ì±…ì„ ì°¾ì•˜ìŠµë‹ˆë‹¤. ì´ ì¶”ì²œì€ ì¸ê¸°ë„ë¥¼ ë°”íƒ•ìœ¼ë¡œ í•˜ë©° ë‹¹ì‹ ì˜ ê´€ì‹¬ì‚¬ì™€ ì™„ë²½í•˜ê²Œ ì¼ì¹˜í•  ê²ƒìž…ë‹ˆë‹¤. ì•„ëž˜ ì±…ë“¤ì„ ì‚´íŽ´ë³´ì„¸ìš”!"
                        })
                
                st.session_state.app_stage = "show_recommendations"
            else:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "I couldn't find books in that specific category. Could you try describing your preferences differently? For example, mention specific genres like 'mystery novels', 'self-help books', or 'Korean literature'.\n\ní•œêµ­ì–´ ë‹µë³€: í•´ë‹¹ ì¹´í…Œê³ ë¦¬ì—ì„œ ì±…ì„ ì°¾ì„ ìˆ˜ ì—†ì—ˆìŠµë‹ˆë‹¤. ë‹¤ë¥¸ ë°©ì‹ìœ¼ë¡œ ì„ í˜¸ë„ë¥¼ ì„¤ëª…í•´ ì£¼ì‹œê² ì–´ìš”? ì˜ˆë¥¼ ë“¤ì–´ 'ì¶”ë¦¬ì†Œì„¤', 'ìžê¸°ê³„ë°œì„œ', 'í•œêµ­ë¬¸í•™'ê³¼ ê°™ì€ êµ¬ì²´ì ì¸ ìž¥ë¥´ë¥¼ ì–¸ê¸‰í•´ ì£¼ì„¸ìš”."
                })
                st.session_state.app_stage = "awaiting_user_input"
        else:
            missing_items = []
            if not dtl_code:
                missing_items.append("category matching")
            if not st.session_state.library_api_key:
                missing_items.append("Library API key")
            
            error_msg = f"Unable to process your request due to: {', '.join(missing_items)}. Please check your API configuration in the sidebar."
            korean_msg = f"ë‹¤ìŒ ì´ìœ ë¡œ ìš”ì²­ì„ ì²˜ë¦¬í•  ìˆ˜ ì—†ìŠµë‹ˆë‹¤: {', '.join(missing_items)}. ì‚¬ì´ë“œë°”ì—ì„œ API ì„¤ì •ì„ í™•ì¸í•´ ì£¼ì„¸ìš”."
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"{error_msg}\n\ní•œêµ­ì–´ ë‹µë³€: {korean_msg}"
            })
            st.session_state.app_stage = "awaiting_user_input"
        
        st.rerun()

    elif st.session_state.app_stage == "show_recommendations":
        st.markdown("### ðŸ“– Recommended Books for You")
        
        # Display books
        for i, book in enumerate(st.session_state.books_data[:10]):  # Show top 10 books
            display_book_card(book, i)
        
        # Chat input for follow-up questions
        user_followup = st.text_input("Ask me anything about these books or request different recommendations:", key="followup_input")
        if st.button("Send", key="send_followup"):
            if user_followup:
                st.session_state.messages.append({"role": "user", "content": user_followup})
                
                # Check if user wants new recommendations
                if any(keyword in user_followup.lower() for keyword in ['different', 'other', 'new', 'more', 'ë‹¤ë¥¸', 'ìƒˆë¡œìš´', 'ë”']):
                    st.session_state.app_stage = "process_user_input"
                else:
                    # Process as follow-up question using HyperCLOVA
                    response = process_followup_with_hyperclova(user_followup, st.session_state.api_key)
                    if response:
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    else:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "I'd be happy to help you with more information about these books or other recommendations. What specific aspect would you like to know more about?\n\ní•œêµ­ì–´ ë‹µë³€: ì´ ì±…ë“¤ì— ëŒ€í•œ ë” ë§Žì€ ì •ë³´ë‚˜ ë‹¤ë¥¸ ì¶”ì²œì— ëŒ€í•´ ê¸°êº¼ì´ ë„ì™€ë“œë¦¬ê² ìŠµë‹ˆë‹¤. ì–´ë–¤ êµ¬ì²´ì ì¸ ì¸¡ë©´ì— ëŒ€í•´ ë” ì•Œê³  ì‹¶ìœ¼ì‹ ê°€ìš”?"
                        })
                st.rerun()

    elif st.session_state.app_stage == "discuss_book":
        if st.session_state.selected_book:
            book = st.session_state.selected_book
            
            # Display selected book details
            st.markdown("### ðŸ“– Let's Talk About This Book")
            
            with st.container():
                cols = st.columns([1, 2])
                with cols[0]:
                    image_url = book.get("bookImageURL", "")
                    if image_url:
                        st.image(image_url, width=200)
                    else:
                        st.markdown("""
                        <div style="width: 150px; height: 200px; background: linear-gradient(135deg, #2c3040, #363c4e); 
                                    display: flex; align-items: center; justify-content: center; border-radius: 8px;">
                            <span style="color: #b3b3cc;">No Image</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                with cols[1]:
                    title = book.get('bookname') or book.get('bookName', 'Unknown Title')
                    authors = book.get('authors') or book.get('author', 'Unknown Author')
                    publisher = book.get('publisher', 'Unknown Publisher')
                    year = book.get('publication_year') or book.get('publicationYear', 'Unknown Year')
                    loan_count = book.get('loan_count') or book.get('loanCount', 0)
                    
                    st.markdown(f"""
                    <div style="padding: 20px;">
                        <h2 style="color: #2c3040; margin-bottom: 15px;">{title}</h2>
                        <div style="margin-bottom: 8px;"><strong>Author:</strong> {authors}</div>
                        <div style="margin-bottom: 8px;"><strong>Publisher:</strong> {publisher}</div>
                        <div style="margin-bottom: 8px;"><strong>Publication Year:</strong> {year}</div>
                        <div style="margin-bottom: 8px;"><strong>Popularity:</strong> {loan_count} loans</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Show introduction message when first entering book discussion
            if not st.session_state.book_intro_shown:
                intro_message = generate_book_introduction(book, st.session_state.api_key)
                st.session_state.book_discussion_messages.append({
                    "role": "assistant", 
                    "content": intro_message
                })
                st.session_state.book_intro_shown = True
                st.rerun()
            
            # Display chat history for this specific book
            for msg in st.session_state.book_discussion_messages:
                display_message(msg)
            
            # Chat input for book discussion with improved key management
            book_question = st.text_input(
                "Ask me anything about this book (plot, themes, similar books, etc.):", 
                key=f"book_discussion_input_{len(st.session_state.book_discussion_messages)}"
            )
            
            if st.button("Ask", key=f"ask_about_book_{len(st.session_state.book_discussion_messages)}"):
                if book_question:
                    # Add user message to book discussion
                    user_msg = {"role": "user", "content": book_question}
                    st.session_state.book_discussion_messages.append(user_msg)
                    
                    # Generate AI response about the book using HyperCLOVA
                    ai_response = process_book_question(
                        book, 
                        book_question, 
                        st.session_state.api_key,
                        st.session_state.book_discussion_messages
                    )
                    
                    assistant_msg = {"role": "assistant", "content": ai_response}
                    st.session_state.book_discussion_messages.append(assistant_msg)
                    
                    st.rerun()
            
            # Back to recommendations button
            if st.button("â† Back to Recommendations", key="back_to_recs"):
                # Clear book discussion messages and intro flag when going back
                st.session_state.book_discussion_messages = []
                st.session_state.book_intro_shown = False
                st.session_state.app_stage = "show_recommendations"
                st.rerun()

    elif st.session_state.app_stage == "show_liked_books":
        st.markdown("### â¤ï¸ My Library")
        
        if hasattr(st.session_state, 'username') and st.session_state.username:
            liked_books = get_liked_books(st.session_state.username)
            
            if liked_books:
                st.markdown(f"You have {len(liked_books)} books in your library:")
                for i, book in enumerate(liked_books):
                    display_liked_book_card(book, i)
            else:
                st.markdown("Your library is empty. Start exploring books to add them to your collection!")
                if st.button("Discover Books"):
                    st.session_state.app_stage = "welcome"
                    st.rerun()
        else:
            st.error("Please ensure you are logged in to view your library.")
        
        # Back to main app button
        if st.button("â† Back to Book Discovery", key="back_to_main"):
            st.session_state.app_stage = "show_recommendations" if st.session_state.books_data else "welcome"
            st.rerun()

if __name__ == "__main__":
    main()
