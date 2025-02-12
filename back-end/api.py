from flask import Flask, jsonify, request, session
from flask_restful import Api, Resource, reqparse
from flask_security import Security, SQLAlchemyUserDatastore, auth_token_required, hash_password, verify_and_update_password, current_user, roles_required, login_user, logout_user,auth_required, roles_accepted
from models import * #db, User, Role, ServiceRequest, ServiceCategory, ServiceProvider, Consumer
from flask import current_app as app
from cache import cache
from datetime import datetime
import uuid

api = Api()


# Request parsers for signup/login
# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
#security = Security(app, user_datastore)


''' Signup, Login and Logout Api'''
class UserAuth(Resource):
    def post(self):
        """Signup functionality using POST method"""

        # Define request parser
        user_parser = reqparse.RequestParser()
        user_parser.add_argument('email', type=str, required=True, help="Email is required")
        user_parser.add_argument('password', type=str, required=True, help="Password is required")
        user_parser.add_argument('username', type=str, required=True, help="Username is required")
        user_parser.add_argument('name', type=str, required=True, help="Name is required")
        user_parser.add_argument('role', type=str, required=True, help="Role is required")

        # Additional fields for ServiceProvider
        user_parser.add_argument('experience_years', type=int, required=False, help="Experience years are required for ServiceProvider")
        user_parser.add_argument('description', type=str, required=False, help="Description is required for ServiceProvider")
        user_parser.add_argument('category_name', type=str, required=False, help="Service name is required for ServiceProvider")
        user_parser.add_argument('price', type=float, required=False, help="Price is required for ServiceProvider")

        # Parse arguments
        args = user_parser.parse_args()
        user_name = args['username']
        name = args['name']
        email = args['email']
        password = args['password']
        role_name = args['role']

        # Check if the user already exists
        if User.query.filter_by(email=email).first():
            return {"message": "User already exists"}, 400

        # Fetch the role from the database
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            return {"message": "Role not found"}, 400

        # Role-specific validation and user creation
        if role_name.lower() == "serviceprovider":
            experience_years = args.get("experience_years", 0)
            description = args.get("description", "")
            category_name = args.get("category_name")
            price = args.get("price")

            # Validate category_name and price
            if not category_name or price is None:
                return {"message": "Category name and Price are required"}, 400

            # Query the ServiceCategory by name
            category = ServiceCategory.query.filter_by(category_name=category_name).first()
            if not category:
                return {"message": f"Service category '{category_name}' not found. Please check the category name or add it to the database."}, 404

            # Create a new user with a unique fs_uniquifier
            user = User(
                username=user_name,
                email=email,
                password=hash_password(password),
                fs_uniquifier=str(uuid.uuid4()),  # Generate a unique identifier
            )
            db.session.add(user)
            db.session.commit()  # Commit to get the user ID

            # Add the role to the user
            user.roles.append(role)
            db.session.commit()  # Commit to update roles

            # Create and save the ServiceProvider entry
            service_provider = ServiceProvider(
                user_id=user.user_id,  # Use the newly created user's ID
                name=name,
                experience_years=experience_years,
                description=description,
                price=price,  # Include price field
                category_id=category.category_id  # Associate the category
            )
            db.session.add(service_provider)
            db.session.commit()  # Commit the new service provider entry

        elif role_name.lower() == "consumer":
            # Create a new user with a unique fs_uniquifier
            user = User(
                username=user_name,
                email=email,
                password=hash_password(password),
                fs_uniquifier=str(uuid.uuid4()),  # Generate a unique identifier
            )
            db.session.add(user)
            db.session.commit()  # Commit to get the user ID

            # Add the role to the user
            user.roles.append(role)
            db.session.commit()  # Commit to update roles

            # Create and save the Consumer entry
            consumer = Consumer(
                user_id=user.user_id,  # Use the newly created user's ID
                name=name
            )
            db.session.add(consumer)
            db.session.commit()  # Commit the new consumer entry

        else:
            return {"message": "Invalid role specified"}, 400

        # Return success response
        return {"message": "User created successfully", "user_id": user.user_id}, 201

class LoadServiceCategory(Resource):
    def get(self):
        categories = ServiceCategory.query.all()
        return {"categories": [category.category_name for category in categories]}, 200

    # @cache.cached(timeout = 10)
