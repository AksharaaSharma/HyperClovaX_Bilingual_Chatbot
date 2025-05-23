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
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', '의', '와', '과', '에', '을', '를', '이', '가'}
        meaningful_words = [word for word in words if len(word) > 3 and word not in common_words]
        
        if meaningful_words:
            return meaningful_words[0]
        else:
            return "books"
    
    title = book_info.get('bookname') or book_info.get('bookName', '알 수 없는 제목')
    authors = book_info.get('authors') or book_info.get('author', '알 수 없는 저자')
    
    prompt = f"""
책 제목: "{title}"
저자: {authors}

이 책의 제목과 저자 정보를 분석하여, 이미지 검색에 가장 적합한 영어 키워드를 생성해주세요.

다음 지침을 따라주세요:
1. 책의 내용, 분위기, 주제를 추측하여 관련된 시각적 요소를 생각해보세요
2. 미리 정의된 카테고리를 사용하지 말고, 책의 고유한 특성을 반영하세요
3. 구체적이고 시각적인 영어 단어 하나만 반환하세요
4. 추상적 개념보다는 구체적인 이미지를 연상시키는 단어를 선택하세요

예시:
- 로맨스 소설 → "romance", "couple", "sunset", "flowers"
- 전쟁 소설 → "battlefield", "soldier", "ruins", "memorial"
- 과학 도서 → "laboratory", "research", "microscope", "discovery"
- 여행 에세이 → "journey", "landscape", "adventure", "exploration"
- 요리 책 → "kitchen", "ingredients", "cooking", "chef"

책의 특성을 가장 잘 표현하는 영어 키워드 하나만 반환하세요.
"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "당신은 책의 내용을 분석하여 시각적 이미지 검색에 적합한 키워드를 생성하는 전문가입니다. 미리 정의된 카테고리를 사용하지 않고, 각 책의 고유한 특성을 반영한 구체적인 키워드를 생성합니다."
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
        st.error(f"키워드 추출 중 오류: {e}")
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
주요 키워드: "{primary_keyword}"
책 제목: "{title}"

주요 키워드와 관련된 시각적 수식어를 2-3개 생성해주세요.
예시:
- "ocean" → "serene", "vast", "blue"
- "forest" → "mysterious", "green", "peaceful"
- "city" → "modern", "bustling", "urban"

영어 단어만 쉼표로 구분하여 반환하세요.
"""
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "시각적 수식어를 생성하는 전문가입니다."
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
        st.error(f"이미지 검색 중 오류: {e}")
        return None

