from typing import List

from data.services.sfkb_mock import SFKBMock
from data.utils import save_file_to_cloud_mock
from djangoProject.celery import app
from data.models import CustomerKeys


@app.task()
def save_to_cloud(source: str, items: List, token: str = None) -> None:
    """
    Saves the given items to the cloud storage
    :param token: optional token from sfkb
    :param source: the source of the items
    :param items: the items to save
    """
    if source == "google_docs":
        for item in items:
            save_file_to_cloud_mock(item.get("URL"), item.get("HTML"))
    elif source == "sfkb":
        for item in items:
            document = SFKBMock().get_doc(token=token, doc_id=item)
            save_file_to_cloud_mock(document.get("URL"), document.get("HTML"))


@app.task()
def index_customers():
    from data.services.customer_service import CustomerService
    """
    Indexes all customers
    """
    customers = CustomerKeys.objects.all().values_list('id', flat=True)
    for customer in customers:
        CustomerService(customer_id=customer).get_and_index_customer_files()
