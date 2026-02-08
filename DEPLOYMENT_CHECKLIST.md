"""
Checklist for deployment
"""

## Pre-Deployment Checklist

### Backend
- [ ] Update SECRET_KEY in production settings
- [ ] Set DEBUG = False
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up PostgreSQL database
- [ ] Configure static files storage
- [ ] Configure media files storage
- [ ] Set up email service
- [ ] Configure HTTPS/SSL
- [ ] Set up logging
- [ ] Configure Redis
- [ ] Run migrations
- [ ] Create superuser
- [ ] Collect static files
- [ ] Test email functionality
- [ ] Set up domain/DNS
- [ ] Configure CORS for production domain
- [ ] Set security headers
- [ ] Enable CSRF protection
- [ ] Test authentication flow
- [ ] Set up monitoring
- [ ] Backup database

### Frontend
- [ ] Update API URL to production
- [ ] Build optimized bundle
- [ ] Test all features
- [ ] Check browser console for errors
- [ ] Verify responsive design
- [ ] Test authentication flow
- [ ] Optimize images
- [ ] Enable compression
- [ ] Set up CDN (optional)
- [ ] Configure caching headers
- [ ] Test on production domain
- [ ] Set up error tracking
- [ ] Performance testing

### Infrastructure
- [ ] Set up servers/hosting
- [ ] Configure firewall
- [ ] Set up SSL certificates
- [ ] Configure reverse proxy (nginx/Apache)
- [ ] Set up database backups
- [ ] Configure auto-scaling (if applicable)
- [ ] Set up monitoring/alerting
- [ ] Configure log aggregation
- [ ] Set up CI/CD pipeline
- [ ] Document deployment process
- [ ] Create runbooks
- [ ] Set up status page

## Post-Deployment

- [ ] Monitor error logs
- [ ] Monitor performance metrics
- [ ] Check user feedback
- [ ] Have rollback plan ready
- [ ] Schedule follow-up review
- [ ] Update documentation
- [ ] Communicate with users