def generate_book_tagline(book_info, api_key):
    """Generate a Korean tagline for the book using HyperCLOVA"""
    if not api_key:
        return "책과 함께하는 특별한 여행"  # Default tagline
    
    title = book_info.get('bookname') or book_info.get('bookName', '알 수 없는 제목')
    authors = book_info.get('authors') or book_info.get('author', '알 수 없는 저자')
    
    prompt = f"""
책 제목: "{title}"
저자: {authors}

이 책에 대한 매력적이고 간결한 한국어 태그라인을 만들어주세요.
태그라인은 10-15자 이내로 작성하고, 책의 분위기나 주제를 잘 표현해야 합니다.
예시: "사랑이 시작되는 곳", "모험이 기다리는 세상", "진실을 찾는 여행"

태그라인만 반환해주세요.
"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "당신은 책 마케팅 전문가입니다. 간결하고 매력적인 한국어 태그라인을 만드는 것이 전문입니다."
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
            return tagline if len(tagline) <= 20 else "책과 함께하는 특별한 여행"
        else:
            return "책과 함께하는 특별한 여행"
    except Exception as e:
        st.error(f"태그라인 생성 중 오류: {e}")
        return "책과 함께하는 특별한 여행"

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
        st.error(f"이미지 검색 중 오류: {e}")
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
        st.error(f"이미지 생성 중 오류: {e}")
        return None

def generate_and_display_book_image(book_info, unsplash_key, hyperclova_key):
    """Generate and display book image with tagline"""
    with st.spinner('책의 내용을 분석하고 맞춤 이미지를 생성하고 있습니다...'):
        # Generate tagline
        tagline = generate_book_tagline(book_info, hyperclova_key)
        
        # Fetch contextually appropriate image from Unsplash
        image_url = fetch_unsplash_image(book_info, unsplash_key, hyperclova_key)
        
        if image_url:
            # Create image with tagline
            book_title = book_info.get('bookname') or book_info.get('bookName', '책')
            img_base64 = create_book_image_with_tagline(image_url, tagline, book_title)
            
            if img_base64:
                st.markdown("### 📸 생성된 책 이미지")
                st.image(f"data:image/jpeg;base64,{img_base64}", caption=f"태그라인: {tagline}")
                
                # Show the search context used
                search_keyword = extract_search_keywords_from_book(book_info, hyperclova_key)
                st.info(f"이미지 검색 키워드: {search_keyword}")
                
                # Download button
                st.download_button(
                    label="이미지 다운로드",
                    data=base64.b64decode(img_base64),
                    file_name=f"{book_title}_image.jpg",
                    mime="image/jpeg"
                )
            else:
                st.error("이미지 생성에 실패했습니다.")
        else:
            st.error("적절한 이미지를 찾을 수 없습니다.")


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
            title = info.get('bookname') or info.get('bookName', '제목 없음')
            authors = info.get('authors') or info.get('author', '저자 없음')
            publisher = info.get('publisher', '출판사 없음')
            year = info.get('publication_year') or info.get('publicationYear', '연도 없음')
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
                if st.button("❌", key=f"remove_{isbn13}_{index}", help="Remove from My Library"):
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
            
            if "한국어 답변:" in message["content"]:
                parts = message["content"].split("한국어 답변:", 1)
                english_part = parts[0].strip()
                korean_part = parts[1].strip() if len(parts) > 1 else ""
                
                st.markdown(f"""
                <div class="message-with-avatar">
                    <div class="message-avatar {avatar_class}">{avatar}</div>
                    <div class="chat-message {message_class}">
                        {english_part}
                        <div class="korean-text">
                            <span class="korean-label">한국어 답변:</span><br>
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
            title = info.get('bookname') or info.get('bookName', '제목 없음')
            authors = info.get('authors') or info.get('author', '저자 없음')
            publisher = info.get('publisher', '출판사 없음')
            year = info.get('publication_year') or info.get('publicationYear', '연도 없음')
            loan_count = info.get('loan_count') or info.get('loanCount', 0)
            isbn13 = info.get('isbn13') or info.get('isbn', 'unknown')

            st.markdown(f"""
            <div style="padding-left: 10px;">
                <div style="font-size: 1.2em; font-weight: bold; color: #333; margin-bottom: 8px;">{title}</div>
                <div style="margin-bottom: 4px;"><strong>저자:</strong> {authors}</div>
                <div style="margin-bottom: 4px;"><strong>출판사:</strong> {publisher}</div>
                <div style="margin-bottom: 4px;"><strong>출간년도:</strong> {year}</div>
                <div style="margin-bottom: 8px;"><strong>대출 횟수:</strong> {loan_count}</div>
            </div>
            """, unsafe_allow_html=True)

            btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 1])
            with btn_col1:
                if st.button(f"이 책에 대해 더 알아보기", key=f"details_{isbn13}_{index}"):
                    st.session_state.selected_book = info
                    st.session_state.app_stage = "discuss_book"
                    st.rerun()
            with btn_col2:
                # Check if this book is already liked
                liked_books = get_liked_books(st.session_state.username)
                already_liked = any((b.get("isbn13") or b.get("isbn")) == isbn13 for b in liked_books)
                if already_liked:
                    st.button("❤️", key=f"liked_{isbn13}_{index}", help="내 서재에 추가됨", disabled=True)
                else:
                    if st.button("❤️", key=f"like_{isbn13}_{index}", help="내 서재에 추가"):
                        # Store the book in MongoDB with consistent ISBN field
                        book_data = info.copy()
                        book_data['isbn13'] = isbn13
                        like_book_for_user(st.session_state.username, book_data)
                        st.success("서재에 추가되었습니다!")
                        st.rerun()
            with btn_col3:
                # Image generation button
                if st.button("🖼️", key=f"image_{isbn13}_{index}", help="맞춤 이미지 생성"):
                    if st.session_state.get('unsplash_api_key') and st.session_state.api_key:
                        generate_and_display_book_image(info, st.session_state.unsplash_api_key, st.session_state.api_key)
                    else:
                        st.error("이미지 생성을 위해 Unsplash API 키와 HyperCLOVA API 키가 필요합니다.")
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
다음은 전체 도서 분류 코드 목록입니다:
{categories_text}

사용자 입력: "{user_input}"

위의 전체 목록에서 사용자 입력과 정확히 일치하는 키워드나 분류명을 찾아주세요.
예를 들어:
- "영문학" → 영미문학 관련 코드
- "역사" → 역사 관련 코드  
- "소설" → 소설 관련 코드
- "철학" → 철학 관련 코드

