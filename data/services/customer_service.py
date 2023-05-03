from typing import List, Dict

from rest_framework.generics import get_object_or_404

from data.models import CustomerKeys
from data.services.sfkb_mock import SFKBMock
from data.tasks import save_to_cloud
from data.services.google_docs_client_mock import GoogleDocsClientMock


class CustomerService:
    def __init__(self, customer_id: int):
        self.customer_id = customer_id

    def get_and_index_customer_files(self) -> List[Dict]:
        """
        Gets and indexes all files for a customer from all sources
        :return: Dict with source and count of files
        """
        customer = get_object_or_404(CustomerKeys, pk=self.customer_id)
        output_data = []
        if customer.google_docs is not None:
            try:
                files = GoogleDocsClientMock(customer=customer.customer_name,
                                             secret=customer.google_docs).get_docs_call()
                save_to_cloud.delay(source='google_docs', items=files)
                output_data.append({
                    'source': 'google_docs',
                    'count': len(files)
                })

            except ValueError:
                pass
        if customer.sfkb_user_name is not None and customer.sfkb_password is not None:
            try:
                token = SFKBMock().authenticate(customer=customer.customer_name, username=customer.sfkb_user_name,
                                                password=customer.sfkb_password)
                docs_ids = SFKBMock().get_doc_ids(token.token)
                save_to_cloud.delay(source='sfkb', items=list(docs_ids), token=token.token)
                output_data.append({
                    'source': 'sfkb',
                    'count': len(docs_ids)
                })
            except ValueError:
                pass
        return output_data
