
# CN2BN - Cross Border E-commerce Platform

![Django](https://img.shields.io/badge/Django-3.2-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)

A Django-based cross-border e-commerce platform with multi-role management system.

## Features

### Role-Based Access Control
- **Admin**
  - Product management (CRUD operations)
  - Currency rate control
  - Delivery configuration
  - Staff management
  - System-wide configurations

- **Staff**
  - Product display management
  - Order processing
  - Customer communication (phone calls)
  - Order status updates

- **User**
  - Product requests (CRUD)
  - Order history tracking
  - Profile management
  - Cross-border payment processing

### Core Functionalities
- Multi-role authentication system
- Gmail verification for user registration
- Product catalog with category filtering
- Real-time currency conversion
- Order tracking system
- Cross-border delivery management

## Installation

1. **Clone Repository**
```bash
git clone https://github.com/Tanvir-yzu/cn2bn.git
cd cn2bn
```

2. **Set Up Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Database Setup**
```bash
python manage.py migrate
```

5. **Create Superuser**
```bash
python manage.py createsuperuser
```

6. **Run Development Server**
```bash
python manage.py runserver
```

## Configuration

Create `.env` file:
```env
SECRET_KEY=your_django_secret_key
DEBUG=True
DB_NAME=cn2bn_db
DB_USER=db_user
DB_PASSWORD=db_password
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_password
```

## Models Overview

### User Model
- name
- email (verified)
- phone (WhatsApp)
- profile_photo
- NID
- facebook_url
- address

### ProductRequest Model
- user (ForeignKey)
- product_info (JSON)
- quantity
- delivery_method
- payment_method
- timestamp
- status

### Product Model
- name
- images
- category (ForeignKey)
- quantity
- price
- available
- colors (ManyToMany)
- sizes (ManyToMany)

### Staff Model
- user (OneToOne)
- nid
- phone
- created_at
- status

### Additional Models
- Category
- Color
- Size

## Frontend Pages
- Homepage with featured products
- Product detail page
- Signup/Login pages
- User profile management
- Password reset functionality
- Order history page
- Category-filtered product listings
- Order confirmation page

## Authentication System
- Email verification for new registrations
- Password reset via email
- Role-based access control
- Social media integration (Facebook)
- Session management

## Database Schema
![Database Schema](docs/db_schema.png) <!-- Add actual schema image path -->

## Technologies Used
- **Backend**: Django 3.2
- **Database**: PostgreSQL
- **Frontend**: HTML5, Bootstrap 5, jQuery
- **Payment**: Cross-border payment gateway integration
- **Deployment**: Docker-ready configuration

## Contribution
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License
MIT License

## Support
Contact: support@cn2bn.com
```

Note: 
1. Replace placeholder values (yourusername, support email, etc.) with actual project details
2. Add proper database schema diagram image when available
3. Update requirements.txt with actual project dependencies
4. Include proper documentation links for payment gateway integration
5. Add deployment instructions specific to your hosting environment

