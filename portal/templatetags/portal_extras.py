import re
from django import template

register = template.Library()

@register.filter(name='embed_video')
def embed_video(url):
    if not url:
        return ""
    
    # Google Drive Links conversion to Embed Preview URL
    if "drive.google.com" in url:
        # e.g., https://drive.google.com/file/d/VIDEO_ID/view...
        if "/file/d/" in url:
            try:
                parts = url.split("/file/d/")
                if len(parts) > 1:
                    video_id = parts[1].split("/")[0].split("?")[0]
                    return f"https://drive.google.com/file/d/{video_id}/preview"
            except Exception:
                pass
        # e.g., https://drive.google.com/open?id=VIDEO_ID
        elif "id=" in url:
            match = re.search(r"[?&]id=([^&]+)", url)
            if match:
                return f"https://drive.google.com/file/d/{match.group(1)}/preview"
            
    # YouTube Links conversion to Embed URL
    if "youtube.com" in url or "youtu.be" in url:
        if "embed" in url:
            return url
        elif "watch?v=" in url:
            match = re.search(r"v=([^&]+)", url)
            if match:
                return f"https://www.youtube.com/embed/{match.group(1)}"
        elif "youtu.be/" in url:
            try:
                parts = url.split("youtu.be/")
                if len(parts) > 1:
                    video_id = parts[1].split("?")[0]
                    return f"https://www.youtube.com/embed/{video_id}"
            except Exception:
                pass
            
    return url

@register.filter(name='card_image')
def card_image(item):
    if not item:
        return 'https://via.placeholder.com/400x300/3b82f6/ffffff?text=Project'
    
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
                
    # 5. Default Placeholder
    return 'https://via.placeholder.com/400x300/3b82f6/ffffff?text=Project'