정확한 일치가 있으면 해당 코드번호만 반환하세요. 정확한 일치가 없으면 "NO_EXACT_MATCH"를 반환하세요.
"""
    
    data_exact = {
        "messages": [
            {
                "role": "system",
                "content": "당신은 도서 분류 전문가입니다. 전체 분류 목록에서 정확한 키워드 일치를 찾아 코드번호만 반환합니다."
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
사용자 입력: "{user_input}"

다음은 사용할 수 있는 도서 분류 코드들입니다:
{categories_text}

정확한 일치가 없으므로, 사용자 입력의 의미와 가장 유사한 분류 코드를 찾아주세요.
의미상 연관성을 고려하여 가장 적절한 코드를 선택하세요.

예를 들어:
- "책 추천" → 일반적인 문학이나 총류 관련 코드
- "경제 관련" → 경제학 관련 코드
- "건강" → 의학이나 건강 관련 코드
- "요리" → 요리, 음식 관련 코드

가장 유사한 코드번호만 반환하세요.
"""
            
            data_similar = {
                "messages": [
                    {
                        "role": "system",
                        "content": "당신은 도서 분류 전문가입니다. 의미적 유사성을 바탕으로 가장 적절한 분류 코드를 찾아 반환합니다."
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
        if st.button("좋아하는 책들"):
            st.session_state.app_stage = "show_liked_books"
            st.rerun()

        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3 style="background: linear-gradient(90deg, #3b2314, #221409);
                      -webkit-background-clip: text;
                      -webkit-text-fill-color: transparent;
                      font-weight: 700;">
                API 설정
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # API Keys section
        with st.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            
            # HyperCLOVA API Key
            hyperclova_api_key = st.text_input("HyperCLOVA API 키를 입력하세요", 
                                              type="password", 
                                              value=st.session_state.api_key)
            st.session_state.api_key = hyperclova_api_key
            
            # Library API Key
            library_api_key = st.text_input("도서관 API 키를 입력하세요", 
                                            type="password", 
                                            value=st.session_state.library_api_key)
            st.session_state.library_api_key = library_api_key
            
            # Unsplash API Key
            unsplash_api_key = st.text_input("Unsplash API 키를 입력하세요", 
                                            type="password", 
                                            value=st.session_state.get('unsplash_api_key', ''))
            st.session_state.unsplash_api_key = unsplash_api_key
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Reset button
        if st.button("다시 시작하기 💫"):
            st.session_state.messages = [
                {"role": "system", "content": "You are a helpful AI assistant specializing in book recommendations. For EVERY response, you must answer in BOTH English and Korean. First provide the complete answer in English, then provide '한국어 답변:' followed by the complete Korean translation of your answer."}
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
                HyperCLOVA X, 한국 도서관 API & Unsplash로 구동
            </p>
        </div>
        """, unsafe_allow_html=True)

# --- Process follow-up questions with HyperCLOVA ---
def process_followup_with_hyperclova(user_input, api_key):
    """Process follow-up questions using HyperCLOVA API"""
    if not api_key:
        return "Please provide your HyperCLOVA API key in the sidebar to get detailed responses.\n\n한국어 답변: 자세한 답변을 받으려면 사이드바에서 HyperCLOVA API 키를 제공해 주세요."
    
    # Create context from previous messages
    conversation_context = ""
    recent_messages = st.session_state.messages[-5:]  # Get last 5 messages for context
    for msg in recent_messages:
        if msg["role"] != "system":
            conversation_context += f"{msg['role']}: {msg['content']}\n"
    
    prompt = f"""
이전 대화 내용:
{conversation_context}

사용자의 새로운 질문: "{user_input}"

위의 맥락을 고려하여 사용자의 질문에 대해 도움이 되는 답변을 해주세요. 
만약 새로운 도서 추천을 요청하는 것 같다면, 구체적인 장르나 주제를 제시해주세요.

답변은 영어와 한국어 모두로 제공하되, 먼저 영어로 완전한 답변을 하고, 
그 다음 "한국어 답변:" 이후에 한국어 번역을 제공하세요.
"""
    
    messages = [
        {
            "role": "system",
            "content": "당신은 도서 추천 전문가입니다. 사용자와의 대화 맥락을 이해하고 도움이 되는 답변을 제공합니다. 항상 영어와 한국어로 답변하세요."
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
        return f"Let's discuss '{title}' by {authors}! This book was published by {publisher} in {year} and has been borrowed {loan_count} times, showing its popularity. What would you like to know about this book - its themes, plot, writing style, or would you like similar recommendations?\n\n한국어 답변: {authors}의 '{title}'에 대해 이야기해 봅시다! 이 책은 {year}년에 {publisher}에서 출간되었으며 {loan_count}번 대출되어 인기를 보여줍니다. 이 책에 대해 무엇을 알고 싶으신가요 - 주제, 줄거리, 문체, 아니면 비슷한 추천을 원하시나요?"
    
    book_context = f"Book: {title} by {authors}, published by {publisher} in {year}, with {loan_count} loans"
    
    messages = [
        {
            "role": "system",
            "content": "You are a knowledgeable book expert. For EVERY response, answer in BOTH English and Korean. First provide complete English answer, then '한국어 답변:' with Korean translation. Provide an engaging introduction about the book."
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
        return f"Let's explore '{title}' by {authors}! This book from {publisher} ({year}) has {loan_count} loans, indicating its appeal to readers. I'm here to discuss anything about this book - from plot details to thematic analysis. What aspect interests you most?\n\n한국어 답변: {authors}의 '{title}'을 탐험해 봅시다! {publisher}({year})의 이 책은 {loan_count}번의 대출로 독자들에게 어필하고 있음을 보여줍니다. 줄거리 세부사항부터 주제 분석까지 이 책에 대한 모든 것을 논의할 준비가 되어 있습니다. 어떤 측면에 가장 관심이 있으신가요?"

def process_book_question(book, question, api_key, conversation_history):
    """Process specific questions about a book using HyperCLOVA with improved context handling"""
    if not api_key:
        return "Please provide your HyperCLOVA API key in the sidebar to get detailed responses about this book.\n\n한국어 답변: 이 책에 대한 자세한 답변을 받으려면 사이드바에서 HyperCLOVA API 키를 제공해 주세요."
    
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
            role = "사용자" if msg["role"] == "user" else "AI"
            context_string += f"{role}: {msg['content']}\n\n"
    
    book_info = f"제목: '{title}', 저자: {authors}, 출판사: {publisher}, 출간년도: {year}, 인기도: {loan_count}회 대출"
    
    # Enhanced prompt with better context integration
    enhanced_prompt = f"""
현재 논의 중인 도서 정보:
{book_info}

이전 대화 내용:
{context_string}

사용자의 새로운 질문: "{question}"

위의 도서와 이전 대화 맥락을 모두 고려하여 사용자의 질문에 대해 상세하고 도움이 되는 답변을 제공해주세요.

답변 지침:
1. 이전 대화의 맥락을 참고하여 연속성 있는 답변을 제공하세요
2. 책의 내용, 주제, 등장인물, 문체, 문화적 배경 등에 대해 구체적으로 설명하세요
3. 필요시 유사한 책 추천도 포함하세요
4. 영어로 완전한 답변을 먼저 제공하고, 그 다음 "한국어 답변:" 이후에 한국어 번역을 제공하세요

답변은 상세하고 통찰력 있게 작성해주세요.
"""
    
    messages = [
        {
            "role": "system",
            "content": f"당신은 '{title}' by {authors}에 대해 논의하는 지식이 풍부한 도서 전문가입니다. 이전 대화의 맥락을 기억하고 연속성 있는 답변을 제공합니다. 모든 답변은 영어와 한국어 모두로 제공하며, 먼저 영어로 완전한 답변을 하고 그 다음 '한국어 답변:'으로 한국어 번역을 제공합니다. 도서의 주제, 줄거리 요소, 등장인물 분석, 문체, 문화적 맥락, 유사한 도서 추천 등을 포함한 상세하고 통찰력 있는 정보를 제공합니다."
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
            return f"I'd be happy to continue our discussion about '{title}', but I'm having trouble connecting to the AI service right now. Could you try asking your question again?\n\n한국어 답변: '{title}'에 대한 논의를 계속하고 싶지만 지금 AI 서비스에 연결하는 데 문제가 있습니다. 질문을 다시 해보시겠어요?"
    except Exception as e:
        st.error(f"Error processing question: {e}")
        return f"I encountered an error while processing your question about '{title}'. Please try rephrasing your question or check your API connection.\n\n한국어 답변: '{title}'에 대한 질문을 처리하는 중 오류가 발생했습니다. 질문을 다시 표현하거나 API 연결을 확인해 주세요."

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
                "First provide complete English answer, then '한국어 답변:' with Korean translation."
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

    st.markdown("<h1 style='text-align:center;'>📚 Book Wanderer / 책방랑자</h1>", unsafe_allow_html=True)
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
            "content": "Hello! Tell me about your favourite books, author, genre, or age group. You can describe what you're looking for in natural language.\n\n한국어 답변: 안녕하세요! 좋아하는 책, 작가, 장르 또는 연령대에 대해 말씀해 주세요. 자연스러운 언어로 원하는 것을 설명해 주시면 됩니다."
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
                        {"role": "system", "content": "You are a helpful book recommendation assistant. For EVERY response, answer in BOTH English and Korean. First provide complete English answer, then '한국어 답변:' with Korean translation."},
                        {"role": "user", "content": f"I found {len(books)} books in the {dtl_label} category. Tell me about this category and encourage me to explore these recommendations."}
                    ], st.session_state.api_key)
                    
                    if ai_response:
                        st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    else:
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": f"Great! I found {len(books)} excellent books in the {dtl_label} category. These recommendations are based on popularity and should match your interests perfectly. Take a look at the books below!\n\n한국어 답변: 좋습니다! {dtl_label} 카테고리에서 {len(books)}권의 훌륭한 책을 찾았습니다. 이 추천은 인기도를 바탕으로 하며 당신의 관심사와 완벽하게 일치할 것입니다. 아래 책들을 살펴보세요!"
                        })
                
                st.session_state.app_stage = "show_recommendations"
            else:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "I couldn't find books in that specific category. Could you try describing your preferences differently? For example, mention specific genres like 'mystery novels', 'self-help books', or 'Korean literature'.\n\n한국어 답변: 해당 카테고리에서 책을 찾을 수 없었습니다. 다른 방식으로 선호도를 설명해 주시겠어요? 예를 들어 '추리소설', '자기계발서', '한국문학'과 같은 구체적인 장르를 언급해 주세요."
                })
                st.session_state.app_stage = "awaiting_user_input"
        else:
            missing_items = []
            if not dtl_code:
                missing_items.append("category matching")
            if not st.session_state.library_api_key:
                missing_items.append("Library API key")
            
            error_msg = f"Unable to process your request due to: {', '.join(missing_items)}. Please check your API configuration in the sidebar."
            korean_msg = f"다음 이유로 요청을 처리할 수 없습니다: {', '.join(missing_items)}. 사이드바에서 API 설정을 확인해 주세요."
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"{error_msg}\n\n한국어 답변: {korean_msg}"
            })
            st.session_state.app_stage = "awaiting_user_input"
        
        st.rerun()

    elif st.session_state.app_stage == "show_recommendations":
        st.markdown("### 📖 Recommended Books for You")
        
        # Display books
        for i, book in enumerate(st.session_state.books_data[:10]):  # Show top 10 books
            display_book_card(book, i)
        
        # Chat input for follow-up questions
        user_followup = st.text_input("Ask me anything about these books or request different recommendations:", key="followup_input")
        if st.button("Send", key="send_followup"):
            if user_followup:
                st.session_state.messages.append({"role": "user", "content": user_followup})
                
                # Check if user wants new recommendations
                if any(keyword in user_followup.lower() for keyword in ['different', 'other', 'new', 'more', '다른', '새로운', '더']):
                    st.session_state.app_stage = "process_user_input"
                else:
                    # Process as follow-up question using HyperCLOVA
                    response = process_followup_with_hyperclova(user_followup, st.session_state.api_key)
                    if response:
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    else:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "I'd be happy to help you with more information about these books or other recommendations. What specific aspect would you like to know more about?\n\n한국어 답변: 이 책들에 대한 더 많은 정보나 다른 추천에 대해 기꺼이 도와드리겠습니다. 어떤 구체적인 측면에 대해 더 알고 싶으신가요?"
                        })
                st.rerun()

    elif st.session_state.app_stage == "discuss_book":
        if st.session_state.selected_book:
            book = st.session_state.selected_book
            
            # Display selected book details
            st.markdown("### 📖 Let's Talk About This Book")
            
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
            if st.button("← Back to Recommendations", key="back_to_recs"):
                # Clear book discussion messages and intro flag when going back
                st.session_state.book_discussion_messages = []
                st.session_state.book_intro_shown = False
                st.session_state.app_stage = "show_recommendations"
                st.rerun()

    elif st.session_state.app_stage == "show_liked_books":
        st.markdown("### ❤️ My Library")
        
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
        if st.button("← Back to Book Discovery", key="back_to_main"):
            st.session_state.app_stage = "show_recommendations" if st.session_state.books_data else "welcome"
            st.rerun()

if __name__ == "__main__":
    main()
