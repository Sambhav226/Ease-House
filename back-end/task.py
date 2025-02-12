from worker import celery
from celery import shared_task
from jinja2 import Template
from mela import send_email
import csv
from models import ServiceProvider, ServiceRequest, Consumer, User
import traceback


@celery.task()
def daily_reminder():
    """
    Sends daily reminders to service professionals via email, reminding them of pending service requests.
    """
    try:
        # Fetch all service providers
        providers = ServiceProvider.query.all()
        print(providers)

        for provider in providers:
            # Check for pending service requests
            pending_requests = ServiceRequest.query.filter_by(
                provider_id=provider.provider_id,
                is_accepted='pending',
                is_closed=False
            ).all()

            if not pending_requests:
                print(f"No pending requests found for provider {provider.name} (ID: {provider.provider_id})")
                continue

            print(f"Found {len(pending_requests)} pending requests for provider {provider.name} (ID: {provider.provider_id})")

            # Prepare email content
            with open('./templates/daily_reminder.html', 'r') as file:
                template = Template(file.read())

            # Render template with provider and pending requests data
            email_content = template.render(
                provider_name=provider.name,
                pending_requests=[
                    {
                        "consumer": request.consumer.name if request.consumer else "Unknown",
                        "location": request.location or "Not specified",
                        "request_date": request.request_date.strftime("%Y-%m-%d") if request.request_date else "Unknown",
                    }
                    for request in pending_requests
                ]
            )

            # Send email to the provider
            # user = User.query.filter_by(user_id=provider.user_id).first()
            send_email(
                to_address="test@gmail.com",#user.email,
                subject="Daily Reminder: Pending Service Requests",
                message=email_content,
                content="html"
            )
        return "Daily reminders sent successfully"

    except Exception as e:
        print(f"Error in daily_reminder task: {str(e)}")
        # print(traceback.format_exc())
        return "Error in sending daily reminders"

@celery.task()
def monthly_reminder():
    """
    Sends a monthly activity report to customers via email, summarizing their service details.
    """
    try:
        # Fetch all consumers
        consumers = Consumer.query.all()

        for consumer in consumers:
            # Fetch service requests for this consumer
            service_requests = ServiceRequest.query.filter_by(consumer_id=consumer.consumer_id).all()

            # Summarize service details
            total_requests = len(service_requests)
            closed_requests = sum(1 for req in service_requests if req.is_closed)
            pending_requests = sum(1 for req in service_requests if  req.is_accepted == 'pending')

            # Prepare email content
            with open('./templates/monthly_report_consumer.html', 'r') as file:
                template = Template(file.read())

            # Render template with service data
            email_content = template.render(
                consumer_name=consumer.name,
                total_requests=total_requests,
                closed_requests=closed_requests,
                pending_requests=pending_requests,
                service_requests=[
                    {
                        "provider": req.provider.name,
                        "location": req.location or "Not specified",
                        "request_date": req.request_date.strftime("%Y-%m-%d") if req.request_date else "Unknown",
                        "status": "Closed" if req.is_closed else ("Pending" if req.is_accepted == 'pending' else "Accepted")
                    }
                    for req in service_requests
                ]
            )

            # Send email to the consumer
            send_email(
                to_address="test@gmail.com",
                subject="Monthly Activity Report",
                message=email_content,
                content="html"
            )

        return "Monthly reports sent successfully"

    except Exception as e:
        print(f"Error in monthly_customer_report task: {str(e)}")
        print(traceback.format_exc())
        return "Error in sending monthly reports"


@shared_task()
def export_closed_requests(professional_id, email):
    """
    Celery task to export closed service requests for a given professional to a CSV file.
    """
    try:
        # Fetch closed service requests for the professional
        closed_requests = ServiceRequest.query.filter_by(
            provider_id=professional_id, is_closed=True
        ).all()

        if not closed_requests:
            return f"No closed service requests found for professional ID {professional_id}"

        # Prepare CSV file
        file_path = f"./static/closed_requests_{professional_id}.csv"
        with open(file_path, mode='w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                "Request ID", "Customer ID", "Professional ID", 
                "Date of Request", "Completion Date", "Remarks"
            ])
            writer.writeheader()

            for request in closed_requests:
                writer.writerow({
                    "Request ID": request.request_id,
                    "Customer ID": request.consumer_id,
                    "Professional ID": request.provider_id,
                    "Date of Request": request.request_date.strftime("%Y-%m-%d"),
                    "Completion Date": request.completion_date.strftime("%Y-%m-%d") if request.completion_date else "N/A",
                    "Remarks": "Completed successfully"  # Add custom remarks here
                })

        # Notify via email
        email_content = f"Your export job for closed service requests has completed. The file is attached."
        send_email(
            to_address=email,
            subject="Closed Service Requests Export",
            message=email_content,
            content="plain",
            attachment=file_path
        )

        return f"Export completed. File saved at {file_path}"

    except Exception as e:
        return f"Error during export: {str(e)}"