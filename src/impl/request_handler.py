import logging
logger = logging.getLogger(__name__)

from typing import Optional
import os
import sys
from pathlib import Path
from collections import OrderedDict


script_dir = os.path.dirname(__file__)
sys.path.append(script_dir)  # Appe

# sys.path.append(str(Path(__file__).resolve().parent.parent / "llmec"))

# print("syspath>", sys.path)


# from celery_app import async_text_to_image_service
# from models.bug_report_request import BugReportRequest

# from models.operation_status import OperationStatus


class RequestHandler:
    #def __init__(self, iie,ch, et=False):
    def __init__(self, app):
        self.app = app
        self.package_content = None
        self.requester_id = None
        self.package_sent_time = None
        self.response = None

        self.DATA_IS_VALID = None
        self.META_IS_VALID = None
        self.USER_HAS_PERMISSION = None

        self.REQUEST_IS_VALID=None
        self.error_code=None

        logger.debug("Request Handler ")
        self.logger= logger

        #self.elapsed_time =et
        self.elapsed_time=None
        if not self.elapsed_time:

            self.elapsed_time= OrderedDict()

    def op_validity(self,meta_data):

        is_permitted=self.check_metadata_validity(meta_data)
        if is_permitted:
            return True
        else:
           # raise HTTPException(status_code=400, detail="user doesnt have permission for this operation")
            return False

    def check_metadata_validity(self, meta_data):
        return True


    def handle_submit_order(self, request):

        # class MyRequest:
        #     def __init__(self):
        #         self.country = country
        #         self.supported = supported

        # mr = MyRequest()

        from impl.services.order.submit_order_service import SubmitOrderService
        dependency = self.app.state.services

        p = SubmitOrderService(request, dependencies=dependency)
        return p.response




