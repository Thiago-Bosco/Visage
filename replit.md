# Barbearia Premium E-commerce

## Overview

This is a Flask-based e-commerce application for a barbershop that specializes in selling premium men's grooming products. The application features a product catalog, shopping cart functionality, and order processing via WhatsApp integration. It includes an admin panel for product management and order tracking.

## User Preferences

Preferred communication style: Simple, everyday language.
Visual preference: Modern, functional design with premium appearance.

## WhatsApp Configuration

Vendor WhatsApp Number: +55 19 98189-6803 (configured for order processing)

## System Architecture

The application follows a traditional MVC (Model-View-Controller) architecture using Flask as the web framework. It's designed as a monolithic application with clear separation of concerns across different modules.

### Core Architecture Components:
- **Flask Web Framework**: Provides the web server and routing capabilities
- **SQLAlchemy ORM**: Handles database operations and model definitions
- **Flask-Admin**: Provides administrative interface for product and order management
- **Flask-WTF**: Handles form validation and CSRF protection
- **Bootstrap 5**: Frontend styling framework with dark theme
- **WhatsApp Integration**: For order processing and customer communication

## Key Components

### Backend Components:

1. **Application Factory** (`app.py`)
   - Configures Flask application with database settings
   - Initializes SQLAlchemy with declarative base
   - Sets up session management and proxy handling
   - Creates initial seed data for products

2. **Data Models** (`models.py`)
   - **Product**: Core product entity with pricing, inventory, and categorization
   - **CartItem**: Session-based shopping cart items
   - **Order**: Customer orders with status tracking
   - **OrderItem**: Individual items within orders

3. **Web Routes** (`routes.py`)
   - Product catalog display
   - Shopping cart management (add, update, remove)
   - Session-based cart tracking using UUID
   - Order processing and WhatsApp integration

4. **Forms** (`forms.py`)
   - Product management forms with validation
   - Shopping cart quantity forms
   - Customer checkout forms with phone integration

5. **Admin Interface** (`admin.py`)
   - Custom admin dashboard with statistics
   - Product management with search and filtering
   - Order tracking and status management

### Frontend Components:

1. **Templates** (`templates/`)
   - **Base Template**: Common layout with navigation and Bootstrap integration
   - **Index**: Product catalog with hero section and grid layout
   - **Cart**: Shopping cart management interface
   - **Checkout**: Customer information and WhatsApp order processing

2. **Static Assets** (`static/`)
   - **CSS**: Custom barbershop theming with brown/gold color scheme
   - **JavaScript**: Cart management and form validation

## Data Flow

1. **Product Browsing**: Users view products from the catalog page, filtered by availability
2. **Cart Management**: Products are added to session-based cart using UUID tracking
3. **Checkout Process**: Customer provides contact information for order processing
4. **Order Creation**: Cart items are converted to order records in database
5. **WhatsApp Integration**: Order details are formatted and sent via WhatsApp link
6. **Admin Management**: Staff can manage products and track orders through admin panel

## External Dependencies

### Core Framework Dependencies:
- **Flask**: Web application framework
- **SQLAlchemy**: Database ORM and migrations
- **Flask-Admin**: Administrative interface
- **Flask-WTF**: Form handling and validation
- **WTForms**: Form field definitions and validators

### Frontend Dependencies:
- **Bootstrap 5**: CSS framework with dark theme support
- **Font Awesome**: Icon library for UI elements
- **Custom CSS**: Barbershop-themed styling

### Third-Party Integrations:
- **WhatsApp Business API**: Order processing and customer communication
- **Placeholder Images**: Via.placeholder.com for product images

## Deployment Strategy

### Database Configuration:
- **Development**: SQLite database (barbershop.db)
- **Production**: Configurable via DATABASE_URL environment variable
- **Connection Pooling**: Configured with pool recycling and pre-ping health checks

### Environment Configuration:
- **Session Secret**: Configurable via SESSION_SECRET environment variable
- **Database URL**: Configurable via DATABASE_URL environment variable
- **Debug Mode**: Enabled for development, should be disabled in production

### Application Structure:
- **Entry Point**: `main.py` runs the Flask application on port 5000
- **Proxy Handling**: Configured for deployment behind reverse proxy
- **Session Management**: Uses secure session handling with configurable secret key

### Scalability Considerations:
- Session-based cart storage allows for horizontal scaling
- Database pooling configured for connection management
- Static assets served efficiently through Flask
- Admin interface provides operational management capabilities

The application is designed to be easily deployable on platforms like Replit, Heroku, or similar PaaS providers with minimal configuration changes.