class UserLogin(Resource):
    def post(self):
        """Login functionality using POST method"""

        user_parser = reqparse.RequestParser()
        user_parser.add_argument('email', type=str, required=True, help="Email is required")
        user_parser.add_argument('password', type=str, required=True, help="Password is required")

        args = user_parser.parse_args()
        email = args['email']
        password = args['password']

        user = user_datastore.find_user(email=email)

        if user is None or not verify_and_update_password(password, user):
            return {'message': 'Invalid credentials'}, 401

        # Check roles and specific conditions
        role_names = [role.name.lower() for role in user.roles]

        if 'serviceprovider' in role_names:
            service_provider = ServiceProvider.query.filter_by(user_id=user.user_id).first()
            if service_provider:
                if not service_provider.is_verified:
                    return {'message': 'Account not verified. Please contact admin.'}, 403
                if service_provider.is_flagged:
                    return {'message': 'Account is flagged. Please contact admin.'}, 403

        if 'consumer' in role_names:
            consumer = Consumer.query.filter_by(user_id=user.user_id).first()
            if not consumer or consumer.is_flagged:
                return {'message': 'Account is flagged. Please contact admin.'}, 403

        # Generate token after verification checks
        token = user.get_auth_token()  # Generate authentication token
        role_name = role_names[0] if role_names else None  # Assuming single role per user
        print(role_name)
        if token:
            login_user(user)  # Log the user in for session-based auth
            db.session.commit()

        response = {
            'email': email,
            'token': token,
            'role': role_name,  # Include the user's role in the response
        }
        return jsonify(response)

    
class UpdateProfile(Resource):
    @auth_token_required
    def put(self):
        data = request.get_json()
        user_id = current_user.user_id

        # Fetch the user record
        user = User.query.filter_by(user_id=user_id).first()

        if not user:
            return {'message': 'User not found'}, 404

        # Check if the user is a Consumer
        consumer = Consumer.query.filter_by(user_id=user_id).first()
        if consumer:
            # Update consumer-related fields
            consumer.name = data.get('name', consumer.name)
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)

            # Only update password if it is explicitly provided
            if 'password' in data and data['password']:
                user.password = hash_password(data['password'])

            db.session.commit()
            return {'message': 'Consumer profile updated successfully'}, 200

        # Check if the user is a Service Provider
        provider = ServiceProvider.query.filter_by(user_id=user_id).first()
        if provider:
            # Update provider-related fields
            provider.name = data.get('name', provider.name)
            provider.description = data.get('description', provider.description)
            provider.experience_years = data.get('experience_years', provider.experience_years)
            provider.price = data.get('price', provider.price)

            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)

            # Only update password if it is explicitly provided
            if 'password' in data and data['password']:
                user.password = hash_password(data['password'])

            db.session.commit()
            return {'message': 'Provider profile updated successfully'}, 200

        return {'message': 'User role not found'}, 404


class Logout(Resource):
    @auth_token_required
    def get(self):
        if current_user.is_authenticated:
            user_email = current_user.email  # Get email before logging out
            logout_user()  # Use Flask-Security's built-in logout method
            session.clear()  # Clear the session data
            return {'message': 'Logged out successfully', 'user': user_email}, 200
        else:
            return {'message': 'No user is currently logged in'}, 401
        

'''APIs Related to Consumer Below'''

class ConsumerInfo(Resource):
    @auth_token_required
    @roles_required('consumer')
    @cache.cached(timeout = 60)
    def get(self):
        # if current_user.is_authenticated:
        user_id = current_user.user_id
        user_name = User.query.filter_by(user_id=user_id).first().username
        email = User.query.filter_by(user_id=user_id).first().email
        consumer = Consumer.query.filter_by(user_id=user_id).first()
        if consumer:
            return jsonify({
                'consumer': {
                    'consumer_id': consumer.consumer_id,
                    'user_id' : user_id,
                    'name': consumer.name,
                    'email' : email,
                    'username' : user_name
                }
            })
        
class ConsumerRequestDetails(Resource):
    @auth_token_required
    @roles_required('consumer')
    @cache.cached(timeout = 2)  # Ensure only consumers can access this
    def get(self, request_id):
        """
        Get the details of a specific service request by ID.
        """
        service_request = ServiceRequest.query.get(request_id)
        
        if not service_request:
            return {'error': 'Request not found'}, 404

        # Prepare response data
        response_data = {
            'request': {
                'location': service_request.location,
                'request_date': service_request.request_date.isoformat() if service_request.request_date else None,
                'completion_date': service_request.completion_date.isoformat() if service_request.completion_date else None,
                'is_completed': service_request.is_completed,
                'is_closed': service_request.is_closed,
            }
        }

        return jsonify(response_data)

