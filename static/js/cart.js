// Cart Management JavaScript

class BarbershopCart {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateCartUI();
        this.initializeTooltips();
    }

    bindEvents() {
        // Add to cart form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.classList.contains('add-to-cart-form')) {
                this.handleAddToCart(e);
            }
        });

        // Quantity updates
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('quantity-input')) {
                this.handleQuantityChange(e);
            }
        });

        // Remove from cart confirmations
        document.addEventListener('click', (e) => {
            if (e.target.closest('[data-action="remove-item"]')) {
                this.handleRemoveItem(e);
            }
        });

        // Clear cart confirmation
        document.addEventListener('click', (e) => {
            if (e.target.closest('[data-action="clear-cart"]')) {
                this.handleClearCart(e);
            }
        });

        // Checkout form validation
        const checkoutForm = document.getElementById('checkoutForm');
        if (checkoutForm) {
            checkoutForm.addEventListener('submit', this.handleCheckout.bind(this));
        }
    }

    handleAddToCart(e) {
        const form = e.target;
        const button = form.querySelector('button[type="submit"]');
        const originalText = button.innerHTML;
        
        // Show loading state
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Adicionando...';
        button.disabled = true;

        // Add animation to button
        button.classList.add('btn-pulse');

        // Simulate network delay for better UX
        setTimeout(() => {
            button.innerHTML = '<i class="fas fa-check me-2"></i>Adicionado!';
            button.classList.remove('btn-pulse');
            button.classList.add('btn-success');
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.classList.remove('btn-success');
                button.disabled = false;
            }, 1500);
        }, 500);
    }

    handleQuantityChange(e) {
        const input = e.target;
        const quantity = parseInt(input.value);
        
        if (quantity < 1) {
            input.value = 1;
            this.showAlert('Quantidade mínima é 1', 'warning');
            return;
        }
        
        if (quantity > 99) {
            input.value = 99;
            this.showAlert('Quantidade máxima é 99', 'warning');
            return;
        }

        // Add visual feedback
        input.style.backgroundColor = '#d4edda';
        setTimeout(() => {
            input.style.backgroundColor = '';
        }, 300);

        this.debounce(() => {
            this.updateCartTotals();
        }, 500)();
    }

    handleRemoveItem(e) {
        e.preventDefault();
        
        const link = e.target.closest('a');
        const productName = link.dataset.productName || 'este item';
        
        if (confirm(`Tem certeza que deseja remover "${productName}" do carrinho?`)) {
            // Add removal animation
            const cartItem = link.closest('.cart-item');
            if (cartItem) {
                cartItem.style.transform = 'translateX(-100%)';
                cartItem.style.opacity = '0';
                
                setTimeout(() => {
                    window.location.href = link.href;
                }, 300);
            } else {
                window.location.href = link.href;
            }
        }
    }

    handleClearCart(e) {
        e.preventDefault();
        
        if (confirm('Tem certeza que deseja limpar todo o carrinho?')) {
            window.location.href = e.target.href;
        }
    }

    handleCheckout(e) {
        const form = e.target;
        const submitButton = form.querySelector('button[type="submit"]');
        
        // Validate required fields
        const nameInput = form.querySelector('#customer_name');
        if (!nameInput.value.trim()) {
            nameInput.focus();
            this.showAlert('Por favor, preencha seu nome', 'error');
            e.preventDefault();
            return;
        }

        // Show loading state
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Preparando WhatsApp...';
        submitButton.disabled = true;

        // Add success animation
        setTimeout(() => {
            submitButton.innerHTML = '<i class="fab fa-whatsapp me-2"></i>Redirecionando...';
        }, 1000);
    }

    updateCartTotals() {
        // This would be called after quantity changes to update totals
        // In a real app, you might make an AJAX call here
        console.log('Updating cart totals...');
    }

    updateCartUI() {
        // Update cart counter in navbar
        const cartBadges = document.querySelectorAll('.cart-count');
        // This would be updated based on actual cart contents
    }

    initializeTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    showAlert(message, type = 'info') {
        // Create and show custom alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        const icon = this.getAlertIcon(type);
        
        alertDiv.innerHTML = `
            <i class="${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    getAlertIcon(type) {
        const icons = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-triangle',
            'warning': 'fas fa-exclamation-circle',
            'info': 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Utility Functions
const BarbershopUtils = {
    formatPrice(price) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(price);
    },

    formatPhone(phone) {
        const cleaned = phone.replace(/\D/g, '');
        if (cleaned.length === 11) {
            return cleaned.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
        } else if (cleaned.length === 10) {
            return cleaned.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
        }
        return phone;
    },

    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    validatePhone(phone) {
        const cleaned = phone.replace(/\D/g, '');
        return cleaned.length >= 10 && cleaned.length <= 11;
    }
};

// Custom CSS Animations
const style = document.createElement('style');
style.textContent = `
    .btn-pulse {
        animation: pulse 0.5s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .cart-item {
        transition: all 0.3s ease;
    }
    
    .fade-out {
        opacity: 0;
        transform: translateX(-100%);
    }
    
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    
    .loading-spinner {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
    }
`;
document.head.appendChild(style);

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BarbershopCart();
    
    // Initialize other features
    initializeProductFilters();
    initializeImageLazyLoading();
    initializeScrollAnimations();
});

// Product Filters (for future enhancement)
function initializeProductFilters() {
    const filterButtons = document.querySelectorAll('[data-filter]');
    filterButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const filter = e.target.dataset.filter;
            filterProducts(filter);
        });
    });
}

function filterProducts(category) {
    const products = document.querySelectorAll('.product-card');
    products.forEach(product => {
        const productCategory = product.dataset.category;
        if (category === 'all' || productCategory === category) {
            product.style.display = 'block';
            product.classList.add('fade-in-up');
        } else {
            product.style.display = 'none';
        }
    });
}

// Image Lazy Loading
function initializeImageLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => imageObserver.observe(img));
    }
}

// Scroll Animations
function initializeScrollAnimations() {
    if ('IntersectionObserver' in window) {
        const animationObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-up');
                }
            });
        }, { threshold: 0.1 });

        const animatedElements = document.querySelectorAll('.animate-on-scroll');
        animatedElements.forEach(el => animationObserver.observe(el));
    }
}

// Export for use in other scripts
window.BarbershopCart = BarbershopCart;
window.BarbershopUtils = BarbershopUtils;
