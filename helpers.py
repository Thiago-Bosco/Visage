import os
from flask import request, url_for

def get_image_url(product):
    """
    Get image URL for product - from database or fallback to placeholder
    """
    # If product has image data in database, serve from database
    if product.image_data:
        return url_for('serve_product_image', product_id=product.id)
    
    # If it's an external URL (http/https), return as is
    if product.image_url and product.image_url.startswith(('http://', 'https://')):
        return product.image_url
    
    # Default fallback to placeholder
    return 'https://via.placeholder.com/300x300/8B4513/FFFFFF?text=Produto'