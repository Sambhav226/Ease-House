from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.orm import Session

db = SQLAlchemy()

# Define the association table between User and Role
user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.user_id', ondelete="CASCADE"), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id', ondelete="CASCADE"), primary_key=True)
)

# Users table with role column to distinguish Admin, ServiceProvider, Consumer
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)

    # Many-to-many relationship with Role, no cascade on delete to keep roles intact
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))


class Consumer(db.Model):
    __tablename__ = 'consumer'
    consumer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_flagged = db.Column(db.Boolean, default=False)

    # One-to-many relationship with ServiceRequest, but no cascade delete
    service_requests = db.relationship('ServiceRequest', backref='consumer', lazy='dynamic')

class ServiceCategory(db.Model):
    __tablename__ = 'service_category'
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Numeric(10, 2), nullable=False)

    # Relationship with ServiceProvider: Cascade delete ServiceProviders when category is deleted
    service_providers = db.relationship(
        'ServiceProvider',
        backref='category',
        cascade="all, delete-orphan",  # Ensures providers are deleted when category is deleted
        passive_deletes=True,
        lazy=True
    )

class ServiceProvider(db.Model):
    __tablename__ = 'service_provider'
    provider_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('service_category.category_id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    experience_years = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    is_flagged = db.Column(db.Boolean, default=False)

    # Cascade delete for related service requests
    service_requests = db.relationship(
        'ServiceRequest',
        backref='provider',
        cascade='all, delete-orphan',  # Ensures service requests are deleted when provider is deleted
        passive_deletes=True,
        lazy=True
    )

class ServiceRequest(db.Model):
    __tablename__ = 'service_request'
    request_id = db.Column(db.Integer, primary_key=True)
    consumer_id = db.Column(db.Integer, db.ForeignKey('consumer.consumer_id', ondelete="CASCADE"), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.provider_id', ondelete="CASCADE"), nullable=False)
    is_accepted = db.Column(db.String(50), default='pending', nullable=False)  # Values: 'yes', 'no', 'pending'
    is_completed = db.Column(db.Boolean, default=False)  # Completed status by consumer
    is_closed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime, nullable=True)  # Date when marked as completed
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(255), nullable=True)


    # Ensuring ServiceRequest deletion does not cascade to ServiceProvider or Consumer
    # The `ondelete="CASCADE"` is kept to allow orphaned requests to be deleted if the Consumer or ServiceProvider is deleted
    # But it will not delete any other objects associated with the ServiceRequest itself.


# class Review(db.Model):
#     __tablename__ = 'reviews'
#     review_id = db.Column(db.Integer, primary_key=True)
#     request_id = db.Column(db.Integer, db.ForeignKey('service_request.request_id', ondelete="CASCADE"), nullable=False)
#     consumer_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False)
#     provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.provider_id', ondelete="CASCADE"), nullable=False)
#     rating = db.Column(db.Integer, nullable=False)
#     review_text = db.Column(db.Text, nullable=True)