class CreateServiceRequest(Resource):
    @auth_token_required
    @roles_required('consumer')
    def post(self):
        data = request.get_json()
        
        consumer_username = data.get('consumer_username')
        provider_id = data.get('provider_id')

        if not all([consumer_username, provider_id]):
            return {'message': 'Consumer username and Provider ID are required'}, 400

        # Fetch consumer's user record based on username
        consumer_user = User.query.filter_by(username=consumer_username).first()
        if not consumer_user:
            return {'message': 'Consumer not found'}, 404

        # Verify that the consumer exists in the Consumer table
        consumer = Consumer.query.filter_by(user_id=consumer_user.user_id).first()
        if not consumer:
            return {'message': 'Consumer record not found'}, 404

        # Verify that the provider exists in the ServiceProvider table and is verified
        provider = ServiceProvider.query.filter_by(provider_id=provider_id, is_verified=True).first()
        if not provider:
            return {'message': 'Service provider not found or not verified'}, 404

        # Check if provider is flagged
        if provider.is_flagged:
            return {'message': 'Service provider is flagged and cannot accept requests'}, 403

        # Check if there is an existing open or pending request for this provider by this consumer, excluding completed ones
        existing_request = ServiceRequest.query.filter_by(
            consumer_id=consumer.consumer_id,
            provider_id=provider.provider_id
        ).filter((ServiceRequest.is_accepted == 'pending') & (ServiceRequest.is_closed == False)) \
         .filter(ServiceRequest.is_completed != True).first()  # Exclude completed requests

        if existing_request:
            return {'message': 'A pending or open service request already exists for this provider from this consumer'}, 400

        # If a request exists but is closed, allow creating a new one
        closed_request = ServiceRequest.query.filter_by(
            consumer_id=consumer.consumer_id,
            provider_id=provider.provider_id,
            is_closed=True
        ).filter(ServiceRequest.is_accepted == 'pending').first()

        if closed_request:
            # Allow creation of a new request since the previous one is closed
            pass

        # Create a new ServiceRequest
        service_request = ServiceRequest(
            consumer_id=consumer.consumer_id,
            provider_id=provider.provider_id,
            is_accepted='pending',
            request_date=datetime.utcnow(),
            is_closed=False,  # Initially, the request is not closed
            is_completed=False  # Initially, the request is not completed
        )
        
        # Add the request to the session and commit
        db.session.add(service_request)
        db.session.commit()

        return {
            'message': 'Service request created successfully',
            'service_request_id': service_request.request_id,
            'is_accepted': service_request.is_accepted,
            'request_date': service_request.request_date.isoformat(),
            'location': service_request.location
        }, 201

