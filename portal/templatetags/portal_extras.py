import re
from django import template

register = template.Library()

@register.filter(name='embed_video')
def embed_video(url):
    if not url:
        return ""
    
    url_lower = url.lower().strip()
    
    # Google Drive Links conversion to Embed Preview URL
    if "drive.google.com" in url_lower:
        if "/file/d/" in url:
            try:
                parts = url.split("/file/d/")
                if len(parts) > 1:
                    video_id = parts[1].split("/")[0].split("?")[0]
                    return f"https://drive.google.com/file/d/{video_id}/preview"
            except Exception:
                pass
        elif "id=" in url:
            match = re.search(r"[?&]id=([^&]+)", url)
            if match:
                return f"https://drive.google.com/file/d/{match.group(1)}/preview"
            
    # YouTube Links conversion to Embed URL
    elif "youtube.com" in url_lower or "youtu.be" in url_lower:
        if "embed" in url:
            if "playsinline" not in url:
                separator = "&" if "?" in url else "?"
                return f"{url}{separator}playsinline=1"
            return url
        elif "watch?v=" in url:
            match = re.search(r"v=([^&]+)", url)
            if match:
                return f"https://www.youtube.com/embed/{match.group(1)}?playsinline=1"
        elif "youtu.be/" in url:
            try:
                parts = url.split("youtu.be/")
                if len(parts) > 1:
                    video_id = parts[1].split("?")[0]
                    return f"https://www.youtube.com/embed/{video_id}?playsinline=1"
            except Exception:
                pass
                
    # Vimeo Links conversion to Embed URL
    elif "vimeo.com" in url_lower:
        if "player.vimeo.com" in url:
            if "playsinline" not in url:
                separator = "&" if "?" in url else "?"
                return f"{url}{separator}playsinline=1"
            return url
        else:
            match = re.search(r"vimeo\.com/(\d+)", url)
            if match:
                return f"https://player.vimeo.com/video/{match.group(1)}?playsinline=1"
                
    # Direct video links
    elif url_lower.endswith(('.mp4', '.webm', '.ogg', '.mov', '.avi')):
        return url
            
    return url

@register.filter(name='is_direct_video')
def is_direct_video(url):
    if not url:
        return False
    url_lower = url.lower().strip()
    return url_lower.endswith(('.mp4', '.webm', '.ogg', '.mov', '.avi')) or any(ext in url_lower for ext in ['.mp4?', '.webm?', '.ogg?'])

@register.filter(name='embed_audio')
def embed_audio(url):
    if not url:
        return ""
    
    # Google Drive Links conversion to Direct Download/Stream URL
    if "drive.google.com" in url:
        if "/file/d/" in url:
            try:
                parts = url.split("/file/d/")
                if len(parts) > 1:
                    file_id = parts[1].split("/")[0].split("?")[0]
                    return f"https://docs.google.com/uc?export=download&id={file_id}"
            except Exception:
                pass
        elif "id=" in url:
            match = re.search(r"[?&]id=([^&]+)", url)
            if match:
                return f"https://docs.google.com/uc?export=download&id={match.group(1)}"
            
    return url

@register.filter(name='card_image')
def card_image(item):
    if not item:
        return 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&auto=format&fit=crop'
    
    # 1. Check cover_image
    cover_image = getattr(item, 'cover_image', None)
    if cover_image:
        return cover_image
        
    # 2. Check main image
    image = getattr(item, 'image', None)
    if image:
        return image
        
    # 3. Check first image in gallery
    gallery_images = getattr(item, 'images', None)
    if gallery_images and isinstance(gallery_images, list) and len(gallery_images) > 0:
        return gallery_images[0]
        
    # 4. Check video thumbnail if it's YouTube
    video = getattr(item, 'video', None)
    if video:
        if "youtube.com" in video or "youtu.be" in video:
            video_id = None
            if "embed/" in video:
                video_id = video.split("embed/")[1].split("?")[0]
            elif "v=" in video:
                match = re.search(r"v=([^&]+)", video)
                if match:
                    video_id = match.group(1)
            elif "youtu.be/" in video:
                video_id = video.split("youtu.be/")[1].split("?")[0]
            if video_id:
                return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                
    # 5. Default Placeholders based on content type
    class_name = item.__class__.__name__
    if class_name == 'Podcast':
        return 'https://images.unsplash.com/photo-1478737270239-2f02b77fc618?w=800&auto=format&fit=crop'
    elif class_name == 'Investor':
        return 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&auto=format&fit=crop'
    elif class_name == 'Service':
        return 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&auto=format&fit=crop'
    return 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&auto=format&fit=crop'