# API Resource to update request status
class ConsumerUpdateRequestStatus(Resource):
    @auth_token_required
    @roles_required('consumer')
    def put(self, request_id):
        """Update multiple parameters of a service request, excluding 'is_accepted'."""
        data = request.get_json()
        service_request = ServiceRequest.query.get(request_id)

        if not service_request:
            return {'error': 'Request not found'}, 404

        # Fields that can be updated
        updatable_fields = [
            'location', 'request_date', 'completion_date', 'is_closed', 'is_completed'
        ]

        # Check if `is_completed` is being updated and if it's allowed
        if 'is_completed' in data:
            if service_request.is_accepted != "yes":
                return {'error': "Cannot update 'is_completed' unless 'is_accepted' is 'accepted'"}, 400

        # Handle `is_closed` defaulting to the existing DB value
        if 'is_closed' not in data:
            data['is_closed'] = service_request.is_closed

        # Update the provided fields
        for field in data:
            if field in updatable_fields:
                if field == 'request_date' or field == 'completion_date':
                    try:
                        # Validate ISO datetime format
                        setattr(service_request, field, datetime.fromisoformat(data[field]) if data[field] else None)
                    except ValueError:
                        return {'error': f"Invalid format for {field}. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}, 400
                else:
                    setattr(service_request, field, data[field] if data[field] else None)

        # Prevent modification of 'is_accepted' explicitly
        if 'is_accepted' in data:
            return {'error': "'is_accepted' cannot be modified in this request"}, 400

        # Commit changes to the database
        db.session.commit()
        return {'message': 'Request updated successfully'}, 200


    @auth_token_required
    @roles_required('consumer')
    def get(self, request_id):
        """Update only the completion status of a service request by the consumer."""
        
        # Fetch the service request by its ID
        service_request = ServiceRequest.query.get(request_id)
        
        if not service_request:
            return {'error': 'Request not found'}, 404
        
        # Check if the service request has been accepted
        if service_request.is_accepted != 'yes':
            return ({'error': 'Completion status can only be modified if the request is accepted'}), 403
        
        # Update the completion status to True and set the completion date
        service_request.is_completed = True
        service_request.completion_date = datetime.utcnow()
        
        # Commit the changes to the database
        db.session.commit()

        # Return success message with the updated status
        return {'message': "Completion status updated to 'completed'"}, 200

class ShowCurrentRequest(Resource):
    @auth_token_required
    @roles_required('consumer')
    def get(self):
        # Use the current user's ID to fetch associated consumer requests
        user_id = current_user.user_id
        consumer = Consumer.query.filter_by(user_id=user_id).first()
        if not consumer:
            return {'error': 'Consumer not found'}, 404

        # Fetch all active service requests for this consumer where is_closed=False
        # This includes requests that may not yet be accepted or completed
        service_requests = ServiceRequest.query.filter_by(consumer_id=consumer.consumer_id, is_closed=False).all()

        if not service_requests:
            return {'error': 'No active service requests found for this consumer'}, 404

        # Format the data to send back to the frontend
        requests_data = []
        for service_request in service_requests:
            # Collect necessary details from each service request
            requests_data.append({
                'request_id': service_request.request_id,
                'is_accepted': service_request.is_accepted,
                'is_completed': service_request.is_completed,
                'completion_date': service_request.completion_date.strftime('%Y-%m-%d %H:%M:%S') if service_request.completion_date else None,
                'request_date': service_request.request_date.strftime('%Y-%m-%d %H:%M:%S'),
                'location': service_request.location,
                'consumer_name': service_request.consumer.name if service_request.consumer else None,
                'consumer_id': service_request.consumer_id,
                'provider_id': service_request.provider_id,
                'is_flagged': service_request.provider.is_flagged if service_request.provider else None,
                'provider_name': service_request.provider.name if service_request.provider else None,
                'provider_verified': service_request.provider.is_verified if service_request.provider else None,
            })

        return {'requests': requests_data}, 200

class ShowServices(Resource):
    @auth_token_required
    @roles_required('consumer')
    def get(self):
        try:
            user_id = current_user.user_id if current_user else None
            #user_name = User.query.filter_by(user_id=user_id).first().username
            print(f"User ID: {user_id}")  # Log the user_id to debug

            if not user_id:
                return {"error": "User not logged in or invalid user ID"}, 400

            # Fetch consumer using the user_id
            consumer = Consumer.query.filter_by(user_id=user_id).first()
            print(f"Consumer found: {consumer}")  # Log the consumer to debug

            if not consumer:
                return {"error": "Consumer not found"}, 400
            
            # Fetch available services and their categories
            services = ServiceProvider.query.filter_by(is_verified=True, is_flagged=False).all()
            print(f"Found services: {services}")  # Log the services to debug

            # Retrieve the category for each service provider
            services_data = []
            for service in services:
                # Assuming the ServiceProvider has a foreign key field `category_id` that links to ServiceCategory
                category = ServiceCategory.query.filter_by(category_id=service.category_id).first()

                if category:
                    category_name = category.category_name

                if service.is_flagged or not service.is_verified:
                    continue
                else:
                    services_data.append({
                        'provider_id': service.provider_id,
                        #'user_name': user_name,
                        'category_name': category_name,
                        'name': service.name,
                        'experience_years': service.experience_years,
                        'description': service.description,
                        'is_verified': service.is_verified,
                        'price': float(service.price),
                        'is_flagged': service.is_flagged,
                        # Add other fields here as needed
                    })
            
            # Return the services data
            return {"services": services_data}, 200
        
        except Exception as e:
            # If anything goes wrong, log the error
            print(f"Error: {str(e)}")
            return {"error": "An unexpected error occurred"}, 500

    
class ConsumerCloseRequest(Resource):
    @auth_token_required
    @roles_required('consumer')
    def delete(self, request_id):
        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            return {'error': 'Request not found'}, 404

        service_request.is_closed = True
        # service_request.is_accepted = 'no'
        db.session.commit()
        return {'message': 'Request Closed successfully'}, 200
        

'''All the API for the ServiceProvider Below'''

class ProviderInfo(Resource):
    @auth_token_required
    @roles_required('serviceprovider')
    @cache.cached(timeout = 60)
    def get(self):
        # Fetch provider details using the current user's ID
        provider = ServiceProvider.query.filter_by(user_id=current_user.user_id).first()
        if not provider:
            return {'error': 'Service provider not found'}, 404

        provider_info = {
            'provider_id': provider.provider_id,
            'user_id': provider.user_id,
            'name': provider.name,
            'description': provider.description,
            'experience_years': provider.experience_years,
            'date_created': provider.date_created.strftime('%Y-%m-%d %H:%M:%S'),
            'is_verified': provider.is_verified,
            'is_flagged': provider.is_flagged,
            'price': str(provider.price),
            'category': provider.category.category_name if provider.category else 'N/A'
        }

        return {'provider_info': provider_info}, 200


# API Resource to get pending requests for a provider
class ShowProviderRequests(Resource):
    @auth_token_required
    @roles_required('serviceprovider')
    def get(self):
        # Fetch the current service provider using the user_id
        user_id = current_user.user_id
        provider = ServiceProvider.query.filter_by(user_id=user_id).first()

        if not provider:
            return {'error': 'Service provider not found'}, 404

        # Fetch all active service requests for this provider (not closed)
        service_requests = ServiceRequest.query.filter_by(
            provider_id=provider.provider_id, is_closed=False
        ).all()

        # Return error if no requests are found
        if not service_requests:
            return {'error': 'No active service requests found for this provider'}, 404

        # Format the response data
        requests_data = []
        for service_request in service_requests:
            consumer_id = service_request.consumer_id
            consumer_name = Consumer.query.filter_by(consumer_id=consumer_id).first().name
            requests_data.append({
                'request_id': service_request.request_id,
                'consumer_name': consumer_name,
                'request_date': service_request.request_date.strftime('%Y-%m-%d %H:%M:%S'),
                'is_completed': service_request.is_completed,
                'completion_date': service_request.completion_date.strftime('%Y-%m-%d %H:%M:%S') if service_request.completion_date else None,
                'is_accepted': service_request.is_accepted,  # 'yes', 'no', or 'pending'
                'location': service_request.location,
            })

        return {'requests': requests_data}, 200

    
class AcceptRequest(Resource):
    @auth_token_required
    @roles_required('serviceprovider')
    def get(self, request_id):
        """Update the acceptance status of a service request by the service provider."""

        # Fetch the service request
        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            return {'error': 'Request not found'}, 404

        # Update the acceptance status
        service_request.is_accepted = 'yes'

        db.session.commit()

        return {'message': f"Request acceptance status updated to yes"}, 200

class DeclineRequest(Resource):
    @auth_token_required
    @roles_required('serviceprovider')
    def get(self, request_id):
        """Update the acceptance status of a service request by the service provider."""

        # Fetch the service request
        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            return {'error': 'Request not found'}, 404

        # Update the acceptance status
        service_request.is_accepted = 'no'

        db.session.commit()

        return {'message': f"Request acceptance status updated to no"}, 200

    
class ProviderCloseRequest(Resource):
    @auth_token_required
    @roles_required('serviceprovider')
    def delete(self, request_id):
        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            return {'error': 'Request not found'}, 404
        
        if service_request.is_completed:
            service_request.is_closed = True
            # service_request.is_accepted = 'no'
            db.session.commit()
            return {'message': 'Request Closed successfully'}, 200
        else:
            return {'error': 'Request is not completed yet'}, 400
    

'''APIs Related to Admin are below'''

# Admin Only Resource (for testing admin access)

class AdminInfo(Resource):
    @auth_token_required
    @roles_required('admin')
    @cache.cached(timeout = 60)
    def get(self):
        # For testing purposes
        return jsonify({
            'message': 'Welcome Admin!',
            'user': current_user.email,
            'role': current_user.roles[0].name,
            'token': current_user.get_auth_token()
        })

class AdminDashboard(Resource):
    @auth_token_required
    @roles_required('admin')
    @cache.cached(timeout = 20)
    def get(self):
        try:
            # Fetch service categories
            categories = ServiceCategory.query.all()
            categories_data = [
                {
                    "category_id": category.category_id,
                    "category_name": category.category_name,
                    "base_price": str(category.base_price)
                }
                for category in categories
            ]

            # Fetch service providers
            providers = ServiceProvider.query.all()
            providers_data = [
                {
                    "provider_id": provider.provider_id,
                    "user_id": provider.user_id,
                    "name": provider.name,
                    "description": provider.description,
                    "experience_years": provider.experience_years,
                    "is_verified": provider.is_verified,
                    "price": str(provider.price),
                    "is_flagged": provider.is_flagged,
                    "category": provider.category.category_name if provider.category else None
                }
                for provider in providers
            ]

            # Fetch consumers
            consumers = Consumer.query.all()
            consumers_data = [
                {
                    "consumer_id": consumer.consumer_id,
                    "user_id": consumer.user_id,
                    "name": consumer.name,
                    "is_flagged": consumer.is_flagged
                }
                for consumer in consumers
            ]

            # Return data as JSON
            return {
                "categories": categories_data,
                "providers": providers_data,
                "consumers": consumers_data
            }, 200

        except Exception as e:
            return {"message": "Failed to fetch data", "error": str(e)}, 500

class Verification(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        # For testing purposes
        return jsonify({
            'message': 'Welcome Admin!',
            'user': current_user.email,
            'role': current_user.roles[0].name,
            'token': current_user.get_auth_token()
        })

    @auth_token_required
    @roles_required('admin')
    def put(self):
            """Update the is_verified status for the selected ServiceProvider"""
            data = request.get_json()
            provider_name = data.get('name')

            if provider_name is None:
                return {'message': 'Provider name is required'}, 400

            # Query for the service provider by name
            service_provider = ServiceProvider.query.filter_by(name=provider_name).first()

            if not service_provider:
                return {'message': f"ServiceProvider with name '{provider_name}' not found"}, 404

            # Set is_verified to True
            service_provider.is_verified = True
            db.session.commit()

            return {
                'message': 'ServiceProvider verification status updated successfully',
                'provider_name': provider_name,
                'is_verified': service_provider.is_verified
            }, 200
class Flagged(Resource):
    @auth_token_required
    @roles_required('admin')
    def put(self):
        data = request.get_json()
        user_id = data.get('user_id')
        is_flagged = data.get('is_flagged')

        if not user_id:
            return {'message': 'User ID is required'}, 400
        if is_flagged is None:
            return {'message': 'is_flagged status is required'}, 400

        # Query the User table by user_id
        user = User.query.filter_by(user_id=user_id).first()

        if not user:
            return {'message': f"User with ID '{user_id}' not found"}, 404

        # Check if the user is associated with a Consumer or ServiceProvider and update is_flagged
        consumer = Consumer.query.filter_by(user_id=user.user_id).first()
        service_provider = ServiceProvider.query.filter_by(user_id=user.user_id).first()

        if consumer:
            # Update consumer's flag status
            consumer.is_flagged = is_flagged
            db.session.commit()
            return {
                'message': 'Consumer flagged status updated successfully',
                'user_id': user_id,
                'is_flagged': consumer.is_flagged
            }, 200

        elif service_provider:
            # Update service provider's flag status
            service_provider.is_flagged = is_flagged
            db.session.commit()
            return {
                'message': 'ServiceProvider flagged status updated successfully',
                'user_id': user_id,
                'is_flagged': service_provider.is_flagged
            }, 200

        return {'message': f"User with ID '{user_id}' does not belong to Consumer or ServiceProvider tables"}, 404

class Category(Resource):
    # @auth_token_required
    # @roles_required('admin')
    def post(self):
        
        data = request.get_json()
        category_name = data.get('category_name')
        base_price = data.get('base_price')

        category = ServiceCategory(category_name=category_name, base_price=base_price)
        db.session.add(category)
        db.session.commit()
        return {'message': 'Category added successfully!'}
    

    @auth_token_required
    @roles_required('admin')
    def put(self):
        data = request.get_json()
        category_name = data.get('category_name')
        new_name = data.get('new_name')
        new_base_price = data.get('new_base_price')

        # Find the category by its current name
        category = ServiceCategory.query.filter_by(category_name=category_name).first()

        if not category:
            return {'message': f"Category '{category_name}' not found"}, 404

        # Update category attributes based on provided parameters
        if new_name:
            category.category_name = new_name
        if new_base_price is not None:  # Allow setting base price to 0 or other values
            category.base_price = new_base_price

        # Commit the changes to the database
        db.session.commit()

        updated_fields = {
            'category_name': category.category_name,
            'base_price': str(category.base_price)
        }

        return {
            'message': f"Category '{category_name}' updated successfully",
            'updated_fields': updated_fields
        }, 200
    
class DeleteCategory(Resource):
    # @auth_token_required
    # @roles_required('admin')
    def delete(self):
        data = request.get_json()
        category_name = data.get('category_name')

        # Find the category by its name
        category = ServiceCategory.query.filter_by(category_name=category_name).first()

        if not category:
            return {'message': f"Category '{category_name}' not found"}, 404

        # Get all providers associated with the category
        providers = category.service_providers

        # Delete associated service requests, providers, and their users
        for provider in providers:
            # Retrieve and delete all service requests for the provider
            service_requests = ServiceRequest.query.filter_by(provider_id=provider.provider_id).all()
            for service_request in service_requests:
                db.session.delete(service_request)  # Delete each ServiceRequest explicitly

            # Delete the associated user for the provider
            user = User.query.get(provider.user_id)
            if user:
                db.session.delete(user)  # Delete the User for the ServiceProvider

            db.session.delete(provider)  # Delete the ServiceProvider itself

        # Finally, delete the category
        db.session.delete(category)
        db.session.commit()

        return {'message': f"Category '{category_name}' and all related data deleted successfully"}, 200


from sqlalchemy import or_

class SearchAPI(Resource):
    @auth_token_required
    @roles_accepted('admin', 'consumer')
    def get(self):
        query = request.args.get('query', '').strip()
        if not query:
            return {"message": "Query parameter is required"}, 400

        # Determine user role
        user_roles = [role.name for role in current_user.roles]
        user_role = None
        if 'admin' in user_roles:
            user_role = 'admin'
        elif 'consumer' in user_roles:
            user_role = 'consumer'
        elif 'serviceprovider' in user_roles:
            user_role = 'serviceprovider'
        else:
            return {"message": "You do not have permission to perform this search"}, 403

        # Initialize result data
        result = {}

        # Search logic based on role
        if user_role == 'admin':
            # Admin can search across all entities
            result["categories"] = [
                {
                    "category_id": category.category_id,
                    "category_name": category.category_name,
                    "base_price": str(category.base_price),
                }
                for category in ServiceCategory.query.filter(
                    ServiceCategory.category_name.ilike(f"%{query}%")
                ).all()
            ]

            result["providers"] = [
                {
                    "provider_id": provider.provider_id,
                    "user_id": provider.user_id,
                    "name": provider.name,
                    "is_verified": provider.is_verified,
                    "price": str(provider.price),
                    "is_flagged": provider.is_flagged,
                }
                for provider in ServiceProvider.query.filter(
                    or_(
                        ServiceProvider.name.ilike(f"%{query}%"),
                        ServiceProvider.description.ilike(f"%{query}%"),
                    )
                ).all()
            ]

            result["consumers"] = [
                {
                    "consumer_id": consumer.consumer_id,
                    "user_id": consumer.user_id,
                    "name": consumer.name,
                    "is_flagged": consumer.is_flagged,
                }
                for consumer in Consumer.query.filter(
                    Consumer.name.ilike(f"%{query}%")
                ).all()
            ]

        elif user_role == 'consumer':
            # Consumers search for service providers matching the query
            providers_by_name = ServiceProvider.query.filter(
                or_(
                    ServiceProvider.name.ilike(f"%{query}%"),
                    ServiceProvider.description.ilike(f"%{query}%"),
                )
            ).all()

            # Providers belonging to categories matching the query
            matching_categories = ServiceCategory.query.filter(
                ServiceCategory.category_name.ilike(f"%{query}%")
            ).all()
            category_ids = [category.category_id for category in matching_categories]
            providers_by_category = ServiceProvider.query.filter(
                ServiceProvider.category_id.in_(category_ids)
            ).all()

            # Combine and remove duplicates
            providers = {
                provider.provider_id: provider
                for provider in providers_by_name + providers_by_category
            }.values()

            result = {
                "providers": [
                    {
                        "provider_id": provider.provider_id,
                        "name": provider.name,
                        "description": provider.description,
                        # Add other fields as needed
                    }
                    for provider in providers
                ],
                "can_create_request": True  # Option to create a new request
            }

        elif user_role == 'serviceprovider':
            # Providers cannot perform a search
            return {"message": "You do not have permission to perform this search"}, 403

        return jsonify(result)

    
# class ExportCsv(Resource):
#     @auth_token_required
#     @roles_required('admin')
#     def get(self):
        


# Resouce API for Login, Logout and Signup
api.add_resource(UserAuth, '/api/auth')
api.add_resource(LoadServiceCategory, '/api/load-category')
api.add_resource(UserLogin, '/api/login') 
api.add_resource(UpdateProfile, '/api/update-profile')
api.add_resource(Logout, '/api/logout')

# Resource API for Consumer
api.add_resource(CreateServiceRequest, '/api/create-request')
api.add_resource(ConsumerUpdateRequestStatus, '/api/consumer/<int:request_id>/update-request')
api.add_resource(ConsumerRequestDetails, '/api/consumer/<int:request_id>/details')
api.add_resource(ConsumerInfo, '/api/consumer/info')
api.add_resource(ShowCurrentRequest, '/api/consumer/show-current-request')
api.add_resource(ConsumerCloseRequest, '/api/consumer/<int:request_id>/close-request')
api.add_resource(ShowServices, '/api/consumer/show-services')

# Resource API for ServiceProvider
api.add_resource(ShowProviderRequests, '/api/provider/requests')
api.add_resource(AcceptRequest, '/api/provider/<int:request_id>/accept-request')
api.add_resource(DeclineRequest, '/api/provider/<int:request_id>/decline-request')
api.add_resource(ProviderCloseRequest, '/api/provider/<int:request_id>/close-request')
api.add_resource(ProviderInfo, '/api/provider/info')

# Resource API for Admin
api.add_resource(AdminInfo, '/api/admin/info')
api.add_resource(AdminDashboard, '/api/admin/dashboard-data')
api.add_resource(Verification, '/api/verification')  # Protected route
api.add_resource(Flagged, '/api/flagged')
api.add_resource(Category, '/api/category')
api.add_resource(DeleteCategory, '/api/category/delete')

api.add_resource(SearchAPI, '/api/search')


# from task import export_closed_requests
# class ExportClosedRequestsAPI(Resource):
#     @auth_token_required
#     @roles_required('admin')
#     def post(self):
#         """
#         API to trigger the export of closed service requests for a professional.
#         """
#         parser = reqparse.RequestParser()
#         parser.add_argument('professional_id', type=int, required=True, help="Professional ID is required")
#         parser.add_argument('email', type=str, required=True, help="Email address is required")
#         args = parser.parse_args()

#         professional_id = args['professional_id']
#         email = args['email']

#         # Trigger the Celery task
#         task = export_closed_requests.delay(professional_id, email)

#         return {
#             "message": "Export job has been triggered",
#             "task_id": task.id
#         }, 202

    
from flask import make_response
import csv
import io

class ExportClosedRequestsAPI(Resource):
    def post(self):
        # Query closed service requests from the database
        closed_requests = ServiceRequest.query.filter_by(is_closed=True).all()

        # Check if there are any closed requests
        if not closed_requests:
            return {"message": "No closed service requests found."}, 404

        # Prepare the CSV data
        csv_output = io.StringIO()
        writer = csv.writer(csv_output)
        writer.writerow(["Service ID", "Customer ID", "Professional ID", "Date of Request", "Location"])

        for request in closed_requests:
            writer.writerow([
                request.request_id,
                request.consumer_id,
                request.provider_id,
                request.request_date.strftime('%Y-%m-%d %H:%M:%S') if request.request_date else "N/A",
                request.location or "N/A"
            ])

        csv_output.seek(0)

        # Create a response with the CSV file
        response = make_response(csv_output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=closed_requests.csv'
        response.headers['Content-Type'] = 'text/csv'

        return response
api.add_resource(ExportClosedRequestsAPI, '/export-closed-requests')